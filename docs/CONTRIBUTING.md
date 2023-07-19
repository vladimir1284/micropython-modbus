# Contributing

Guideline to contribute to this package

---------------

## General

You're always welcome to contribute to this package with or without raising an
issue before creating a PR.

Please follow this guideline covering all necessary steps and hints to ensure
a smooth review and contribution process.

## Code

To test and verify your changes it is recommended to run all checks locally in
a virtual environment. Use the following commands to setup and install all
tools.

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements-test.txt
```

For very old systems it might be necessary to use an older version of
`pre-commit`, an "always" working version is `1.18.3` with the drawback of not
having `flake8` and maybe other checks in place.

### Format

The Python code format is checked by `flake8` with the default line length
limit of 79. Further configuration can be found in the `.flake8` file in the
repo root.

The YAML code format is checked by `yamllint` with some small adjustments as
defined in the `.yamllint` file in the repo root.

Use the following commands (inside the virtual environment) to run the Python
and YAML checks

```bash
# check Python
flake8 .

# check YAML
yamllint .
```

### Tests

Every code should be covered by a unittest. This can be achieved for
MicroPython up to some degree, as hardware specific stuff can't be always
tested by a unittest.

For now `mpy_unittest` is used as tool of choice and runs directly on the
divice. For ease of use a Docker container is used as not always a device is
at hand or connected to the CI.

The hardware UART connection is faked by a TCP connection providing the same
interface and basic functions as a real hardware interface.

The tests are defined, as usual, in the `tests` folder. The `mpy_unittest`
takes and runs all tests defined and imported there by the `__init__.py` file.

Further tests, which could be called Integration tests, are defined in this
folder as well. To be usable they may require a counterpart e.g. a client
communicating with a host, which is simply achieved by two Docker containers,
defined in the `docker-compose-tcp-test.yaml` or `docker-compose-rtu-test.yaml`
file, located in the repo root. The examples for TCP or RTU client usage are
used to provide a static setup.

Incontrast to Python, no individual test results will be reported as parsable
XML or similar, the container will exit with either `1` in case of an error or
with `0` on success.

```bash
# build and run the "native" unittests
docker build --tag micropython-test --file Dockerfile.tests .

# Execute client/host TCP examples
docker compose up --build --exit-code-from micropython-host

# Run client/host TCP tests
docker compose -f docker-compose-tcp-test.yaml up --build --exit-code-from micropython-host

# Run client/host RTU examples with faked RTU via TCP
docker compose -f docker-compose-rtu.yaml up --build --exit-code-from micropython-host

# Run client/host RTU tests
docker compose -f docker-compose-rtu-test.yaml up --build --exit-code-from micropython-host
```

### Precommit hooks

This repo is equipped with a `.pre-commit-config.yaml` file to combine most of
the previously mentioned checks plus the changelog validation, see next
section, into one handy command. It additionally allows to automatically run
the checks on every commit.

In order to run this repo's pre commit hooks, perform the following steps

```bash
# install pre-commit to run before each commit, optionally
pre-commit install

pre-commit run --all-files
```

## Changelog

The changelog format is based on [Keep a Changelog][ref-keep-a-changelog], and
this project adheres to [Semantic Versioning][ref-semantic-versioning].

Please add a changelog entry for every PR you contribute. The versions are
seperated into `MAJOR.MINOR.PATCH`:

- Increment the major version by 1 in case you created a breaking, non
backwards compatible change which requires the user to perform additional
tasks, adopt his currently running code or in general can't be used as is anymore.
- Increment the minor version by 1 on new "features" which can be used or are
optional, but in either case do not require any changes by the user to keep
the system running after upgrading.
- Increment the patch version by 1 on bugfixes which fix an issue but can be
used out of the box, like features, without any changes by the user. In some
cases bugfixes can be breaking changes of course.

Please add the date the change has been made as well to the changelog
following the format `## [MAJOR.MINOR.PATCH] - YYYY-MM-DD`. It is not
necessary to keep this date up to date, it is just used as meta data.

The changelog entry shall be short but meaningful and can of course contain
links and references to other issues or PRs. New lines are only allowed for a
new bulletpoint entry. Usage examples or other code snippets should be placed
in the code documentation, README or the docs folder.

### General

The package version file, located at `umodbus/version.py` contains the latest
changelog version.

To avoid a manual sync of the changelog version and the package version file
content, the `changelog2version` package is used. It parses the changelog,
extracts the latest version and updates the version file.

The package version file can be generated with the following command consuming
the latest changelog entry

```bash
changelog2version \
	--changelog_file changelog.md \
	--version_file umodbus/version.py \
	--version_file_type py \
	--debug
```

To validate the existing package version file against the latest changelog
entry use this command

```bash
changelog2version \
	--changelog_file=changelog.md \
	--version_file=umodbus/version.py \
	--validate
```

### MicroPython

On MicroPython the `mip` package is used to install packages instead of `pip`
at MicroPython version 1.20.0 and newer. This utilizes a `package.json` file
in the repo root to define all files and dependencies of a package to be
downloaded by [`mip`][ref-mip-docs].

To avoid a manual sync of the changelog version and the MicroPython package
file content, the `setup2upypackage` package is used. It parses the changelog,
extracts the latest version and updates the package file version entry. It
additionally parses the `setup.py` file and adds entries for all files
contained in the package to the `urls` section and all other external
dependencies to the `deps` section.

The MicroPython package file can be generated with the following command based
on the latest changelog entry and `setup` file.

```bash
upy-package \
	--setup_file setup.py \
	--package_changelog_file changelog.md \
	--package_file package.json
```

To validate the existing package file against the latest changelog entry and
setup file content use this command

```bash
upy-package \
	--setup_file setup.py \
	--package_changelog_file changelog.md \
	--package_file package.json \
	--validate
```

## Documentation

Please check the `docs/DOCUMENTATION.md` file for further details.

<!-- Links -->
[ref-keep-a-changelog]: https://keepachangelog.com/en/1.0.0/
[ref-semantic-versioning]: https://semver.org/spec/v2.0.0.html
[ref-mip-docs]: https://docs.micropython.org/en/v1.20.0/reference/packages.html
