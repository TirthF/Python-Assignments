"""
Enrollment_2_7.py
Assignment 2, Question 7: Generator-Based JSON ETL Pipeline
Problem Statement: Create an ETL pipeline using generator functions that reads a large JSON-lines
file of sensor records, filters corrupted records, transforms units, groups readings by device
and produces summary statistics. The program must not load the full file into memory.
Input Format: Path of JSONL file. Each line contains device_id, timestamp, temperature_c and humidity.
Output Format: For each device: count, min temperature, max temperature, average temperature and corrupted record count.
Expected Time Complexity: O(number of records)
Expected Space Complexity: O(number of devices)
"""

import sys
import os
import json

def extract(filepath):
    """Generator reading JSONL file line-by-line without loading entire file into memory."""
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                yield line

def transform(lines):
    """Generator transforming lines into validated records."""
    for line in lines:
        try:
            data = json.loads(line)
        except Exception:
            continue

        device_id = data.get("device_id")
        if not device_id:
            continue

        try:
            temp = float(data["temperature_c"])
            humidity = float(data.get("humidity", 0))
            yield device_id, temp, humidity, True
        except (ValueError, TypeError, KeyError):
            yield device_id, None, None, False

def load_and_aggregate(records):
    """Single-pass accumulator computing running statistics per device."""
    stats = {}
    for device_id, temp, humidity, is_valid in records:
        if device_id not in stats:
            stats[device_id] = [0, 0.0, float('inf'), float('-inf'), 0]

        dev = stats[device_id]
        if is_valid:
            dev[0] += 1
            dev[1] += temp
            if temp < dev[2]:
                dev[2] = temp
            if temp > dev[3]:
                dev[3] = temp
        else:
            dev[4] += 1
    return stats

def main():
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        print("=== Sensor Data ETL Pipeline (Q7) ===")
        filepath = input("Enter path to JSONL file (e.g. sensor_data.jsonl): ").strip()

    if not filepath:
        print("Error: No file path provided.")
        return

    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        return

    lines = extract(filepath)
    records = transform(lines)
    stats = load_and_aggregate(records)

    for device in sorted(stats.keys()):
        count, total, min_val, max_val, corrupted = stats[device]
        if count > 0:
            avg = total / count
            min_str = int(min_val) if min_val == int(min_val) else f"{min_val:.2f}"
            max_str = int(max_val) if max_val == int(max_val) else f"{max_val:.2f}"
            print(f"{device} count={count} min={min_str} max={max_str} avg={avg:.2f} corrupted={corrupted}")
        else:
            print(f"{device} count=0 min=0 max=0 avg=0.00 corrupted={corrupted}")

if __name__ == "__main__":
    main()
