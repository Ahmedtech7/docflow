
import json
import sys


def load_inventory(path):
    try:
        with open(path, "r") as file:
            documents = json.load(file)

        if not isinstance(documents, list):
            raise ValueError("JSON must contain an array")

        return documents

    except FileNotFoundError:
        print("Error: File not found")
    except json.JSONDecodeError:
        print("Error: Invalid JSON")
    except ValueError as error:
        print("Error:", error)

    sys.exit(1)


def count_by(documents, key):
    counts = {}

    for document in documents:
        if not isinstance(document, dict):
            raise ValueError("Each document must be an object")

        value = document.get(key)

        if not isinstance(value, str):
            raise ValueError(f"Missing or invalid {key}")

        if value in counts:
            counts[value] += 1
        else:
            counts[value] = 1

    return counts


def main():
    if len(sys.argv) != 2:
        print("Usage: python inventory.py file_path")
        sys.exit(1)

    documents = load_inventory(sys.argv[1])

    try:
        types = count_by(documents, "document_type")
        departments = count_by(documents, "department")
    except ValueError as error:
        print("Error:", error)
        sys.exit(1)

    print("DocFlow - Document Inventory")
    print("Total documents:", len(documents))

    print("\nBy type:")
    for name in sorted(types):
        print(f"  {name}: {types[name]}")

    print("\nBy department:")
    for name in sorted(departments):
        print(f"  {name}: {departments[name]}")


if __name__ == "__main__":
    main()
