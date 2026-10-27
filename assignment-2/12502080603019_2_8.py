"""
Enrollment_2_8.py
Assignment 2, Question 8: Matrix Path Optimizer with Dynamic Programming
Problem Statement: Given an n x m matrix of integers, find the maximum score path from top-left
to bottom-right. You may move right, down or diagonally down-right. Some cells are blocked.
Also print the number of distinct maximum-score paths modulo 1000000007.
Input Format: First line: n m. Next n lines: m values where X represents blocked cell and integers represent scores.
Output Format: Maximum score and number of maximum-score paths. Print IMPOSSIBLE if no valid path exists.
Expected Time Complexity: O(n * m)
Expected Space Complexity: O(m) optimized
"""

import sys

def main():
    MOD = 1000000007

    if sys.stdin.isatty():
        print("=== Maximum Score Path in Matrix (Q8) ===")
        dim = input("Enter dimensions n and m (e.g. 3 3): ").strip()
        if not dim:
            return
        n, m = map(int, dim.split())
        print(f"Enter {n} rows of {m} values (use X for blocked cells, e.g. 1 2 3):")
        matrix = [input().strip().split() for _ in range(n)]
    else:
        input_data = sys.stdin.read().split()
        if not input_data:
            return
        n = int(input_data[0])
        m = int(input_data[1])
        idx = 2
        matrix = []
        for _ in range(n):
            matrix.append(input_data[idx:idx + m])
            idx += m

    prev_dp = [(-float('inf'), 0)] * m

    for i in range(n):
        curr_dp = [(-float('inf'), 0)] * m
        row = matrix[i]

        for j in range(m):
            cell = row[j]
            if cell == 'X':
                continue

            val = int(cell)

            if i == 0 and j == 0:
                curr_dp[0] = (val, 1)
                continue

            candidates = []
            if i > 0 and prev_dp[j][0] != -float('inf'):
                candidates.append(prev_dp[j])
            if i > 0 and j > 0 and prev_dp[j - 1][0] != -float('inf'):
                candidates.append(prev_dp[j - 1])
            if j > 0 and curr_dp[j - 1][0] != -float('inf'):
                candidates.append(curr_dp[j - 1])

            if not candidates:
                continue

            best_score = max(c[0] for c in candidates)
            total_ways = sum(c[1] for c in candidates if c[0] == best_score) % MOD
            curr_dp[j] = (best_score + val, total_ways)

        prev_dp = curr_dp

    ans_score, ans_ways = prev_dp[m - 1]
    if ans_score == -float('inf'):
        print("IMPOSSIBLE")
    else:
        print(f"{ans_score} {ans_ways}")

if __name__ == "__main__":
    main()
