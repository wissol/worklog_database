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

db = SqliteDatabase("work_log.db")

term = Terminal()


class Task(Model):
    user_name = CharField(max_length=255)
    task_name = CharField(max_length=255)
    task_duration = IntegerField(help_text="Time spent on the task, in minutes")
    task_date = DateTimeField(default=datetime.datetime.now)  # research Date Formats
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




def add_task():
    """

    """
    ugly_prompts = ["Your name:\t", "Your task name:\t", 'Time spent on the task:\t', "Notes, ctrl+d to finish."]

    def give_format(x):
        return term.bold(x)

    pretty_prompts = list(map(give_format, ugly_prompts))

    name_of_user = barbican(pretty_prompts[0])
    name_of_task = barbican(pretty_prompts[1])
    duration_of_task = barbican(pretty_prompts[2], is_time=True)

    print(pretty_prompts[3])
    notes = stdin.read()

    Task.create(user_name=name_of_user, task_name=name_of_task,
                task_duration=duration_of_task, task_notes=notes)


def initialize():
    db.connect()
    db.create_tables([Task], safe=True)


def view_entries():
    """

    :return:
    """
    tasks = Task.select().order_by(Task.task_date.desc())
    for task in tasks:
        print(task.task_name)
        print(task.user_name)
        print(task.task_date.strftime("%d/%m/%y"))
        print(task.task_notes)

def show_help():
    print(term.clear)
    print("When prompted for the menu, input a to add a task, v to view entries, q to quit, h for this help")
    print("When adding the time spent on a task enter the time in minutes or in the hh:ss format ")

menu = OrderedDict([
    ('a', [add_task, "add task"]),
    ('v', [view_entries, "view entries"]),
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
