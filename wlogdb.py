#!/usr/bin/env python3

"""

Work Log Databse Script

A simple work log script using a SQL db to implement its data model

Began on: 7 September 2016

by Miguel de Luis



"""

from collections import OrderedDict
import datetime

from peewee import *
from blessings import Terminal

db = SqliteDatabase("work_log.db")




class Task(Model):
    user_name = CharField(max_length=255)
    task_name = CharField(max_length=255, unique=True)
    task_duration = IntegerField(help_text="Time spent on the task, in minutes")
    task_date = DateTimeField(default=datetime.datetime.now)  # research Date Formats
    task_notes = TextField()
    
    class Meta:
        database = db


def add_task():
    """

    """
    name_of_user = input("Enter your name: ")
    name_of_task = input("Task name:")
    duration_of_task = input("Minutes")
    notes = input("notes")

    Task.create(user_name=name_of_user, task_name=name_of_task,
                task_duration=duration_of_task, task_notes=notes)


def initialize():
    db.connect()
    db.create_tables([Task], safe=True)


def view_entries():
    """

    :return:
    """
    pass


def quit_script():
    """
    Quit program
    :return:
    """
    quit()

menu = OrderedDict([
    ('a', [add_task, "add task"]),
    ('v', [view_entries, "view entries"]),
    ('q', [quit_script, "quit script"]),
])

term = Terminal()


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
