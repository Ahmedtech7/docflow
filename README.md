# DocFlow — Document Inventory Utility

A Python command-line utility that reads a local JSON document inventory and reports the total number of records, document counts by file type, and document counts by department.

## Requirements

- Python 3 (standard library only; no installation of external packages needed)

## Run

From the project root directory:

```bash
python3 inventory.py data/sample_metadata.json
```

On systems where `python` invokes Python 3, this also works:

```bash
python inventory.py data/sample_metadata.json
```

Pass a different local inventory file as the argument if needed.

## Example output

```text
DocFlow - Document Inventory
Total documents: 2

By type:
  md: 1
  txt: 1

By department:
  Finance: 1
  HR: 1
```

## Input format

The JSON file must contain a top-level array of document objects. Each document must have string fields named `document_type` and `department`. Other metadata fields, such as `id`, `filename`, `size_kb`, `uploaded_at`, and `file_path`, are allowed but are not used for counting. Every record is counted once, even if IDs are repeated. All file types are counted, including formats not otherwise supported by DocFlow.

## Error handling

The utility shows useful errors and exits with a nonzero status when an input file does not exist, is malformed JSON, has a non-array root, or has malformed document records. An empty array produces `Total documents: 0` and empty group sections.

## Verify

From the project root:

```bash
python3 inventory.py data/sample_metadata.json
python3 inventory.py data/does_not_exist.json
```

For further checks, create a temporary local JSON file containing `[]`, another containing `{}`, and another containing `{ invalid }`, then run each through the same command. Missing/invalid inputs should print an error and exit unsuccessfully; the empty array should print a zero-document summary.

The utility only reads inventory files and never modifies them.


## Task 1.2 - Document Validation

DocFlow now supports document metadata validation.

### Run Inventory (Task 1.1)

```bash
python3 inventory.py data/sample_metadata.json
```

### Run Validation (Task 1.2)

```bash
python3 inventory.py --validate data/validation_sample.json
```

### Validation Rules

- All seven required fields must be present.
- Text fields must contain non-empty strings.
- Document IDs must be unique (case-insensitive).
- Only txt and md file types are supported.
- Filename extensions must match document types.
- File size must be greater than 0 and at most 5120 KB.
- Upload dates must be valid ISO 8601 date-times.
- File paths must be relative and within data/documents/.
- Every applicable rejection reason is reported.

### Example Validation Output

```text
DocFlow - Document Validation
Documents inspected: 5
Accepted: 2
Rejected: 3
```

### Notes

Validation only checks metadata. It does not check whether document files exist.




## Task 1.3 — Reporting CLI

Task 1.3 adds JSON report export using `reporting.py`.

The reporting utility reuses the inventory and validation
functions from `inventory.py` without duplicating them.

### Display inventory

```bash
python3 reporting.py data/sample_metadata.json
```

### Validate documents

```bash
python3 reporting.py data/validation_sample.json --validate
```

### Export inventory report

```bash
python3 reporting.py data/sample_metadata.json --output reports/inventory.json
```

### Export validation report

```bash
python3 reporting.py data/validation_sample.json --validate --output reports/validation.json
```

### Help

```bash
python3 reporting.py --help
```

### Report contents

Inventory reports include total documents and counts by type
and department.

Validation reports include total, accepted, and rejected
document counts, plus each rejected record's index, ID,
and rejection reasons.

### Error handling

The reporting utility prevents overwriting the input JSON
file and returns a nonzero exit code when an error occurs.



## Task 2.2 — Automated Tests

The test suite uses [pytest](https://docs.pytest.org/) and synthetic data only.

### Setup

Dependencies are managed with [uv](https://docs.astral.sh/uv/). pytest is in the `dev` dependency group in `pyproject.toml`, and exact versions are locked in `uv.lock`.

```bash
uv sync
```

### Run

From the repository root:

```bash
uv run pytest
```

Add `-v` to see each test name. Configuration lives in `pytest.ini`.

### What is covered

| File | Area |
|---|---|
| `tests/test_loading.py` | Valid, empty, missing, malformed and non-array JSON |
| `tests/test_summary.py` | Totals and counts by type and department; malformed records |
| `tests/test_validation.py` | Every metadata rule, including size and path boundaries |
| `tests/test_duplicates.py` | Case-insensitive duplicate IDs and accepted/rejected totals |
| `tests/test_reports.py` | Report structure, counts, rejection details, deterministic output, safe saving |
| `tests/test_cli.py` | Exit codes, `--output` forms, overwrite protection, error messages |

Tests named `test_regression_bug_a/b/c_*` protect the Task 2.1 fixes described in `docs/debugging-log.md`.

Every test writes to its own temporary folder, so the suite does not change files in `data/` or `reports/`, and it can run repeatedly in any order.

## Task 2.3 — Docker

Run DocFlow and its tests without installing Python or pytest on your machine. You only need **Docker**.

### Build the image

```bash
docker build -t docflow .
```

### Run the tests

```bash
docker run --rm docflow python -m pytest
```

All 140 tests run inside the container, including the Task 2.1 regression tests.

### Run the CLI

Inventory summary of the sample data (the image's default command):

```bash
docker run --rm docflow
```

Inventory or validation of a file from your machine:

```bash
docker run --rm -v "$PWD/data:/app/data:ro" docflow python inventory.py data/sample_metadata.json
docker run --rm -v "$PWD/data:/app/data:ro" docflow python inventory.py data/validation_sample.json --validate
```

### Example: validate an inventory and export a report to the host

```bash
mkdir -p reports
docker run --rm \
  --user "$(id -u):$(id -g)" \
  -v "$PWD/data:/app/data:ro" \
  -v "$PWD/reports:/app/reports" \
  docflow python inventory.py data/validation_sample.json --validate --output reports/validation_report.json
cat reports/validation_report.json
```

The CLI prints `Report saved to: /app/reports/validation_report.json`. That is the path inside the container, and it is the same file as `reports/validation_report.json` on your machine.

To use your own inventory, put the file in `data/` and pass its path.

### How files move between the host and the container

| Host folder | Container folder | Mode | Why |
|---|---|---|---|
| `data/` | `/app/data` | read-only (`:ro`) | the container reads your input files; it cannot change them |
| `reports/` | `/app/reports` | read-write | reports are written to your machine |

`--rm` deletes each container when it exits. Reports survive because they are written to the mounted host folder, not inside the container. `--user` writes report files as your host user instead of root.

The test command mounts nothing. It tests the code copied into the image, and every test writes only to its own temporary folder.

### Image details

- Base image: `python:3.14-slim`, the same Python version used locally.
- Working directory: `/app`, so relative paths such as `data/` and `tests/` work exactly as they do locally.
- Dependencies are installed with uv from `pyproject.toml` and `uv.lock` into `/app/.venv`, which is on `PATH`.
- Runs as a non-root user.
- `.dockerignore` keeps git data, caches, virtual environments, generated reports and secret files out of the image.

### Dependency versions

Dependencies are managed with uv:

- The application uses only the Python standard library, so `dependencies` in `pyproject.toml` is empty.
- pytest is in the `dev` dependency group: `pytest==9.0.3`.
- `uv.lock` pins the exact version of every package, including pytest's own dependencies.
- The image installs them with `uv sync --frozen`, which fails the build if `uv.lock` does not match `pyproject.toml`, so every build gets the same versions.
- The uv binary itself is pinned to `0.13.8` in the `Dockerfile`.

To upgrade pytest, change the version in `pyproject.toml`, run `uv lock`, and rebuild the image.

### Exit codes

`docker run` returns the exit code of the command inside the container:

- A missing or invalid input file prints `Error: ...` and exits with 1.
- A failing test makes `pytest` exit with 1.

Check it with `echo $?` after any command.

### Troubleshooting

- `Cannot connect to the Docker daemon`: start Docker Desktop and retry.
- `docker-credential-desktop: executable file not found` (macOS): add Docker's tools to your PATH:

  ```bash
  export PATH="$PATH:/Applications/Docker.app/Contents/Resources/bin"
  ```
