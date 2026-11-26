"""Area 6: command-line behaviour, exit codes and file safety.

Regression tests for Task 2.1 are named test_regression_bug_* and map to docs/debugging-log.md.

الهدف: نشغّل البرنامج كامل من التيرمنال ونتأكد من أكواد الخروج والرسائل.
وش نسوي: 0 = نجاح، 1 = خطأ في البيانات أو الملف، 2 = أمر مكتوب غلط (argparse).
وفي آخر الملف اختبارات regression لبلاغات تاسك 2.1:
- Bug A: --output=path لازم يعطي نفس نتيجة --output path.
- Bug B: ملف غير موجود لازم يطلع خطأ وكود خروج 1.
- Bug C: سجل خربان يعطي رسالة واضحة بدون مجاميع ناقصة.
"""

import json

import pytest

# --- successful runs exit 0 ---


def test_summary_success(run_cli, write_json, make_doc):
    result = run_cli(write_json([make_doc()]))
    assert result.returncode == 0
    assert result.stdout.startswith("DocFlow - Document Inventory\nTotal documents: 1")
    assert result.stderr == ""


def test_validate_success_lists_rejections(run_cli, write_json, make_doc):
    result = run_cli(write_json([make_doc(), make_doc(id="doc-001")]), "--validate")
    assert result.returncode == 0
    assert "Accepted: 1\nRejected: 1" in result.stdout
    assert "- Duplicate document ID" in result.stdout


def test_validate_output_writes_validation_report(run_cli, write_json, make_doc, tmp_path):
    out = tmp_path / "validation.json"
    result = run_cli(write_json([make_doc(), make_doc(size_kb=0)]), "--validate", "--output", out)
    assert result.returncode == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["rejected"][0]["index"] == 1


def test_shipped_samples_still_work(run_cli, tmp_path):
    assert run_cli("data/sample_metadata.json").returncode == 0
    assert run_cli("data/validation_sample.json", "--validate").returncode == 0
    assert run_cli("data/sample_metadata.json", "--output", tmp_path / "r.json").returncode == 0


# --- failing runs exit nonzero with a clear message ---


def test_malformed_json_fails(run_cli, tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{ invalid", encoding="utf-8")
    result = run_cli(path)
    assert result.returncode == 1
    assert result.stderr.startswith("Error:")


def test_non_array_json_fails(run_cli, write_json):
    result = run_cli(write_json({"documents": []}))
    assert result.returncode == 1
    assert "JSON must contain an array" in result.stderr


@pytest.mark.parametrize("args", [[], ["a.json", "--unknown"], ["a.json", "--output"]])
def test_bad_arguments_show_usage(run_cli, args):
    result = run_cli(*args)
    assert result.returncode == 2  # argparse usage error
    assert "usage:" in result.stderr


def test_output_cannot_overwrite_input(run_cli, write_json, make_doc):
    source = write_json([make_doc()])
    before = source.read_text(encoding="utf-8")
    result = run_cli(source, "--output", source)
    assert result.returncode == 1
    assert "Cannot overwrite the input JSON file" in result.stderr
    assert source.read_text(encoding="utf-8") == before


def test_output_cannot_be_a_directory(run_cli, write_json, make_doc, tmp_path):
    result = run_cli(write_json([make_doc()]), "--output", tmp_path)
    assert result.returncode == 1
    assert "Output path must be a file" in result.stderr


# --- REGRESSION: Task 2.1 bug reports ---


def test_regression_bug_a_output_equals_form_matches_space_form(
    run_cli, write_json, make_doc, tmp_path
):
    """Bug A: --output=path.json must behave exactly like --output path.json."""
    source = write_json([make_doc(), make_doc(id="DOC-002", size_kb=0)])
    spaced, equals = tmp_path / "spaced.json", tmp_path / "equals.json"
    r1 = run_cli(source, "--output", spaced)
    r2 = run_cli(source, f"--output={equals}")
    assert (r1.returncode, r2.returncode) == (0, 0)
    assert spaced.read_bytes() == equals.read_bytes()


def test_regression_bug_b_missing_file_exits_nonzero(run_cli, tmp_path):
    """Bug B: a missing input must print an error and exit nonzero."""
    result = run_cli(tmp_path / "does_not_exist.json")
    assert result.returncode == 1
    assert "No such file or directory" in result.stderr
    assert result.stdout == ""


@pytest.mark.parametrize(
    "field, value",
    [
        ("department", None),
        ("document_type", 5),
        ("department", ""),
    ],
)
def test_regression_bug_c_malformed_record_fails_cleanly(
    run_cli, write_json, make_doc, field, value
):
    """Bug C: one malformed record gives an actionable error and no partial totals."""
    result = run_cli(write_json([make_doc(), make_doc(**{field: value})]))
    assert result.returncode == 1
    assert f"Record at index 1 has a missing or non-string '{field}'" in result.stderr
    assert result.stdout == ""


def test_regression_bug_c_missing_key_and_non_object(run_cli, write_json, make_doc):
    """Bug C: a missing key or a non-object record is reported the same way."""
    doc = make_doc()
    del doc["department"]
    for bad in (doc, "not-an-object"):
        result = run_cli(write_json([make_doc(), bad]))
        assert result.returncode == 1
        assert "Record at index 1" in result.stderr
