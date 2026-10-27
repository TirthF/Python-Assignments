import sys
import os
import re

EMAIL_PATTERN = re.compile(
    r'(?<![a-zA-Z0-9+_\-@])'
    r'([a-zA-Z0-9+_-]+(?:\.[a-zA-Z0-9+_-]+)*)'
    r'@'
    r'([a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)*\.(?:com|edu|org))'
    r'\b(?!\.[a-zA-Z0-9])',
    re.IGNORECASE
)


def validate_file_path(path_str: str) -> str | None:

    if not path_str:
        sys.stderr.write("Input Error: File path cannot be empty.\n")
        return None

    clean_path = path_str.strip('"\'')

    if not os.path.exists(clean_path):
        sys.stderr.write(f"File Error: Path does not exist: '{clean_path}'\n")
        return None

    if not os.path.isfile(clean_path):
        sys.stderr.write(f"File Error: Path is not a regular file: '{clean_path}'\n")
        return None

    if not os.access(clean_path, os.R_OK):
        sys.stderr.write(f"Permission Error: File is not readable: '{clean_path}'\n")
        return None

    return clean_path


def process_email_records(file_path: str) -> dict[str, dict]:
    '''
    Reads the input text file line-by-line with a 1 MB buffer to handle files up to 1 GB.
    '''
    domain_data: dict[str, dict] = {}

    with open(file_path, mode='r', buffering=1024 * 1024, encoding='utf-8', errors='ignore') as file:
        for line in file:
            for match in EMAIL_PATTERN.finditer(line):
                username = match.group(1)
                domain = match.group(2).lower()  # Domain names are case-insensitive per RFC

                if domain not in domain_data:
                    email = f"{username}@{domain}"
                    domain_data[domain] = {
                        'users': {username},
                        'smallest_email': email
                    }
                else:
                    entry = domain_data[domain]
                    entry['users'].add(username)
                    email = f"{username}@{domain}"
                    if email < entry['smallest_email']:
                        entry['smallest_email'] = email

    return domain_data

def display_domain_statistics(domain_data: dict[str, dict]) -> None:
   
    for domain in sorted(domain_data.keys()):
        info = domain_data[domain]
        print(f"{domain} {len(info['users'])} {info['smallest_email']}")


def main() -> None:
    # Acquire file path from command line arguments or user input
    if len(sys.argv) > 1:
        raw_path = sys.argv[1].strip()
    else:
        try:
            prompt_text = "Enter path of text file: " if sys.stdin.isatty() else ""
            raw_path = input(prompt_text).strip()
        except (EOFError, KeyboardInterrupt):
            return

    # Input Validation
    validated_path = validate_file_path(raw_path)
    if not validated_path:
        sys.exit(1)

    # Process & Display Results
    domain_data = process_email_records(validated_path)
    display_domain_statistics(domain_data)


if __name__ == "__main__":
    main()
