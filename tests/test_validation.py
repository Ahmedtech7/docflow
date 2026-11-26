"""Area 3: metadata validation rules for a single document.

الهدف: نختبر كل قاعدة في validate_document على مستند واحد.
وش نسوي: الحقول الناقصة أو الفاضية، النوع (txt/md) والامتداد، حدود الحجم
(أكبر من 0 وأقل أو يساوي 5120)، صيغة التاريخ، والمسارات الخطيرة مثل ../
parametrize يكرر الاختبار الواحد على قيم كثيرة، عشان كذا عدد الاختبارات كبير.
"""

import pytest

from inventory import validate_document

TEXT_FIELDS = ["id", "filename", "department", "document_type", "uploaded_at", "file_path"]


def test_valid_document_has_no_errors(make_doc):
    assert validate_document(make_doc()) == []


def test_valid_md_document_has_no_errors(make_doc):
    doc = make_doc(filename="notes.md", document_type="md", file_path="data/documents/notes.md")
    assert validate_document(doc) == []


@pytest.mark.parametrize("record", ["text", 5, None, ["a"]])
def test_non_object_record_is_rejected(record):
    assert validate_document(record) == ["Document must be an object"]


@pytest.mark.parametrize("field", TEXT_FIELDS + ["size_kb"])
def test_missing_field_is_reported(make_doc, field):
    doc = make_doc()
    del doc[field]
    assert f"Missing field: {field}" in validate_document(doc)


@pytest.mark.parametrize("field", TEXT_FIELDS)
@pytest.mark.parametrize("value", ["", "   ", None, 7, True])
def test_blank_or_non_string_text_field_is_reported(make_doc, field, value):
    assert f"Invalid or blank field: {field}" in validate_document(make_doc(**{field: value}))


def test_all_errors_are_reported_together(make_doc):
    doc = make_doc(document_type="pdf", filename="x.pdf", size_kb=-1, uploaded_at="nope")
    errors = validate_document(doc)
    assert "Unsupported document type: pdf" in errors
    assert "Unsupported filename extension" in errors
    assert "Size must be between 0 and 5120 KB" in errors
    assert "Invalid ISO 8601 date-time" in errors


# --- formats and filenames ---


@pytest.mark.parametrize("doc_type", ["pdf", "docx", "TXT", "Md"])
def test_unsupported_document_type(make_doc, doc_type):
    assert f"Unsupported document type: {doc_type}" in validate_document(
        make_doc(document_type=doc_type)
    )


@pytest.mark.parametrize("filename", ["policy.pdf", "policy", "policy.TXT", "policy.txt.bak"])
def test_unsupported_filename_extension(make_doc, filename):
    assert "Unsupported filename extension" in validate_document(make_doc(filename=filename))


@pytest.mark.parametrize("doc_type, filename", [("txt", "policy.md"), ("md", "policy.txt")])
def test_filename_type_mismatch(make_doc, doc_type, filename):
    errors = validate_document(make_doc(document_type=doc_type, filename=filename))
    assert "Filename extension does not match document type" in errors


@pytest.mark.parametrize("filename", ["dir/policy.txt", "dir\\policy.txt"])
def test_filename_with_path_separator(make_doc, filename):
    assert "Invalid filename" in validate_document(make_doc(filename=filename))


# --- size boundaries: 0 < size_kb <= 5120 ---


@pytest.mark.parametrize("size", [0.1, 1, 5120, 5120.0])
def test_size_inside_bounds_is_accepted(make_doc, size):
    assert validate_document(make_doc(size_kb=size)) == []


@pytest.mark.parametrize("size", [0, -1, 5120.01, 5121])
def test_size_outside_bounds_is_rejected(make_doc, size):
    assert "Size must be between 0 and 5120 KB" in validate_document(make_doc(size_kb=size))


@pytest.mark.parametrize("size", ["24", None, True, False, [24]])
def test_size_must_be_a_number(make_doc, size):
    assert "Size must be a number" in validate_document(make_doc(size_kb=size))


# --- timestamps ---


@pytest.mark.parametrize(
    "stamp", ["2026-10-05T09:30:00", "2026-10-05T09:30:00+03:00", "2026-10-05T09:30"]
)
def test_valid_timestamp_is_accepted(make_doc, stamp):
    assert validate_document(make_doc(uploaded_at=stamp)) == []


@pytest.mark.parametrize(
    "stamp",
    ["2026-10-05", "not-a-date", "2026-13-05T09:30:00", "2026-10-05T25:00:00", "05/10/2026T09:30"],
)
def test_invalid_timestamp_is_rejected(make_doc, stamp):
    assert "Invalid ISO 8601 date-time" in validate_document(make_doc(uploaded_at=stamp))


# --- file paths ---


@pytest.mark.parametrize("path", ["data/documents/policy.txt", "data/documents/hr/policy.txt"])
def test_safe_path_is_accepted(make_doc, path):
    assert validate_document(make_doc(file_path=path)) == []


@pytest.mark.parametrize(
    "path",
    [
        "../private/policy.txt",  # parent directory escape
        "data/documents/../../etc/passwd",  # traversal inside the prefix
        "/data/documents/policy.txt",  # absolute path
        "C:/data/documents/policy.txt",  # drive letter
        "data\\documents\\policy.txt",  # backslashes
        "data/other/policy.txt",  # outside data/documents
        "data/documents",  # no file name
        "data/documents/",  # empty file name
    ],
)
def test_unsafe_or_invalid_path_is_rejected(make_doc, path):
    assert "Invalid file path" in validate_document(make_doc(file_path=path))
