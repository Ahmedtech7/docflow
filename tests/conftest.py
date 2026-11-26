"""Shared fixtures. Every test gets fresh synthetic data in its own tmp_path.

الهدف: أدوات مشتركة تستخدمها كل ملفات الاختبار، عشان ما نكرر نفس الكود.
وش نسوي:
- make_doc: يعطي مستند سليم، ونغيّر فيه الحقل اللي نبي نختبره بس.
- write_json: يكتب البيانات في ملف JSON داخل مجلد مؤقت (tmp_path) ينحذف بعد الاختبار.
- run_cli: يشغّل inventory.py كأنه من التيرمنال، ويرجع كود الخروج و stdout و stderr.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def make_doc():
    """Return a valid document; keyword arguments override fields."""

    def _make(**overrides):
        doc = {
            "id": "DOC-001",
            "filename": "policy.txt",
            "department": "HR",
            "document_type": "txt",
            "size_kb": 24,
            "uploaded_at": "2026-10-05T09:30:00",
            "file_path": "data/documents/policy.txt",
        }
        doc.update(overrides)
        return doc

    return _make


@pytest.fixture
def write_json(tmp_path):
    """Write data as JSON into tmp_path and return the file path."""

    def _write(data, name="inventory.json"):
        path = tmp_path / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    return _write


@pytest.fixture
def run_cli():
    """Run inventory.py as a user would and return the CompletedProcess."""

    def _run(*args):
        return subprocess.run(
            [sys.executable, "inventory.py", *map(str, args)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    return _run
