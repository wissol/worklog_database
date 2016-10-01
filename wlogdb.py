#!/usr/bin/env python3

"""

Work Log Database Script

A simple work log script using a SQL db to implement its data model

Began on: 7 September 2016

by Miguel de Luis



"""

# imports

from collections import OrderedDict
from datetime import date
from sys import stdin, exit
import logging

from blessings import Terminal
from peewee import *

# constants

DATE_FORMAT = "%d/%m/%Y"
STANDARD_FIELD_LENGTH = 255

# Global

db = SqliteDatabase("work_log.db")

term = Terminal()

logging.basicConfig(filename='log.log', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')


class Task(Model):
    task_00_project = CharField(max_length=STANDARD_FIELD_LENGTH, default="In Box")
    task_1_user_name = CharField(max_length=STANDARD_FIELD_LENGTH)
    task_0_name = CharField(max_length=STANDARD_FIELD_LENGTH)
    task_3_duration = IntegerField(help_text="Time spent on the task, in minutes")
    task_2_date = DateField(default=date.today)
    task_4_notes = TextField()

    class Meta:
        database = db


def show_help_message(message: str) -> int:
    """
    Print x if there's an x to print
    :param message: string
    :return: None
    """
    if message:
        print(term.bold("\a" + message))
        return 1
    else:
        return 0


def input_task_date(prompt: str, help_message: str = "") -> date:
    """
    Manages the user input of task dates, allows various formats, defaults to date.today()
    :param prompt: string, a prompt for the user
    :param help_message: a help message to display on request or when data does not validate
    :return: Date (not DateTime!)
    """
    show_help_message(help_message)
    x = input(prompt)
    return cook_raw_date(prompt, x)


def cook_raw_date(prompt: str, raw_task_date: str) -> date:
    """
    Transform the string into a date
    :param raw_task_date:
    :param prompt:
    :return: Date
    """
    raw_task_date = raw_task_date.replace(" ", "").replace(".", "/").replace("-", "/").strip("").lower()
    # some countries use . for the / https://en.wikipedia.org/wiki/Date_format_by_country
    if raw_task_date == "help":
        logging.info("help shown")
        help_message = """
    Enter dates as dd/mm/yyyy.
    ==========================

    * If you want to use the alternative format of mm/dd/yyyy write the letter M before your date as in M12/23/2016.

    * If you want to use the alternative format of yyyy/mm/dd write the letter Y before the date as in Y2016/12/23.

    * You may also substitute / for . or - with or without spaces
    """
        return input_task_date(prompt, help_message=help_message)

    elif raw_task_date:
        try:
            if raw_task_date[0] == "m":
                month, day, year = tuple(map(int, raw_task_date[1:].split("/")))
            elif raw_task_date[0] == "y":
                year, month, day = tuple(map(int, raw_task_date[1:].split("/")))
            else:
                day, month, year = tuple(map(int, raw_task_date.split("/")))

            return date(year, month, day)
        except ValueError:
            logging.info("Invalid raw date string caught")
            return input_task_date(prompt,
                                   help_message=
                                   "Enter the date in an accepted format or just press enter for today, help for help"
                                   )
    else:
        return date.today()


def process_raw_time(prompt, raw_time):
    """
    process the raw time spent string into an int with the minutes spent on a task
    :param prompt: str
    :param raw_time: str
    :return:
    """
    try:
        return int(raw_time)
    except ValueError:
        if ":" in raw_time:
            try:
                hours, minutes = tuple(map(int, raw_time.split(":")))
                if minutes > 59:
                    return input_time_spent_on_task(
                        prompt,
                        help_message="If entering time using the hours:minutes format, minutes"
                                     "shouldn't be any higher than 59."
                    )
                else:
                    return hours * 60 + minutes
            except ValueError:
                logging.info("Invalid raw time string caught")
                return input_time_spent_on_task(
                    prompt,
                    help_message="Enter time in minutes or as hours:minutes"
                )
        else:
            logging.info("Unrecognised time spent format")
            return input_time_spent_on_task(
                prompt,
                help_message="Enter time in minutes or as hours:minutes"
            )


def input_time_spent_on_task(prompt, help_message=""):
    """
    Handle time spent on task input
    :param prompt: string
    :param help_message: string
    :return: int
    """
    show_help_message(help_message)
    raw_data = input(prompt).strip()
    raw_data.strip("-")  # Negative time spent doesn't make any sense unless you are the Doctor
    return process_raw_time(prompt, raw_time=raw_data)


def input_task_notes(prompt: str) -> str:
    """
    Handles task notes input
    :rtype: str
    :prompt: str
    """
    print(prompt)
    return stdin.read()


def input_standard_data(prompt, help_message="", field_length=STANDARD_FIELD_LENGTH):
    """
    Handles user data entry for miscellaneous data fields
    :param prompt: string
    :param help_message: string
    :param field_length: int
    :return: string
    """

    show_help_message(help_message)
    raw_data = input(prompt).strip()
    return raw_data[0:field_length]  # Avoids adding a Field size larger than the Standard Field Length


def input_task_data():
    """
    Bundles task data entry and edition
    :return: tuple, with the Task fields
    """
    ugly_prompts = ["Your name:\t", "Your task name:\t",
                    'Time spent on the task:\t', "Notes, ctrl+d to finish.",
                    "Project:\t",
                    "Date Enter the date when the task was completed or hit enter for today, help for help:\t"]

    pretty_prompts = list(map((lambda x: term.bold(x)), ugly_prompts))

    project = input_standard_data(pretty_prompts[4])
    name_of_user = input_standard_data(pretty_prompts[0])
    name_of_task = input_standard_data(pretty_prompts[1])
    date_entered = input_task_date(pretty_prompts[5])
    duration_of_task = input_time_spent_on_task(pretty_prompts[2])
    notes = input_task_notes(pretty_prompts[3])

    return project, name_of_user, name_of_task, duration_of_task, notes, date_entered


def add_task():
    """
    Creates a new task, based on user input
    :return: None
    """
    project, name_of_user, name_of_task, duration_of_task, notes, date_entered = input_task_data()

    Task.create(task_00_project=project, task_1_user_name=name_of_user, task_0_name=name_of_task,
                task_3_duration=duration_of_task, task_4_notes=notes, task_2_date=date_entered)


def initialize():
    """
    :return: None
    """
    db.connect()
    db.create_tables([Task], safe=True)


def next_task(ti, tasks):
    """
    Returns index of the next task to show
    :param ti: int task index
    :return: int
    """
    if ti < len(tasks) - 1:
        return ti + 1
    else:
        print("\a No more tasks to show")
        return ti


def previous_task(ti, tasks):
    """
    Returns index of the previous task to show
    tasks not used, but decided to keep it, not to complicate show_task_and_menu function
    :param ti: int task index
    :return: int
    """
    if ti == 0:
        print("\a This is the first task")
        return ti
    else:
        return ti - 1


def exit_view(ti, tasks):
    """
    ti and tasks not used, but decided to keep it, not to complicate show_task_and_menu function
    :param ti: int
    :return:
    """
    return -1


def edit_task(ti, tasks):
    """
    Handles task edition
    :param ti: int
    :param tasks: [Task]
    :return:
    """
    project, name_of_user, name_of_task, duration_of_task, notes, edited_date = input_task_data()
    # edited_date avoids shadowing date
    tasks[ti].task_00_project = project
    tasks[ti].task_1_user_name = name_of_user
    tasks[ti].task_0_name = name_of_task
    tasks[ti].task_3_duration = duration_of_task
    tasks[ti].task_4_notes = notes
    tasks[ti].task_2_date = edited_date

    user_confirm = input("Confirm edit y/N").strip().lower()
    if user_confirm == "y":
        tasks[ti].save()
        print("Task edited")
    else:
        print("Nothing changed")
    return ti


def delete_task(ti, tasks):
    """
    Handles task deletion
    :param ti: int, task index
    :param tasks: [Task]
    :return: int
    """
    user_confirms = input("Please confirm you want to delete this task y/N").strip().lower()
    if user_confirms == "y":
        tasks[ti].delete_instance()
        print("Task {} deleted".format(tasks[ti].task_0_name))
        return -1
    else:
        return ti


def view_entries(
        tasks,
        fields_to_hide=set([]),
        title="Tasks"
):
    """
    Show filtered tasks, task by task, allows navigation, also acts as menu to edit and delete tasks

    OK Ducky, First thing we call show_task_and_menu to show us the first task and a sub menu
    That sub menu has choices for next, previous, edit, delete task and exit view entries
    We ask the user nicely for a choice, passing around the task index
    If the user wants to exit we pass -1


    :param tasks: Tasks Filtered tasks
    :param fields_to_hide: set([strings]) A set of strings referring to the task field names that we don't want to show
    :param title: String to show as title of the filter being shown
    :return: None
    """
    fields = {"task_00_project", "task_0_name", "task_1_user_name", "task_2_date", "task_4_notes", "task_3_duration"}
    fields_to_show = sorted(list(fields - fields_to_hide))

    number_of_tasks = len(tasks)

    def input_choice(choices,
                     menu_prompt="(p)revious\t(n)ext\n(d)elete\t(e)dit\ne(x)it", help_message=""):
        """
        Handles the sub-menu
        :param menu_prompt: string
        :param choices: a dictionary with the show menu choices
        :param help_message: string
        :return: char with the menu option
        """
        show_help_message(help_message)
        print(term.bold_underline("Menu\n"))
        print(term.bold(menu_prompt))
        choice = input().lower().strip()

        if choice in choices.keys():
            logging.info("choice in choice keys")
            return choice
        else:
            return input_choice(choices=choices, help_message="\aValid choices: p,n,x")

    def show_task_and_menu(ti=0):
        """
        Shows a given task in the tasks lists
        and a sub menu for the user to interact on such task
        ask user input
        calls the appropriate function for the menu option select
        :param ti:
        :return: None
        """

        choices = {"n": next_task, "p": previous_task, "x": exit_view, "d": delete_task, "e": edit_task}
        # choices a dictionary with the show menu choices
        try:
            show_task(task=tasks[ti], total_tasks=number_of_tasks, task_number=ti + 1)
        except IndexError:
            logging.ERROR("Index Error on show_task_and_menu, perhaps no tasks on the database")
            print("You may want to add a task first")
            return None

        choice = choices[input_choice(choices)]

        ti = choice(ti, tasks)

        if ti < 0:
            return None
        else:
            return show_task_and_menu(ti)

    def show_task(task, total_tasks, task_number):
        """
        Shows a task nicely
        :param task: Task
        :param total_tasks: int
        :param task_number: int
        :return: None
        """
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

    show_task_and_menu()


def get_tasks_by_date():
    try:
        return Task.select().order_by(Task.task_2_date)
    except OperationalError:
        logging.ERROR("Operational Error on get_tasks_by_date")
        return None


def show_dates_with_tasks():
    """
    Shows a lists of dates that have tasks, and the number of tasks on each date
    :return: [string] list_of_dates
    """

    tasks = get_tasks_by_date()

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


def safe_date_choice_input(list_of_dates: list, validation_message: str = "") -> date:
    """
    manages input to safely choose a date among those which have tasks
    :param list_of_dates: [str]
    :param validation_message: str
    :return: date
    """
    show_help_message(validation_message)

    raw_input = input("\nEnter date to look for: ")
    try:
        date_entered = list_of_dates[int(raw_input) - 1]
        day, month, year = date_entered.split("/")
        return date(int(year), int(month), int(day))
    except IndexError:
        logging.info("User entered a number not in the dates list on safe_date_choice_input")
        return safe_date_choice_input(list_of_dates,
                                      validation_message="That number does not correspond to any date.")
    except ValueError:
        logging.info("User entered something other than a number in the dates list on safe_date_choice_input")
        return safe_date_choice_input(list_of_dates,
                                      validation_message="Choose any of the dates using its ordinal number.")


def search_entries_by_date():
    """
    Finds tasks if names or notes done in a particular date
    Shows filtered task
    :return: None
    """

    list_of_dates = show_dates_with_tasks()

    if list_of_dates:

        date_to_search = safe_date_choice_input(list_of_dates)

        tasks = Task.select().where(Task.task_2_date == date_to_search)

        view_entries(tasks,
                     title="Tasks completed on {}".format(date_to_search.strftime(DATE_FORMAT)),
                     fields_to_hide={"task_2_date"})

    else:
        print("Database empty")


def get_filtered_tasks(term_filter, attribute_to_filter=None):
    """
    returns list of tasks filtered according to selection
    :param attribute_to_filter: the attribute we are searching for
    :param term_filter: string
    :return: [task] or None
    """
    try:
        all_tasks = Task.select()
    except OperationalError:
        return None

    try:
        if attribute_to_filter:
            return all_tasks.where(attribute_to_filter == term_filter)
        else:
            return Task.select().where(
                (Task.task_0_name.contains(term_filter)) |
                (Task.task_4_notes.contains(term_filter))
            )
    except OperationalError:
        logging.error("The data model could be messed up or the var to filter could be invalid")
        return None


def search_entries_by_employee():
    """
    1. Finds tasks if names or notes done by a particular user
    2. Shows filtered task
    :return: None
    """
    employee = input("Employee name:").strip()

    tasks = get_filtered_tasks(employee, Task.task_1_user_name)
    if tasks:
        view_entries(tasks,
                     title="Tasks completed by {}".format(employee),
                     fields_to_hide={"task_1_user_name"})
    else:
        print("No tasks by employee: {}".format(employee))


def find_by_search_term():
    """
    1. Finds tasks if names or notes contains a search term provided by the user
    2. Shows filtered task
    :return: None
    """
    search_term = input("Term to search:").strip()

    tasks = get_filtered_tasks(term_filter=search_term)

    if tasks:
        view_entries(tasks,
                     title="Tasks that contain \"{}\"".format(search_term))
    else:
        print("No task meets the search term \"{}\"".format(search_term))


def search_by_project():
    """
    Searches by project, shows filtered task calling view_entries
    :return: None
    """
    project_to_search = input("Project to search for:").strip()

    tasks = get_filtered_tasks(term_filter=project_to_search, attribute_to_filter=Task.task_00_project)

    if tasks:
        view_entries(tasks,
                     title="Tasks that belong to \"{}\"".format(project_to_search))
    else:
        print("No task in the project: \"{}\"".format(project_to_search))
        return None


def search_entries(help_str=""):
    """
    Handles sub menu for different ways to search
    :return:
    """
    print(term.clear)
    show_help_message(help_str)
    search_menu = OrderedDict([
        ("e", [search_entries_by_employee, "search entries by employee"]),
        ("f", [find_by_search_term, "find by search term"]),
        ("d", [search_entries_by_date, "find by date"]),
        ("p", [search_by_project, "find by project"])
    ])


    for key, value in search_menu.items():
        print("{} {} {} {}".format(term.bold, key, term.normal, value[1].title()))
    choice = input().strip().lower()
    if choice in search_menu.keys():
        search_menu[choice][0]()
    else:
        logging.info("Search Entry Option not in menu")
        return search_entries(help_str="\aOption not in menu")



def menu_loop(menu):
    """
    Main menu loop
    :param menu: OrderedDict
    :return: None
    """
    print(term.clear)
    while True:
        for key, value in menu.items():
            print("{} {} {} {}".format(term.bold, key, term.normal, value[1].title()))

        choice = input("Choice: ").strip()

        if choice in menu:
            menu[choice][0]()


def quit_script():
    logging.info("User chose to exit the script")
    exit(0)


def main():
    """
    Main Function
    :return: None
    """

    initialize()

    main_menu = OrderedDict([
        ('a', [add_task, "add task"]),
        ('s', [search_entries, "search entries"]),
        ('q', [quit_script, "quit script"]),
    ])

    menu_loop(main_menu)


if __name__ == '__main__':
    logging.info("Script begins to run")
    main()
else:
    pass
