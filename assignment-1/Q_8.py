"""
Log Indexer and Compressor Implementation
"""
import os
import re
import pickle
import zipfile

def main():
    while True:
        folder = input("Enter log folder path: ").strip()
        if not folder:
            print("Error: Folder path cannot be empty.")
            continue
        if not os.path.isdir(folder):
            print("Error: The specified folder does not exist. Please try again.")
            continue
        break

    index = {}

    # 1. Process files and build the index
    print(f"\nProcessing files in '{folder}'...")
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)

        if not os.path.isfile(filepath):
            continue

        if not filename.lower().endswith(".txt"):
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                for line_no, line in enumerate(file, 1):
                    # Extract alphanumeric tokens
                    tokens = re.findall(r'\b[a-zA-Z0-9]+\b', line.lower())

                    # Add unique tokens per line to the index
                    for token in set(tokens):
                        if token not in index:
                            index[token] = []
                        index[token].append((filename, line_no))
        except IOError as e:
            print(f"Warning: Could not read file {filename} ({e})")

    # 2. Save the index using pickle
    index_file = os.path.join(folder, "log_index.pkl")
    try:
        with open(index_file, "wb") as file:
            pickle.dump(index, file)
    except IOError as e:
        print(f"Error: Could not save index file ({e})")
        return

    # 3. Create a compressed ZIP archive of the logs and the index
    zip_file = os.path.join(folder, "compressed_logs.zip")
    try:
        with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)

                if os.path.isfile(filepath):
                    if filename.endswith(".txt") or filename == "log_index.pkl":
                        zipf.write(filepath, filename)
    except IOError as e:
        print(f"Error: Could not create ZIP archive ({e})")
        return

    print("\n--- Results ---")
    print("Index created successfully")
    print("Index file:", "log_index.pkl")
    print("ZIP file:", "compressed_logs.zip")

if __name__ == "__main__":
    main()