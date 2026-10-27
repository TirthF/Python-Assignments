"""
Enrollment_2_6.py
Assignment 2, Question 6: Log Anomaly Detector using Sliding Window
Problem Statement: Given timestamped application logs, detect every user who has at least X failed
login attempts within any T-minute window followed by a successful login from a different IP address.
Use regex to parse log lines and an optimized sliding window per user.
Input Format: First line: X T. Next line: n. Next n lines: timestamp user ip status.
Output Format: Suspicious user ids in lexicographic order with the timestamp of the first detected suspicious success.
Constraints: 1 <= n <= 2000000, 1 <= X <= 100, 1 <= T <= 1440, logs are sorted by timestamp
Expected Time Complexity: O(n) using queues per user
Expected Space Complexity: O(active failures per user)
"""

import sys
import re
from collections import deque, defaultdict

LOG_PATTERN = re.compile(r'^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)')

def parse_time(ts):
    parts = ts.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 3600 + int(parts[1]) * 60
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return int(ts) * 60

def main():
    if sys.stdin.isatty():
        print("=== Suspicious Login Detector (Q6) ===")
        first_line = input("Enter X and T (e.g. 3 10): ").strip()
        if not first_line:
            return
        x_val, t_val = map(int, first_line.split())
        n = int(input("Enter number of log lines n (e.g. 5): ").strip())
        print(f"Enter {n} lines (format: timestamp user ip status):")
        log_lines = [input().strip() for _ in range(n)]
    else:
        input_data = sys.stdin.read().splitlines()
        lines = [line.strip() for line in input_data if line.strip()]
        if not lines:
            return
        x_val, t_val = map(int, lines[0].split())
        n = int(lines[1])
        log_lines = lines[2:2 + n]

    window_sec = t_val * 60
    user_failures = defaultdict(deque)
    user_ip_counts = defaultdict(lambda: defaultdict(int))
    suspicious_users = {}

    prev_sec = 0
    day_offset = 0

    for line in log_lines:
        match = LOG_PATTERN.match(line)
        if not match:
            continue

        ts_str, user, ip, status = match.groups()
        status = status.upper()

        if user in suspicious_users:
            continue

        sec = parse_time(ts_str)
        if sec < prev_sec:
            day_offset += 86400
        prev_sec = sec
        t_sec = sec + day_offset

        q = user_failures[user]
        counts = user_ip_counts[user]

        # Slide window: evict failures older than T minutes
        while q and (t_sec - q[0][0]) > window_sec:
            old_t, old_ip = q.popleft()
            counts[old_ip] -= 1
            if counts[old_ip] == 0:
                del counts[old_ip]

        if status == "FAIL":
            q.append((t_sec, ip))
            counts[ip] += 1
        elif status == "SUCCESS":
            # Check if there are at least X failures from a different IP
            diff_ip_failures = len(q) - counts.get(ip, 0)
            if diff_ip_failures >= x_val:
                suspicious_users[user] = ts_str
                del user_failures[user]
                del user_ip_counts[user]

    for user in sorted(suspicious_users.keys()):
        print(f"{user} {suspicious_users[user]}")

if __name__ == "__main__":
    main()
