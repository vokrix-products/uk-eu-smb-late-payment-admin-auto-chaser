#!/usr/bin/env python3
"""Demo: process a hardcoded CSV without any arguments, print results, exit 0."""

from processor import process_file

def main():
    # Hardcoded CSV representing a simple supplier payment statement
    csv_data = (
        "vendor,amount,due_date,status\n"
        "Acme Corp,1500.00,2024-12-01,overdue\n"
        "Global Supply Ltd,2300.00,2025-01-15,pending\n"
        "TechParts Inc,750.00,2025-02-28,paid\n"
    )
    test_bytes = csv_data.encode('utf-8')

    results = process_file(test_bytes)

    print(f"Extracted {len(results)} record(s):")
    for rec in results:
        print(rec)

if __name__ == "__main__":
    main()
    exit(0)
