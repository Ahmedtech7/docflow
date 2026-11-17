
import json
import argparse
import sys
import os
import tempfile
from pathlib import Path

from inventory import (
    load_inventory,
    count_by,
    validate_inventory,
    show_inventory,
    show_validation
)


class ReportBuilder:

    def inventory_report(self, documents):
        return {
            "summary": {
                "total_documents": len(documents)
            },
            "by_type": count_by(documents, "document_type"),
            "by_department": count_by(documents, "department")
        }

    def validation_report(self, documents):
        accepted, rejected = validate_inventory(documents)

        rejected_records = []

        for index, doc_id, errors in rejected:
            document = documents[index]

            original_id = None

            if isinstance(document, dict):
                original_id = document.get("id")

            rejected_records.append({
                "index": index,
                "id": original_id,
                "reasons": errors
            })

        return {
            "summary": {
                "total_documents": len(documents),
                "accepted_documents": len(accepted),
                "rejected_documents": len(rejected)
            },
            "rejected": rejected_records
        }


class ReportWriter:

    def save(self, report, input_path, output_path):
        source = Path(input_path).resolve()
        destination = Path(output_path).resolve()

        if source == destination:
            raise ValueError(
                "Cannot overwrite the input JSON file"
            )

        if destination.exists() and destination.is_dir():
            raise ValueError(
                "Output path must be a file"
            )

        # Prepare valid JSON before writing
        content = json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
            allow_nan=False
        )

        # Create the output directory if needed
        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Write to a temporary file first
        temporary_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=destination.parent,
                prefix=".docflow_",
                suffix=".tmp",
                delete=False
            ) as file:
                temporary_path = Path(file.name)
                file.write(content)
                file.write("\n")

            # Replace the output only after writing succeeds
            os.replace(temporary_path, destination)

        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

        print(f"Report saved to: {destination}")


def main():
    parser = argparse.ArgumentParser(
        description="DocFlow Reporting CLI"
    )

    parser.add_argument(
        "file_path",
        help="Path to the input JSON inventory"
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate document metadata"
    )

    parser.add_argument(
        "--output",
        help="Save the selected report as JSON"
    )

    args = parser.parse_args()

    try:
        # Prevent overwriting input
        if args.output:
            source = Path(args.file_path).resolve()
            destination = Path(args.output).resolve()

            if source == destination:
                raise ValueError(
                    "Cannot overwrite the input JSON file"
                )

        documents = load_inventory(args.file_path)

        if args.output:
            builder = ReportBuilder()
            writer = ReportWriter()

            if args.validate:
                report = builder.validation_report(documents)
            else:
                report = builder.inventory_report(documents)

            writer.save(
                report,
                args.file_path,
                args.output
            )

        elif args.validate:
            show_validation(documents)

        else:
            show_inventory(documents)

    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        json.JSONDecodeError
    ) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
