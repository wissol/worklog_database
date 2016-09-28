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

    def test_cook_date_bad_data(self):
        with self.assertLogs():
            wlogdb.cook_raw_date("","abanibia_boembé")

    def test_show_dates_with_tasks(self):
        a = wlogdb.show_dates_with_tasks()
        self.assertIsNot(a,None)
        b = wlogdb.safe_date_choice_input(a,"")
        self.assertIsInstance(b, date)


class BadRawTaskDate(unittest.TestCase):
    @unittest.expectedFailure
    def test_pipo(self):
        with self.assertRaises(self):
            wlogdb.process_raw_time("a", raw_time="treinta y siete:12.5")



if __name__ == '__main__':
    unittest.main()
