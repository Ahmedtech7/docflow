# DocFlow Task 2.1 — Debugging Log

All inputs are small synthetic files. Tests: `python3 -m unittest discover -s tests -v`.

## Bug A — `--output=file.json` vs `--output file.json`

- **Symptom:** `python3 inventory.py data/sample_metadata.json --output=reports/check.json`
- **Expected vs actual:** Expected the same report and exit status as the space form. Actual on this branch: both forms print `Report saved to: ...`, exit 0, and the two files are byte-identical (`cmp` reports no difference).
- **Investigation:** Read `main()` in `inventory.py`. Options are parsed with `argparse`, which accepts both forms. There is a single `args.output` code path. Checked git history: no earlier commit parses `--output` by hand.
- **Root cause:** Not reproducible on this code. A hand-written `sys.argv` parser would only recognise the space form, but none exists here.
- **Fix and verification:** No code change. Added `test_regression_bug_a_output_equals_form_matches_space_form` (`tests/test_cli.py`) as a regression guard. It passes.

## Bug B — Missing input file appears successful

- **Symptom:** `python3 inventory.py data/does_not_exist.json`
- **Expected vs actual:** Expected an error message and nonzero exit. Actual: `Error: [Errno 2] No such file or directory: ...` on stderr, `echo $?` prints `1`.
- **Investigation:** `main()` wraps the work in `try/except (OSError, ValueError, KeyError, TypeError)`, prints to stderr and calls `sys.exit(1)`. Success paths fall through, exit 0.
- **Root cause:** Not reproducible on this code. The report likely describes a version that printed the error without exiting nonzero.
- **Fix and verification:** No code change. Added `test_regression_bug_b_missing_file_exits_nonzero` (`tests/test_cli.py`). It passes.
- **Remaining limitation:** `json.JSONDecodeError` is a `ValueError`, so it is covered. Other exception types would produce a traceback (still nonzero).

## Bug C — One malformed record breaks the inventory summary

- **Symptom:** a file where one record has `"department": null`, a non-string `document_type`, or no `department` key, then `python3 inventory.py bad.json`.
- **Expected vs actual:** Expected a defined policy and an actionable message. Actual (before): a `Total documents: 3` / `By type:` header printed, then `Error: '<' not supported between instances of 'int' and 'str'` (exit 1). A missing key gave a bare `KeyError`-style message such as `'department'`. Partial output plus a cryptic message.
- **Investigation:** Traced the failure to `count_by()`. It does `document[key]` without checking the value. A `None` or `int` value became a dict key, and `sorted()` in `show_inventory` then failed on mixed types. A missing key raised `KeyError`, and a non-object record raised `TypeError`. Ruled out `validate_inventory`, which already handles all of these. `--output` reports already work because `ReportBuilder` counts only accepted records.
- **Root cause:** `count_by()` (used by `show_inventory`) trusts record shape that only `validate_inventory` checks.
- **Fix:** `count_by()` now raises `ValueError("Record at index N has a missing or non-string '<key>'. ... run with --validate ...")`. `main()` already turns this into `Error: ...` on stderr and exit 1. The check runs before any printing, so no misleading totals appear.
- **Policy chosen:** the plain summary **fails cleanly**. A partial summary would silently drop records from the totals. `--validate` and `--output` reports are the partial-with-rejections path: they list every rejected record and count only accepted ones.
- **Verification:** `test_regression_bug_c_malformed_record_fails_cleanly` and `test_regression_bug_c_missing_key_and_non_object` (`tests/test_cli.py`) cover null, wrong type, missing key and non-object records (exit 1, message names the index, empty stdout). `test_blank_or_non_string_text_field_is_reported` (`tests/test_validation.py`) and `test_shipped_samples_still_work` (`tests/test_cli.py`) confirm validation and the normal summary still work.
- **Remaining limitation:** only the first bad record is named. Use `--validate` for the full list.
