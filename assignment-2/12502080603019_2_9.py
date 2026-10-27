"""
Enrollment_2_9.py
Assignment 2, Question 9: OOP Inventory Merger with Operator Overloading
Problem Statement: Design Product and Inventory classes. Inventory must support adding products,
deleting products, updating stock, comparing inventories by total value, and merging two inventories
using operator overloading (+). Conflicting product ids must merge stock quantities but preserve
the lower purchase price and higher selling price for reporting.
Input Format: Two inventory files followed by q operations such as ADD, DELETE, UPDATE, MERGE and COMPARE.
Output Format: Operation status, merged inventory summary and total valuation.
Expected Time Complexity: O(n + m + q) average using dictionaries
Expected Space Complexity: O(n + m)
"""

import sys
import os

class Product:
    def __init__(self, pid, name, stock, purchase, selling):
        self.pid = str(pid).strip()
        self.name = str(name).strip()
        self.stock = int(stock)
        self.purchase = float(purchase)
        self.selling = float(selling)

    def __str__(self):
        p_val = int(self.purchase) if self.purchase.is_integer() else f"{self.purchase:.2f}"
        s_val = int(self.selling) if self.selling.is_integer() else f"{self.selling:.2f}"
        return f"{self.pid} {self.name} stock={self.stock} purchase={p_val} selling={s_val}"

class Inventory:
    def __init__(self, name=""):
        self.name = name
        self.products = {}

    def add(self, product):
        if product.pid in self.products:
            p = self.products[product.pid]
            p.stock += product.stock
            p.purchase = min(p.purchase, product.purchase)
            p.selling = max(p.selling, product.selling)
        else:
            self.products[product.pid] = Product(
                product.pid, product.name, product.stock, product.purchase, product.selling
            )

    def delete(self, pid):
        if pid in self.products:
            del self.products[pid]
            return True
        return False

    def update_stock(self, pid, new_stock):
        if pid in self.products:
            self.products[pid].stock = int(new_stock)
            return True
        return False

    def total_value(self):
        return sum(p.stock * p.selling for p in self.products.values())

    def __lt__(self, other):
        return self.total_value() < other.total_value()

    def __gt__(self, other):
        return self.total_value() > other.total_value()

    def __eq__(self, other):
        return self.total_value() == other.total_value()

    def __add__(self, other):
        merged = Inventory("Merged")
        for p in self.products.values():
            merged.add(p)
        for p in other.products.values():
            merged.add(p)
        return merged

def parse_product_line(line):
    parts = line.split()
    if len(parts) >= 5:
        pid = parts[0]
        name = parts[1]
        stock = parts[2]
        purchase = parts[3]
        selling = parts[4]
        return Product(pid, name, stock, purchase, selling)
    return None

def load_file_into_inventory(filepath, inv):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                p = parse_product_line(line.strip())
                if p:
                    inv.add(p)

def main():
    inv_a = Inventory("A")
    inv_b = Inventory("B")
    operations = []

    if sys.stdin.isatty():
        print("=== Inventory Manager (Q9) ===")
        print("1. Run Sample (A: P1 Pen 10 5 8, B: P1 Pen 7 4 9 -> MERGE)")
        print("2. Enter custom inventory and operations")
        choice = input("Enter choice (1 or 2, default 1): ").strip()

        if choice == "2":
            print("\nEnter products for Inventory A (format: P1 Pen 10 5 8).")
            print("Type 'done' when finished:")
            while True:
                line = input("Inventory A > ").strip()
                if line.lower() == "done" or not line:
                    break
                p = parse_product_line(line)
                if p:
                    inv_a.add(p)

            print("\nEnter products for Inventory B (format: P1 Pen 7 4 9).")
            print("Type 'done' when finished:")
            while True:
                line = input("Inventory B > ").strip()
                if line.lower() == "done" or not line:
                    break
                p = parse_product_line(line)
                if p:
                    inv_b.add(p)

            print("\nEnter operations (MERGE, COMPARE, ADD, DELETE, UPDATE).")
            print("Type 'done' when finished:")
            while True:
                op = input("Operation > ").strip()
                if op.lower() == "done" or not op:
                    break
                operations.append(op)
        else:
            inv_a.add(Product("P1", "Pen", 10, 5, 8))
            inv_b.add(Product("P1", "Pen", 7, 4, 9))
            operations = ["MERGE"]
            print("\nResult:")
    else:
        lines = sys.stdin.read().splitlines()
        if not lines:
            return

        first_tokens = lines[0].strip().split()
        if len(first_tokens) >= 2 and os.path.exists(first_tokens[0]) and os.path.exists(first_tokens[1]):
            load_file_into_inventory(first_tokens[0], inv_a)
            load_file_into_inventory(first_tokens[1], inv_b)
            operations = lines[1:]
        else:
            current_target = inv_a
            for line in lines:
                line_str = line.strip()
                if not line_str:
                    continue

                if line_str.startswith("Inventory A:"):
                    current_target = inv_a
                    content = line_str.replace("Inventory A:", "").strip()
                    p = parse_product_line(content)
                    if p:
                        current_target.add(p)
                elif line_str.startswith("Inventory B:"):
                    current_target = inv_b
                    content = line_str.replace("Inventory B:", "").strip()
                    p = parse_product_line(content)
                    if p:
                        current_target.add(p)
                elif line_str.startswith("Operation:"):
                    op = line_str.replace("Operation:", "").strip()
                    operations.append(op)
                elif line_str.startswith(("ADD", "DELETE", "UPDATE", "MERGE", "COMPARE")):
                    operations.append(line_str)
                else:
                    p = parse_product_line(line_str)
                    if p:
                        current_target.add(p)

    for op in operations:
        parts = op.split()
        if not parts:
            continue
        cmd = parts[0].upper()

        if cmd == "MERGE":
            merged = inv_a + inv_b
            for pid in sorted(merged.products.keys()):
                print(merged.products[pid])
        elif cmd == "COMPARE":
            val_a = inv_a.total_value()
            val_b = inv_b.total_value()
            if inv_a > inv_b:
                cmp_sym = ">"
            elif inv_a < inv_b:
                cmp_sym = "<"
            else:
                cmp_sym = "=="
            print(f"Inventory A ({val_a:.2f}) {cmp_sym} Inventory B ({val_b:.2f})")
        elif cmd == "ADD":
            target = inv_a if parts[1].upper() == "A" else inv_b
            p = Product(parts[2], parts[3], parts[4], parts[5], parts[6])
            target.add(p)
            print(f"ADDED {p.pid}")
        elif cmd == "DELETE":
            target = inv_a if parts[1].upper() == "A" else inv_b
            pid = parts[2]
            success = target.delete(pid)
            print(f"DELETED {pid}" if success else f"NOT FOUND {pid}")
        elif cmd == "UPDATE":
            target = inv_a if parts[1].upper() == "A" else inv_b
            pid = parts[2]
            new_stock = parts[3]
            success = target.update_stock(pid, new_stock)
            print(f"UPDATED {pid}" if success else f"NOT FOUND {pid}")

if __name__ == "__main__":
    main()
