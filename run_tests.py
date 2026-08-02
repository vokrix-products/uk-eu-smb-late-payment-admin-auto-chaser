#!/usr/bin/env python3
"""Unit tests for processor.py"""

import unittest
from processor import process_file, map_status

class TestProcessor(unittest.TestCase):

    def test_csv_simple(self):
        csv = "vendor,amount,due_date,status\nFoo Ltd,1000.00,2025-03-01,paid\n"
        recs = process_file(csv.encode('utf-8'))
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]['title'], 'Foo Ltd')
        self.assertEqual(recs[0]['status'], 'paid:good')
        self.assertEqual(recs[0]['due_date'], '2025-03-01')

    def test_missing_status(self):
        csv = "vendor,amount,due_date\nBar Inc,500.00,2024-06-15\n"
        recs = process_file(csv.encode('utf-8'))
        self.assertEqual(recs[0]['status'], 'pending:warning')

    def test_multiple_rows(self):
        csv = ("vendor,amount,due_date,status\n"
               "A,100,2025-01-01,pending\n"
               "B,200,2025-02-02,overdue\n")
        recs = process_file(csv.encode('utf-8'))
        self.assertEqual(len(recs), 2)
        self.assertEqual(recs[0]['status'], 'pending:warning')
        self.assertEqual(recs[1]['status'], 'overdue:critical')

    def test_date_formats(self):
        csv = "vendor,amount,due_date\nC,300,31/12/2024\n"
        recs = process_file(csv.encode('utf-8'))
        self.assertEqual(recs[0]['due_date'], '2024-12-31')

    def test_non_text_bytes(self):
        recs = process_file(b'\x80\x81\x82')
        self.assertEqual(recs, [])

    def test_map_status(self):
        self.assertEqual(map_status('paid'), 'paid:good')
        self.assertEqual(map_status('discrepancy'), 'discrepancy:critical')

if __name__ == '__main__':
    unittest.main()
