"""Area 5: report generation and saving.

الهدف: نتأكد إن التقرير يُبنى صح ويُحفظ بأمان.
وش نسوي: نتأكد من شكل التقرير وأرقامه، وإن نفس الإدخال يعطي نفس الملف بالضبط،
وإن العربي يبقى مقروء، وإن الحفظ ما يكتب فوق ملف الإدخال ولا يقبل مجلد بدل ملف.
"""
import json

import pytest

from reporting import ReportBuilder, ReportWriter


@pytest.fixture
def mixed_docs(make_doc):
    return [
        make_doc(id="DOC-001", department="HR"),
        make_doc(id="DOC-002", department="Finance", filename="b.md", document_type="md"),
        make_doc(id="Doc-001", department="IT"),     # duplicate of DOC-001
        make_doc(id="DOC-004", size_kb=9000),        # too large
        "not-an-object",
    ]


def test_inventory_report_structure_and_counts(mixed_docs):
    assert ReportBuilder().inventory_report(mixed_docs) == {
        "summary": {"total_records": 5, "accepted_documents": 2, "rejected_documents": 3},
        "by_type": {"txt": 1, "md": 1},
        "by_department": {"HR": 1, "Finance": 1},
    }


def test_validation_report_rejection_details(mixed_docs):
    report = ReportBuilder().validation_report(mixed_docs)
    assert report["summary"] == {"total_records": 5, "accepted_documents": 2, "rejected_documents": 3}
    assert report["rejected"] == [
        {"index": 2, "id": "Doc-001", "reasons": ["Duplicate document ID"]},   # original ID, not lowercased
        {"index": 3, "id": "DOC-004", "reasons": ["Size must be between 0 and 5120 KB"]},
        {"index": 4, "id": None, "reasons": ["Document must be an object"]},
    ]


def test_empty_inventory_report():
    report = ReportBuilder().validation_report([])
    assert report == {
        "summary": {"total_records": 0, "accepted_documents": 0, "rejected_documents": 0},
        "by_type": {}, "by_department": {}, "rejected": [],
    }


def test_saved_report_is_valid_sorted_json(tmp_path, mixed_docs):
    out = tmp_path / "report.json"
    report = ReportBuilder().validation_report(mixed_docs)
    ReportWriter().save(report, tmp_path / "input.json", out)
    text = out.read_text(encoding="utf-8")
    assert json.loads(text) == report
    assert text == json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def test_same_input_gives_byte_identical_report(tmp_path, mixed_docs):
    builder, writer = ReportBuilder(), ReportWriter()
    first, second = tmp_path / "1.json", tmp_path / "2.json"
    writer.save(builder.validation_report(mixed_docs), tmp_path / "in.json", first)
    writer.save(builder.validation_report(mixed_docs), tmp_path / "in.json", second)
    assert first.read_bytes() == second.read_bytes()


def test_arabic_text_is_kept_readable(tmp_path, make_doc):
    out = tmp_path / "r.json"
    ReportWriter().save(ReportBuilder().inventory_report([make_doc(department="الموارد")]), tmp_path / "in.json", out)
    assert "الموارد" in out.read_text(encoding="utf-8")


def test_save_creates_missing_parent_folders(tmp_path):
    out = tmp_path / "nested" / "deeper" / "r.json"
    ReportWriter().save({"a": 1}, tmp_path / "in.json", out)
    assert json.loads(out.read_text(encoding="utf-8")) == {"a": 1}


def test_save_leaves_no_temporary_files(tmp_path):
    ReportWriter().save({"a": 1}, tmp_path / "in.json", tmp_path / "r.json")
    assert sorted(p.name for p in tmp_path.iterdir()) == ["r.json"]


def test_save_refuses_to_overwrite_input(tmp_path):
    source = tmp_path / "in.json"
    source.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="Cannot overwrite the input JSON file"):
        ReportWriter().save({"a": 1}, source, tmp_path / "." / "in.json")
    assert source.read_text(encoding="utf-8") == "[]"


def test_save_refuses_directory_as_output(tmp_path):
    with pytest.raises(ValueError, match="Output path must be a file"):
        ReportWriter().save({"a": 1}, tmp_path / "in.json", tmp_path)
