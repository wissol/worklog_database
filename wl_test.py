import unittest
from datetime import date

import wlogdb


class ShowHelpMessageTest(unittest.TestCase):
    def test_input_task_date_returns_date(self):
        testing_date_is_date = wlogdb.input_task_date(prompt="Testing Input Task Date", help_message="Type a Date")
        self.assertIsInstance(testing_date_is_date, date)

    def test_show_message(self):
        test_show_message_variable = wlogdb.show_help_message("A help message has been printed")
        self.assertEqual(test_show_message_variable, 1, "And returns 1")
        test_show_message_variable = wlogdb.show_help_message("")
        self.assertEqual(test_show_message_variable, 0, "No help message has been printed and returns 0")

    def test_view_task(self):
        tasks = wlogdb.Task.select().order_by(wlogdb.Task.task_2_date)
        self.assertIsNot(len(tasks), 0)

    def test_raw_task_date(self):
        a = wlogdb.process_raw_time("", raw_time="12:22")
        self.assertEqual(a, 12*60 + 22)

    def test_next_task(self):
        next1 = wlogdb.next_task(2, wlogdb.Task.select())
        self.assertEqual(next1, 3)
        next2 = wlogdb.next_task(3, wlogdb.Task.select())
        self.assertEqual(next2, 3)

    def test_previous_task(self):
        prev1 = wlogdb.previous_task(0, wlogdb.Task.select())
        self.assertEqual(prev1, 0)
        prev2 = wlogdb.previous_task(3, wlogdb.Task.select())
        self.assertEqual(prev2, 2)

    def test_cook_date(self):
        rtd = "23/12/2015"
        ctd = wlogdb.cook_raw_date("", rtd)
        self.assertEqual(ctd, date(year=2015, month=12, day=23))

    def test_cook_date_y(self):
        rtd = "y2015/12/23"
        ctd = wlogdb.cook_raw_date("", rtd)
        self.assertEqual(ctd, date(year=2015, month=12, day=23))

    def test_cook_date_m(self):
        rtd = "m12/23/ 2015"  # adding a space just in case it makes it fail
        ctd = wlogdb.cook_raw_date("", rtd)
        self.assertEqual(ctd, date(year=2015, month=12, day=23))

    def test_cook_date_help(self):
        rtd = "help"
        with self.assertLogs():
            wlogdb.cook_raw_date("", rtd)

    def test_cook_date_bad_data(self):
        with self.assertLogs():
            wlogdb.cook_raw_date("", "abanibia boembé")

    def test_show_dates_with_tasks(self):
        a_date_index = wlogdb.show_dates_with_tasks()
        self.assertIsNot(a_date_index, None)
        b = wlogdb.safe_date_choice_input(a_date_index, "")
        self.assertIsInstance(b, date)

    def test_bad_raw_time(self):
        process_12_67_test = wlogdb.process_raw_time("", "12:67")
        self.assertNotEqual(process_12_67_test, 12 + 67*60)

    def test_input_standard_data(self):
        input_std_data_test = wlogdb.input_standard_data("TESTING: Input standard data Test, something over 5 chars",
                                                         field_length=5)
        self.assertLessEqual(len(input_std_data_test), 5)

    def test_get_filtered_tasks(self):
        tasks_with_300_stars = wlogdb.get_filtered_tasks("*"*300)  # a 300 * string shouldn't be in the database
        self.assertIs(len(tasks_with_300_stars), 0)

    def test_get_filtered_tasks_cosa(self):
        wlogdb.Task.create(task_00_project="project", task_1_user_name="name_of_user",
                           task_0_name="name_of_task",task_3_duration=9999,
                           task_4_notes="notes", task_2_date=wlogdb.date.today()
                           )
        tasks_with_duration9999 = wlogdb.get_filtered_tasks("project", attribute_to_filter=wlogdb.Task.task_00_project)
        self.assertEqual(tasks_with_duration9999[0].task_3_duration, 9999)

    def test_process_raw_time(self):
        with self.assertLogs() as l:
            wlogdb.process_raw_time("", "raw_time")
            self.assertIn("INFO:root:Unrecognised time spent format", l.output)

    def test_search_entries_main_menu(self):
        with self.assertLogs():
            # print "Search for something not in search menu like 343434 or this test will fail"
            wlogdb.search_entries("TESTING: Search for something not in search menu like 343434 or this test will fail")

    def test_safe_date_choice_input(self):
        self.assertEqual(wlogdb.safe_date_choice_input(list_of_dates=["25/12/2016"],
                                                       validation_message="\aTESTING type 1 <---"),
                         date(year=2016, month=12, day=25)
                         )

        with self.assertLogs() as log:
            wlogdb.safe_date_choice_input(list_of_dates=["25/12/2016"],
                                          validation_message="\aTESTING NOW type 2  <---")
            self.assertIn("INFO:root:User entered a number not in the dates list on safe_date_choice_input",
                          log.output)

        with self.assertLogs() as log:
            wlogdb.safe_date_choice_input(list_of_dates=["25/12/2016"],
                                          validation_message="\aTESTING FINALLY type anything but a number   <---"
                                          )
            self.assertIn(
                "INFO:root:User entered something other than a number in the dates list on safe_date_choice_input",
                log.output)


class BadRawTaskDate(unittest.TestCase):
    @unittest.expectedFailure
    def test_pipo(self):
        with self.assertRaises(self):
            wlogdb.process_raw_time("a", raw_time="treinta y siete:12.5")


if __name__ == '__main__':
    unittest.main()
