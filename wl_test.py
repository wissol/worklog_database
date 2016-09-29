import unittest
import wlogdb
import logging
from datetime import date


class ShowHelpMessageTest(unittest.TestCase):
    def test_something(self):
        a = wlogdb.input_task_date("a", "b")
        self.assertIsInstance(a, date)

    def test_show_message(self):
        b = wlogdb.show_help_message("print")
        self.assertEqual(b, 1, "print printed")
        b = wlogdb.show_help_message("")
        self.assertEqual(b, 0, "nothing does not get printed")

    def test_view_task(self):
        tasks = wlogdb.Task.select().order_by(wlogdb.Task.task_2_date)
        self.assertIsNot(tasks,[])

    def test_raw_task_date(self):
        a = wlogdb.process_raw_time("",raw_time="12:22")
        self.assertEqual(a, 12*60 + 22)

    def test_next_task(self):
        next1 = wlogdb.next_task(2,[1,2,3,4])
        self.assertEqual(next1,3)
        next2 = wlogdb.next_task(3,[1,2,3,4])
        self.assertEqual(next2,3)

    def test_previous_task(self):
        prev1 = wlogdb.previous_task(0, [])
        self.assertEqual(prev1, 0)
        prev2 = wlogdb.previous_task(3, [])
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
            wlogdb.cook_raw_date("", "abanibia_boembé")

    def test_show_dates_with_tasks(self):
        a_date_index = wlogdb.show_dates_with_tasks()
        self.assertIsNot(a_date_index, None)
        b = wlogdb.safe_date_choice_input(a_date_index, "")
        self.assertIsInstance(b, date)

    def test_bad_raw_time(self):
        process_12_67_test = wlogdb.process_raw_time("", "12:67")
        self.assertNotEqual(process_12_67_test, 12 + 67*60)

    def test_input_standard_data(self):
        input_std_data_test = wlogdb.input_standard_data("Input standard data Test, something over 5 chars",
                                                         field_length=5)
        self.assertLessEqual(len(input_std_data_test), 5)


class BadRawTaskDate(unittest.TestCase):
    @unittest.expectedFailure
    def test_pipo(self):
        with self.assertRaises(self):
            wlogdb.process_raw_time("a", raw_time="treinta y siete:12.5")



if __name__ == '__main__':
    unittest.main()
