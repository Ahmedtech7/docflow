
import json
import argparse
from datetime import datetime
from pathlib import PurePosixPath


# Read JSON inventory
def load_inventory(path):
    with open(path, "r", encoding="utf-8") as file:
        documents = json.load(file)

    if not isinstance(documents, list):
        raise ValueError("JSON must contain an array")

    return documents


# Count documents by a specific field
def count_by(documents, key):
    counts = {}

    for document in documents:
        value = document[key]
        counts[value] = counts.get(value, 0) + 1

    return counts


# Display the original inventory summary
def show_inventory(documents):
    types = count_by(documents, "document_type")
    departments = count_by(documents, "department")

    print("DocFlow - Document Inventory")
    print("Total documents:", len(documents))

    print("\nBy type:")
    for name in sorted(types):
        print(f"  {name}: {types[name]}")

    print("\nBy department:")
    for name in sorted(departments):
        print(f"  {name}: {departments[name]}")


# Validate one document
def validate_document(document):
    errors = []

    if not isinstance(document, dict):
        return ["Document must be an object"]

    text_fields = [
        "id", "filename", "department",
        "document_type", "uploaded_at", "file_path"
    ]

    required_fields = text_fields + ["size_kb"]

    for field in required_fields:
        if field not in document:
            errors.append(f"Missing field: {field}")

    for field in text_fields:
        if field in document:
            value = document[field]
            if not isinstance(value, str) or not value.strip():
                errors.append(f"Invalid or blank field: {field}")

    # Check document type
    doc_type = document.get("document_type")

    if isinstance(doc_type, str) and doc_type.strip():
        if doc_type not in ("txt", "md"):
            errors.append(f"Unsupported document type: {doc_type}")

    # Check filename extension
    filename = document.get("filename")

    if isinstance(filename, str) and filename.strip():
        if "/" in filename or "\\" in filename:
            errors.append("Invalid filename")

        extension = PurePosixPath(filename).suffix

        if extension not in (".txt", ".md"):
            errors.append("Unsupported filename extension")

        if doc_type in ("txt", "md"):
            if extension != "." + doc_type:
                errors.append("Filename extension does not match document type")

    # Check document size
    if "size_kb" in document:
        size = document["size_kb"]

        if type(size) not in (int, float):
            errors.append("Size must be a number")
        elif not 0 < size <= 5120:
            errors.append("Size must be between 0 and 5120 KB")

    # Check upload date
    uploaded_at = document.get("uploaded_at")

    if isinstance(uploaded_at, str) and uploaded_at.strip():
        try:
            if "T" not in uploaded_at:
                raise ValueError("Missing time")

            datetime.fromisoformat(uploaded_at)
        except ValueError:
            errors.append("Invalid ISO 8601 date-time")

    # Check file path
    file_path = document.get("file_path")

    if isinstance(file_path, str) and file_path.strip():
        parts = file_path.split("/")

        if (
            "\\" in file_path
            or ".." in parts
            or parts[:2] != ["data", "documents"]
            or len(parts) < 3
            or not parts[-1]
            or file_path.startswith("/")
            or ":" in parts[0]
        ):
            errors.append("Invalid file path")

    return errors


# Validate all documents
def validate_inventory(documents):
    accepted = []
    rejected = []
    accepted_ids = set()

    for index, document in enumerate(documents):
        errors = validate_document(document)

        doc_id = None

        if isinstance(document, dict):
            value = document.get("id")

            if isinstance(value, str) and value.strip():
                doc_id = value.strip().lower()

                if doc_id in accepted_ids:
                    errors.append("Duplicate document ID")

        if errors:
            rejected.append((index, doc_id, errors))
        else:
            accepted.append(document)
            accepted_ids.add(doc_id)

    return accepted, rejected


# Display validation results
def show_validation(documents):
    accepted, rejected = validate_inventory(documents)

    print("DocFlow - Document Validation")
    print("Documents inspected:", len(documents))
    print("Accepted:", len(accepted))
    print("Rejected:", len(rejected))

    for index, doc_id, errors in rejected:
        print(f"\nRejected record at index {index} ({doc_id or 'Unknown'}):")

        for error in errors:
            print(f"- {error}")


# Main program
def main():
    parser = argparse.ArgumentParser(description="DocFlow Utility")
    parser.add_argument("file_path", help="Path to JSON file")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate document metadata"
    )

    args = parser.parse_args()

    try:
        documents = load_inventory(args.file_path)

        if args.validate:
            show_validation(documents)
        else:
            show_inventory(documents)

    except (OSError, ValueError, json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
