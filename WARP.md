# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

- Repository: countryflag (Python package + CLI)
- Primary tools: setuptools (PEP 517), tox, pytest, black, isort, flake8, mypy, sphinx
- Entry point: countryflag (maps to countryflag.cli.main:main)

Commands
- Environment setup
  - Create venv and install dev extras
    - python -m venv .venv && source .venv/bin/activate
    - python -m pip install --upgrade pip
    - pip install -e .[dev]
  - Optional: install test/docs extras only
    - pip install -e .[test]
    - pip install -e .[docs]
  - Pre-commit
    - pre-commit install
    - pre-commit run --all-files

- Test
  - Full test suite (pytest directly; coverage configured via pytest.ini/pyproject)
    - pytest
  - Full test suite (matrix and env parity with CI)
    - tox
  - Single file / single test
    - pytest tests/test_cli.py
    - pytest tests/test_cli.py::test_help
  - By marker (see pytest.ini markers: unit, integration, performance, property, slow, plugin, cache, cli, e2e)
    - pytest -m unit
    - pytest -m "not slow"

- Lint, format, type-check (respect user’s rule: only project files, exclude venv/deps)
  - Format
    - black src tests benchmarks examples
    - isort src tests benchmarks examples
  - Lint (flake8 config lives in tox.ini)
    - flake8 src tests
  - Type-check (strict settings in pyproject.toml; additional mypy.ini tweaks)
    - mypy src
  - Tox targets used by CI
    - tox -e flake8,mypy

- Build and install
  - PEP 517 build
    - python -m build
  - Install built wheel then smoke tests (mirrors CI “build-test” job)
    - pip install dist/*.whl
    - pytest tests/test_cli.py tests/unit/test_core.py
  - End-to-end via tox (runs PEP 517 install for testenv)
    - tox

- Docs
  - Build Sphinx HTML
    - tox -e docs
  - Output at docs/build/html

- Benchmarks and examples
  - Benchmarks (shell wrapper)
    - bash scripts/run_benchmarks.sh
  - Python benchmark harness
    - python benchmarks/run_benchmarks.py
  - Timing example
    - python examples/example_timing_test.py

High-level architecture
- Package layout (src/countryflag)
  - cli/
    - main.py: CLI entrypoint (exposed as console_script "countryflag"). Handles parsing of flags: --countries/--file/--files, --reverse, --region, --format (text/json/csv), --separator, --fuzzy/--threshold, --language, --interactive, --list-countries/--list-regions, --validate, concurrency flags, verbosity, caching toggles. Delegates to core API and utils.
  - core/
    - CountryFlag domain logic lives here (CountryFlag class exposed via countryflag.core). Key responsibilities:
      - Input normalization and alias handling
      - Conversion country→flag and reverse lookup
      - Region grouping and filtering
      - Integrates caching layer
      - Surfaces convenience API used by CLI and Python users: get_flag, get_flags_by_region, reverse_lookup, clear_global_cache
    - converters.py: normalization and mapping helpers (country names ↔ codes ↔ emoji). Uses external deps: country_converter and emoji-country-flag.
    - models.py, exceptions.py: typed data models and error taxonomy for robust API surface.
  - cache/
    - base.py defines cache protocol/abstract base.
    - memory.py and disk.py provide concrete caches. Project uses a global shared cache by default for instance-to-instance reuse; CountryFlag.clear_global_cache() resets shared state (important for tests).
  - plugins/
    - base.py defines extension interfaces. Examples of custom plugin implementations live under examples/plugins (e.g., custom_cache_plugin, custom_data_source_plugin, custom_output_format_plugin). Plugin discovery is explicit (import and pass into CountryFlag/CLI); there is no implicit auto-discovery in this repo.
  - utils/
    - io.py: file input helpers including async (process_file_input_async) for large files.
    - text.py, validation.py, suppress.py: normalization, validation, and utility context managers.
  - __main__.py: allows python -m countryflag invocation.
  - lookup.py, core/flag.py: mapping orchestration and emoji rendering helpers.

- Cross-cutting support files
  - platform_timing_logic.py: encapsulates OS-specific timing thresholds used by performance/stress tests to keep CI reliable across Windows/macOS/Linux.
  - pyproject.toml: authoritative config for build, tools (black/isort/pytest/mypy/coverage), entry points, extras.
  - tox.ini: defines test, lint, docs, and build envs; CI drives tox so local tox runs mirror CI.
  - mypy.ini: complements tool.mypy in pyproject with pathing, ignores for third-party stubs, and targeted ignores for specific modules (temporary exceptions noted for core.converters and cli.main).
  - pytest.ini: markers and coverage defaults; tests live under tests/ with unit, property-based, performance, stress groupings.
  - .pre-commit-config.yaml: standard hooks plus black/isort/flake8/mypy/bandit; use pre-commit run --all-files before commits.

CI/CD and quality gates
- GitHub Actions uses tox for parity:
  - test job: tox across py39–py312 on Ubuntu/macOS/Windows; uploads coverage.xml to Codecov.
  - lint job: tox -e flake8,mypy.
  - docs job: tox -e docs and uploads artifact.
  - build-test job: python -m build → pip install wheel → targeted pytest run, via tox -e build.
- Publish workflow builds with python -m build and uploads via twine on release creation.

Important behavioral notes
- Coverage is configured via pytest addopts; running pytest at repo root generates coverage.xml for CI.
- Formatting: Follow project rule to only format project files (src, tests, examples, benchmarks). Do not touch venv/, dist/, build/, .tox/.
- Global cache: tests rely on deterministic behavior; use CountryFlag.clear_global_cache() to reset shared cache between cases when needed.
- Windows vs Unix timing: performance/stress thresholds differ; see platform_timing_logic.py and docs/README_TIMING_LOGIC.md.

Pointers to docs
- README.md: user-facing usage (CLI and Python API) and caching examples, including global cache sharing semantics.
- docs/PROJECT_SUMMARY.md: quick status, commands, and recent changes; useful orientation for new sessions.
- docs/README_TIMING_LOGIC.md and platform_timing_logic.py: background and implementation for timing thresholds.

