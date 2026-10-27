"""
File: Enrollment_2_2.py (Replace 'Enrollment' with your Student ID / Enrollment Number)
Assignment: 2, Question: 2
Problem: Multi-Page HTML Product Scraper and Top-K Ranker
Language: Python 3.10 or above
Dependencies: Standard Library only (re, sys, os, html) - No external packages needed.

Run Instructions:
    python Enrollment_2_2.py
    Input:
    p k
    path_to_page1.html
    path_to_page2.html
    ...
"""

import sys
import os
import re
import html


def parse_and_validate_header(header_line: str) -> tuple[int, int] | None:
    """
    Validates that the header contains two valid positive integers: p and k.
    Constraints: 1 <= p <= 5000, 1 <= k <= 1000.
    """
    tokens = header_line.split()
    if len(tokens) < 2:
        sys.stderr.write("Input Error: First line must contain two integers: p and k.\n")
        return None

    try:
        p = int(tokens[0])
        k = int(tokens[1])
    except ValueError:
        sys.stderr.write("Input Error: p and k must be valid integers.\n")
        return None

    if p < 1 or p > 5000:
        sys.stderr.write(f"Warning: p ({p}) is outside [1, 5000]. Proceeding with p={max(1, p)}.\n")
        p = max(1, p)

    if k < 1:
        sys.stderr.write(f"Warning: k ({k}) must be at least 1. Proceeding with k=1.\n")
        k = 1

    return p, k


def parse_product_block(block_text: str) -> tuple[str, float, float, int | float] | None:
    """
    Extracts and normalizes product name, rating, and price from an HTML block.
    Returns (name, rating_val, price_val, norm_price) or None if incomplete.
    """
    # 1. Product Name extraction
    name_match = re.search(
        r'<[^>]*class=[\'"][^\'"]*(?:name|title)[^\'"]*[\'"][^>]*>(.*?)</',
        block_text,
        re.IGNORECASE | re.DOTALL
    )
    if not name_match:
        name_match = re.search(r'<h[1-6][^>]*>(.*?)</h[1-6]>', block_text, re.IGNORECASE | re.DOTALL)

    if not name_match:
        return None

    clean_name = re.sub(r'<[^>]+>', '', name_match.group(1)).strip()
    name = html.unescape(clean_name)
    if not name:
        return None

    # 2. Price extraction & normalization
    price_match = re.search(
        r'<[^>]*class=[\'"][^\'"]*price[^\'"]*[\'"][^>]*>(.*?)</',
        block_text,
        re.IGNORECASE | re.DOTALL
    )
    price_segment = price_match.group(1) if price_match else block_text

    price_num_match = re.search(r'[\$₹£€]?\s*(\d+(?:,\d+)*(?:\.\d+)?)', price_segment)
    if not price_num_match:
        return None

    price_val = float(price_num_match.group(1).replace(',', ''))
    # Normalize price format: 499 if integer, else 499.5
    norm_price = int(price_val) if price_val.is_integer() else price_val

    # 3. Rating extraction
    rating_match = re.search(
        r'<[^>]*class=[\'"][^\'"]*(?:rating|stars?|score)[^\'"]*[\'"][^>]*>(.*?)</',
        block_text,
        re.IGNORECASE | re.DOTALL
    )
    rating_segment = rating_match.group(1) if rating_match else block_text

    rating_num_match = re.search(r'(\d+(?:\.\d+)?)', rating_segment)
    if not rating_num_match:
        return None

    rating_val = float(rating_num_match.group(1))

    return name, rating_val, price_val, norm_price


def extract_products_from_file(file_path: str, products_dict: dict[str, tuple]) -> None:
    """
    Reads one HTML file at a time, keeping memory footprint O(u).
    Extracts products and removes duplicates by name (favors higher rating, then lower price).
    
    Time Complexity: O(size of this file)
    """
    clean_path = file_path.strip('"\'')
    if not os.path.exists(clean_path):
        sys.stderr.write(f"Warning: File not found: '{clean_path}' (skipping)\n")
        return

    if not os.path.isfile(clean_path):
        sys.stderr.write(f"Warning: Path is not a file: '{clean_path}' (skipping)\n")
        return

    # Read and parse file
    with open(clean_path, 'r', encoding='utf-8', errors='ignore') as f:
        html_content = f.read()

    # Split into product containers (looks for div, article, li, tr with product/item/card classes)
    blocks = re.split(
        r'<(?:div|article|li|tr|section)[^>]*class=[\'"][^\'"]*(?:product|item|card|listing)[^\'"]*[\'"][^>]*>',
        html_content,
        flags=re.IGNORECASE
    )
    candidate_blocks = blocks[1:] if len(blocks) > 1 else [html_content]

    for block in candidate_blocks:
        parsed = parse_product_block(block)
        if not parsed:
            continue

        name, rating_val, price_val, norm_price = parsed

        # Deduplication by name: keep record with best rank (highest rating, lowest price)
        if name not in products_dict:
            products_dict[name] = (rating_val, price_val, name, norm_price)
        else:
            curr_rating, curr_price, _, _ = products_dict[name]
            if (rating_val, -price_val) > (curr_rating, -curr_price):
                products_dict[name] = (rating_val, price_val, name, norm_price)


def rank_and_display_top_products(products_dict: dict[str, tuple], k: int) -> None:
    """
    Sorts unique products by:
      1. Highest rating first (-rating)
      2. Lower price next (price)
      3. Lexicographical product name (name)
    Prints the top K products.
    """
    sorted_products = sorted(products_dict.values(), key=lambda item: (-item[0], item[1], item[2]))

    for rating_val, price_val, name, norm_price in sorted_products[:k]:
        print(f"{name} {norm_price} {rating_val}")


def main() -> None:
    prompt_header = "Enter p (files) and k (top products) [e.g. '2 2']: " if sys.stdin.isatty() else ""
    try:
        first_line = input(prompt_header).strip()
        while not first_line:
            first_line = input().strip()
    except (EOFError, KeyboardInterrupt):
        return

    header = parse_and_validate_header(first_line)
    if not header:
        sys.exit(1)

    p, k = header
    products_dict: dict[str, tuple] = {}

    for i in range(p):
        prompt_file = f"Enter path for HTML file {i + 1}: " if sys.stdin.isatty() else ""
        try:
            file_path = input(prompt_file).strip()
            if file_path:
                extract_products_from_file(file_path, products_dict)
        except (EOFError, KeyboardInterrupt):
            break

    rank_and_display_top_products(products_dict, k)


if __name__ == "__main__":
    main()
