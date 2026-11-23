import json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOOD = {"id": "a", "filename": "a.txt", "department": "HR", "document_type": "txt",
        "uploaded_at": "2026-01-10T10:30:00", "file_path": "data/documents/a.txt", "size_kb": 1}


def run(*args):
    return subprocess.run([sys.executable, "inventory.py", *map(str, args)],
                          cwd=ROOT, capture_output=True, text=True)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def write(self, name, data):
        path = self.tmp / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_a_output_space_and_equals_match(self):
        src = self.write("in.json", [GOOD])
        r1 = run(src, "--output", self.tmp / "1.json")
        r2 = run(src, f"--output={self.tmp / '2.json'}")
        self.assertEqual((r1.returncode, r2.returncode), (0, 0))
        self.assertEqual((self.tmp / "1.json").read_text(), (self.tmp / "2.json").read_text())

    def test_b_missing_file_exits_nonzero(self):
        r = run(self.tmp / "nope.json")
        self.assertEqual(r.returncode, 1)
        self.assertIn("Error:", r.stderr)

    def test_c_malformed_record_fails_cleanly(self):
        for bad in ({**GOOD, "department": None}, {**GOOD, "document_type": 5},
                    {k: v for k, v in GOOD.items() if k != "department"}, "not-an-object"):
            r = run(self.write("bad.json", [GOOD, bad]))
            self.assertEqual(r.returncode, 1, bad)
            self.assertIn("index 1", r.stderr)
            self.assertEqual(r.stdout, "")  # no misleading partial totals

    def test_c_validate_still_reports_malformed(self):
        r = run(self.write("bad.json", [GOOD, {**GOOD, "department": None}]), "--validate")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Rejected: 1", r.stdout)

    def test_normal_workflows(self):
        src = self.write("ok.json", [GOOD])
        self.assertEqual(run(src).returncode, 0)
        self.assertEqual(run(src, "--validate").returncode, 0)


if __name__ == "__main__":
    unittest.main()
