#!/usr/bin/env python3

"""

Work Log Databse Script

A simple work log script using a SQL db to implement its data model

Began on: 7 September 2016

by Miguel de Luis



"""

from collections import OrderedDict
from datetime import date
from sys import stdin, exit

from peewee import *
from blessings import Terminal

DATE_FORMAT = "%d/%m/%Y"
STANDARD_FIELD_LENGTH = 255

db = SqliteDatabase("work_log.db")

term = Terminal()


class Task(Model):
    task_00_project = CharField(max_length=STANDARD_FIELD_LENGTH, default="In Box")
    task_1_user_name = CharField(max_length=STANDARD_FIELD_LENGTH)
    task_0_name = CharField(max_length=STANDARD_FIELD_LENGTH)
    task_3_duration = IntegerField(help_text="Time spent on the task, in minutes")
    task_2_date = DateField(default=date.today)  # research Date Formats
    task_4_notes = TextField()

    
    class Meta:
        database = db


def show_validation(x):
    if x:
        print(x)


def get_task_date(prompt, validation_message=""):
    """
    Ask user for task date, validates,
    :return: string ... dd/mm/yyyy
    """

    show_validation(validation_message)

    raw_task_date = input("Please enter the date for this task. Enter help for help:> ") \
        .replace(" ", "").replace(".", "/").replace("-", "/").strip("").lower()
    # some countries use . for the / https://en.wikipedia.org/wiki/Date_format_by_country

    if raw_task_date == "help":
        help_message = """
    Enter dates as dd/mm/yyyy.
    ==========================

    * If you want to use the alternative format of mm/dd/yyyy write the letter M before your date as in M12/23/2016.

    * If you want to use the alternative format of yyyy/mm/dd write the letter Y before the date as in Y2016/12/23.

    * You may also substitute / for . or - with or without spaces
    """
        return get_task_date(prompt, validation_message=help_message)

    if raw_task_date:
        try:
            if raw_task_date[0] == "m":
                month, day, year = tuple(map(int, raw_task_date[1:].split("/")))
            elif raw_task_date[0] == "y":
                year, month, day = tuple(map(int, raw_task_date[1:].split("/")))
            else:
                day, month, year = tuple(map(int, raw_task_date.split("/")))


            print(day, month, year)
            return date(year, month, day)
        except ValueError:
            return get_task_date(prompt,
                                 validation_message=
                                 "Please enter the date in a know format or just press enter for today, help for help"
                                 )
    else:
        return date.today()


def gatehouse(prompt, is_time=False, validation_message ="", are_they_notes=False, is_date=False):
    """

    :param prompt:
    :param is_time:
    :return:
    """
    if validation_message:
        print(validation_message)
    if are_they_notes:
        print(prompt)
        return stdin.read()

    if is_time:
        raw_data = input(prompt).strip()
        raw_data.strip("-")  # Negative time spent doesn't make any sense unless you are the Doctor
        try:
            return int(raw_data)
        except ValueError:
            if ":" in raw_data:
                try:
                    hours, minutes = tuple(map(int, raw_data.split(":")))
                    if minutes > 59:
                        return gatehouse(prompt, is_time=True,
                                         validation_message="If entering time using the hours:minutes format, minutes"
                                                            "shouldn't be higher than 59.")
                    else:
                        return hours * 60 + minutes
                except ValueError:
                    return gatehouse(prompt, is_time=True,
                                     validation_message="Enter time in minutes or as hours:minutes")
            else:
                return gatehouse(prompt, is_time=True,
                                 validation_message="Enter time in minutes or as ours:minutes")
    elif is_date:
        return get_task_date(prompt)
    else:
        raw_data = input(prompt).strip()
        return raw_data[0:STANDARD_FIELD_LENGTH]  # Avoids adding a Field size larger than the Standard Field Length


def input_task_data():
    ugly_prompts = ["Your name:\t", "Your task name:\t",
                    'Time spent on the task:\t', "Notes, ctrl+d to finish.",
                    "Project:\t", "Date Enter the date when the task was completed or hit enter for today:\t"]

    pretty_prompts = list(map((lambda x: term.bold(x)), ugly_prompts))

    project = gatehouse(pretty_prompts[4])
    name_of_user = gatehouse(pretty_prompts[0])
    name_of_task = gatehouse(pretty_prompts[1])
    date = gatehouse(pretty_prompts[5], is_date=True)
    duration_of_task = gatehouse(pretty_prompts[2], is_time=True)
    notes = gatehouse(pretty_prompts[3], are_they_notes=True)

    return project, name_of_user, name_of_task, duration_of_task, notes, date


def add_task():
    """

    """
    project, name_of_user, name_of_task, duration_of_task, notes, date = input_task_data()

    Task.create(task_00_project=project, task_1_user_name=name_of_user, task_0_name=name_of_task,
                task_3_duration=duration_of_task, task_4_notes=notes, task_2_date = date)


def initialize():
    db.connect()
    db.create_tables([Task], safe=True)


def view_entries(tasks,
                 fields_to_hide=set([]), title="Tasks"):
    """

    :return:
    """
    fields = set(["task_00_project", "task_0_name", "task_1_user_name",
                  "task_2_date", "task_4_notes", "task_3_duration"])
    fields_to_show = sorted(list(fields - fields_to_hide))

    number_of_tasks = len(tasks)

    def next_task(ti):
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
        project, name_of_user, name_of_task, duration_of_task, notes, date = input_task_data()

        tasks[ti].task_00_project = project
        tasks[ti].task_1_user_name = name_of_user
        tasks[ti].task_0_name = name_of_task
        tasks[ti].task_3_duration = duration_of_task
        tasks[ti].task_4_notes = notes
        tasks[ti].task_2_date = date

        user_confirm = input("Confirm edit y/N").strip().lower()
        if user_confirm == "y":
            tasks[ti].save()
            print("Task edited")
        else:
            print("Nothing changed")
        return ti

    def delete_task(ti):
        user_confirms = input("Please confirm you want to delete this task y/N").strip().lower()
        if user_confirms == "y":
            tasks[ti].delete_instance()
            print("Task {} deleted".format(tasks[ti].task_0_name))
            return -1
        else:
            return ti

    choices = {"n": next_task, "p": previous_task, "x": exit_view, "d": delete_task, "e":edit_task}

    def show_menu(ti=0):

        show_task(task=tasks[ti], total_tasks=number_of_tasks, task_number=ti+1)

        choice = choices[input_choice()]

        ti = choice(ti)

        if ti < 0:
            return None
        else:
            return show_menu(ti)

    def show_task(task, total_tasks, task_number):
        print_tags = dict(task_00_project="Project", task_0_name="Description",
                          task_1_user_name="User", task_2_date="Date",
                          task_3_duration="Minutes spent on task", task_4_notes="Notes:\n")

        print(term.clear)
        print(term.bold_underline(title))

        print("Task {} of {}\n".format(task_number, total_tasks))
        for fts in fields_to_show:
            field = task.__dict__['_data'][fts]
            if fts == "task_2_date":
                field = field.strftime(DATE_FORMAT)
            if field:
                print("{}: {}".format(term.bold(print_tags[fts]), field))
        print()

    show_menu()


def show_dates_with_tasks():
    tasks = Task.select().order_by(Task.task_2_date)

    if tasks:
        def pretty_dates(x):
            return x.task_2_date.strftime(DATE_FORMAT)

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

    def safe_date_choice_input(validation_message=""):
        if validation_message:
            print(term.bold_underline(validation_message))

        raw_input = input("\nEnter date to look for: ")
        try:
            date_entered = list_of_dates[int(raw_input) - 1]
            day, month, year = date_entered.split("/")
            return date(int(year), int(month), int(day))
        except IndexError:
            return safe_date_choice_input(validation_message="That number does not correspond to any date.")
        except ValueError:
            return safe_date_choice_input(validation_message="Choose any of the dates using its ordinal number.")

    list_of_dates = show_dates_with_tasks()

    if list_of_dates:

        date_to_search = safe_date_choice_input()

        tasks = Task.select().where(Task.task_2_date == date_to_search)

        view_entries(tasks,
                     title="Tasks completed on {}".format(date_to_search.strftime(DATE_FORMAT)),
                     fields_to_hide={"task_2_date"})

    else:
        print("Database empty")


def search_entries_by_employee():
    employee = input("Employee name:").strip()

    tasks = Task.select().where(Task.task_1_user_name == employee)
    if tasks:
        view_entries(tasks,
                     title="Tasks completed by {}".format(employee),
                     fields_to_hide={"task_1_user_name"})
    else:
        print("No tasks by employee: {}".format(employee))


def find_by_search_term():
    search_term = input("Term to search:").strip()

    tasks = Task.select().where(
        (Task.task_0_name.contains(search_term)) |
        (Task.task_4_notes.contains(search_term))
    )
    if tasks:
        view_entries(tasks,
                     title="Tasks that contain \"{}\"".format(search_term))
    else:
        print("No task meets the search term \"{}\"".format(search_term))


def search_by_project():
    project_to_search = input("Project to search for:").strip()

    tasks = Task.select().where(
        Task.task_00_project == project_to_search
    )

    if tasks:
        view_entries(tasks,
                     title="Tasks that belong to \"{}\"".format(project_to_search))
    else:
        print("No task in the project: \"{}\"".format(project_to_search))


def search_entries():

    search_menu = OrderedDict([
        ("e", [search_entries_by_employee, "search entries by employee"]),
        ("f", [find_by_search_term, "find by search term"]),
        ("d", [search_entries_by_date, "find by date"]),
        ("p", [search_by_project, "find by project"])
    ])

    print(term.clear)
    for key, value in search_menu.items():
        print("{} {} {} {}".format(term.bold, key, term.normal, value[1].title()))
    choice = input().strip().lower()
    if choice in search_menu.keys():
        search_menu[choice][0]()
    else:
        return search_entries()  # let's make a generic menu function instead


def show_help():
    print(term.clear)
    print("When prompted for the menu, input a to add a task, v to view entries, q to quit, h for this help")
    print("When adding the time spent on a task enter the time in minutes or in the hh:ss format ")


def view_all_entries():
    tasks_to_view = Task.select().order_by(Task.task_2_date.desc())
    if tasks_to_view:
        view_entries(tasks=tasks_to_view)
    else:
        print("No tasks to show")

main_menu = OrderedDict([
    ('a', [add_task, "add task"]),
    ('v', [view_all_entries, "view entries"]),
    ('s', [search_entries, "search entries"]),
    ('q', [exit, "quit script"]),
    ('h', [show_help, "show help"])
])


def menu_loop(menu):
    print(term.clear)
    while True:
        for key, value in menu.items():
            print("{} {} {} {}".format(term.bold, key, term.normal, value[1].title()))

        choice = input("Choice: ").strip()

        if choice in menu:
            menu[choice][0]()


def main():
    initialize()

    menu_loop(main_menu)


if __name__ == '__main__':
    main()
else:
    pass
