# DocFlow developer commands.
#
#   make build          build the Docker image
#   make test           run the pytest suite in Docker
#   make inventory      inventory summary of INPUT, in Docker
#   make validate       validation summary of INPUT, in Docker
#   make report         validate INPUT and save reports/$(REPORT) on the host, in Docker
#
#   make format         format the Python files (changes files)
#   make lint           check lint rules (never changes files)
#   make format-check   check formatting (never changes files; used by CI)
#   make check          lint + format-check + test
#
# Docker targets need Docker. Ruff targets need uv and run on the host, because
# formatting must edit the files in your checkout.
#
# Override the input or report name: make report INPUT=data/validation_sample.json REPORT=my_check.json

INPUT  ?= data/sample_metadata.json
REPORT ?= validation_report.json

# --locked fails if uv.lock does not match pyproject.toml.
RUFF = uv run --locked ruff

.PHONY: build test inventory validate report format lint format-check check

build:
	docker compose build

# Docker targets rebuild first (cached, so fast) so they never test stale code.
test: build
	docker compose run --rm test

inventory: build
	docker compose run --rm inventory python inventory.py $(INPUT)

validate: build
	docker compose run --rm inventory python inventory.py $(INPUT) --validate

# --user writes the report as your host user instead of the container user.
report: build
	mkdir -p reports
	docker compose run --rm --user "$$(id -u):$$(id -g)" inventory \
		python inventory.py $(INPUT) --validate --output reports/$(REPORT)

format:
	$(RUFF) format .
	$(RUFF) check --select I --fix .

lint:
	$(RUFF) check .

format-check:
	$(RUFF) format --check --diff .

check: lint format-check test
