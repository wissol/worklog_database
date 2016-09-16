#!/usr/bin/env python3

"""

Work Log Databse Script

A simple work log script using a SQL db to implement its data model

Began on: 7 September 2016

by Miguel de Luis



"""

from collections import OrderedDict
import datetime
from sys import stdin, exit

from peewee import *
from blessings import Terminal

DATE_FORMAT = "%d/%m/%Y"

db = SqliteDatabase("work_log.db")

term = Terminal()


class Task(Model):
    user_name = CharField(max_length=255)
    task_name = CharField(max_length=255)
    task_duration = IntegerField(help_text="Time spent on the task, in minutes")
    task_date = DateTimeField(default=datetime.date.today)  # research Date Formats
    task_notes = TextField()
    
    class Meta:
        database = db


def barbican(prompt, is_time=False, validation_message = ""):
    """
    Barbican, being the gatehouse of a castle
    :param prompt:
    :param is_time:
    :return:
    """
    if validation_message:
        print(validation_message)
    try:
        x = input(prompt).strip()
    except KeyboardInterrupt:
        is_it_goodbye = input("Quit program? y/N")
        if is_it_goodbye == "y":
            exit()
        else:
            return barbican(prompt, is_time, validation_message="")
    if is_time:
        x.strip("-")  # Negative time spent doesn't make any sense unless you are the Doctor
        try:
            return int(x)
        except ValueError:
            if ":" in x:
                try:
                    hours, minutes = tuple(map(int, x.split(":")))
                    if minutes > 59:
                        return barbican(prompt, is_time=True,
                                        validation_message="If entering time using the hours:minutes format, minutes"
                                                           "shouldn't be higher than 59.")
                    else:
                        return hours * 60 + minutes
                except ValueError:
                    return barbican(prompt, is_time=True, validation_message="Enter time in minutes or as hours:minutes")
            else:
                return barbican(prompt, is_time=True, validation_message="Enter time in minutes or as ours:minutes")
    else:
        return x[0:255]


def input_task_data():
    ugly_prompts = ["Your name:\t", "Your task name:\t", 'Time spent on the task:\t', "Notes, ctrl+d to finish."]

    def give_format(x):
        return term.bold(x)

    pretty_prompts = list(map(give_format, ugly_prompts))

    name_of_user = barbican(pretty_prompts[0])
    name_of_task = barbican(pretty_prompts[1])
    duration_of_task = barbican(pretty_prompts[2], is_time=True)

    print(pretty_prompts[3])
    notes = stdin.read()

    return name_of_user, name_of_task, duration_of_task, notes


def add_task():
    """

    """
    name_of_user, name_of_task, duration_of_task, notes = input_task_data()

    Task.create(user_name=name_of_user, task_name=name_of_task,
                task_duration=duration_of_task, task_notes=notes)


def initialize():
    db.connect()
    db.create_tables([Task], safe=True)


def show_task(task, fields_to_show, total_tasks, task_number):
    print_tags = dict(task_name="Description", user_name="User", task_date="Date:",
                      task_duration="Minutes spent on task", task_notes="Notes:\n")

    print("Task {} of {}\n".format(task_number, total_tasks))
    for fts in fields_to_show:
        field = task.__dict__['_data'][fts]
        if fts == "task_date":
            field = field.strftime(DATE_FORMAT)
        if field:
            print("{} : {}".format(print_tags[fts], field))
    print()


def view_entries(tasks,
                 fields_to_hide=set([]), title="Tasks"):
    """

    :return:
    """
    fields = set(["task_name", "user_name", "task_date", "task_notes", "task_duration"])
    fields_to_show = fields - fields_to_hide

    number_of_tasks = len(tasks)

    print(term.clear)
    print(term.bold_underline(title))

    def next_task(ti):
        print("len",len(tasks))
        if ti < len(tasks) - 1:
            return ti + 1
        else:
            print("\a No more tasks to show")
            return ti

    def previous_task(ti):
        if ti == 0:
            print("\a This is the first task")
            return ti
        else:
            return ti - 1

    def exit_view(ti):
        ti = -1 + ti*0
        return ti

    def input_choice(message="(p)revious\t(n)ext\te(x)it"):
        print(message)
        choice = input().lower().strip()

        if choice in choices.keys():
            return choice
        else:
            return input_choice(message="Valid choices: p,n,x")

    def edit_task(ti):
        name_of_user, name_of_task, duration_of_task, notes = input_task_data()

        tasks[ti].user_name = name_of_user
        tasks[ti].task_name = name_of_task
        tasks[ti].task_duration = duration_of_task
        tasks[ti].task_notes = notes

        user_confirm = input("Confirm edit y/N").strip().lower()
        if user_confirm == "y":
            tasks[ti].save()
            print("Task edited")
            return -1
        else:
            print("Nothing changed")
            return ti

    def delete_task(ti):
        user_confirms = input("Please confirm you want to delete this task y/N").strip().lower()
        if user_confirms == "y":
            tasks[ti].delete_instance()
            print("Task {} deleted".format(tasks[ti].task_name))
            return -1
        else:
            return ti

    choices = {"n": next_task, "p": previous_task, "x": exit_view, "d": delete_task, "e":edit_task}

    def show_menu(ti=0):

        show_task(tasks[ti], fields_to_show, task_number=ti+1, total_tasks=number_of_tasks)

        choice = choices[input_choice()]

        ti = choice(ti)

        if ti < 0:
            return None
        else:
            print("no",ti)
            return show_menu(ti)

    show_menu()


def show_dates_with_tasks():
    tasks = Task.select()

    if tasks:
        def pretty_dates(x):
            return x.task_date.strftime(DATE_FORMAT)

        all_dates = list(map(pretty_dates, tasks))
        list_of_dates = []
        tasks_in_dates = {}

        for date_item in all_dates:
            if date_item not in list_of_dates:
                list_of_dates.append(date_item)
                tasks_in_dates[date_item] = 1
            else:
                tasks_in_dates[date_item] += 1

        print(term.clear)
        print(term.bold("\n\tDates with Task --- Number of Dates\n"))
        i = 1
        for date_item in list_of_dates:
            print("\t{}.- {}\t--- {}".format(term.bold(str(i)), date_item, tasks_in_dates[date_item]))
            i += 1
        return list_of_dates
    else:
        return None


def search_entries_by_date():
    list_of_dates = show_dates_with_tasks()

    if list_of_dates:

        def safe_date_choice_input(validation_message=""):
            if validation_message:
                print(term.bold_underline(validation_message))

            raw_input = input("\nEnter date to look for: ")
            try:
                date_entered = list_of_dates[int(raw_input) - 1]
                day, month, year = date_entered.split("/")
                return datetime.date(int(year), int(month), int(day))
            except IndexError:
                return safe_date_choice_input(validation_message="That number does not correspond to any date.")
            except ValueError:
                return safe_date_choice_input(validation_message="Choose any of the dates using its ordinal number.")

        date_to_search = safe_date_choice_input()

        tasks = Task.select().where(Task.task_date == date_to_search)

        view_entries(tasks,
                     title="Tasks completed on {}".format(date_to_search.strftime(DATE_FORMAT)),
                     fields_to_hide={"task_date"})

    else:
        print("Database empty")


def search_entries():
    search_entries_by_date()


def show_help():
    print(term.clear)
    print("When prompted for the menu, input a to add a task, v to view entries, q to quit, h for this help")
    print("When adding the time spent on a task enter the time in minutes or in the hh:ss format ")


def view_all_entries():
    tasks_to_view = Task.select().order_by(Task.task_date.desc())
    if tasks_to_view:
        view_entries(tasks=tasks_to_view)
    else:
        print("No tasks to show")

menu = OrderedDict([
    ('a', [add_task, "add task"]),
    ('v', [view_all_entries, "view entries"]),
    ('s', [search_entries, "search entries"]),
    ('q', [exit, "quit script"]),
    ('h', [show_help, "show help"])
])


def menu_loop():
    print(term.clear)
    while True:
        for key, value in menu.items():
            print("{} {} {} {}".format(term.bold, key, term.normal, value[1].title()))

        choice = input("Choice: ").strip()

        if choice in menu:
            menu[choice][0]()


def main():
    initialize()
    menu_loop()


if __name__ == '__main__':
    main()
else:
    pass
