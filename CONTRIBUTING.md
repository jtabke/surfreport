# Contributing to surfreport

## Getting Started

Before contributing, please familiarize yourself with the project:

- **Read the README**: Check [README.md](README.md) for an overview of the project, its purpose, and usage instructions.
- **Review the Codebase**: Explore the `src/surf_report/` directory to understand the structure, including the main CLI logic (`main.py`), Surfline API integration (`providers/surfline/`), and utility functions (`utils/`).

## Development Setup

To set up the project for development:

1. **Clone the Repository**:

   ```sh
   git clone https://github.com/jtabke/surfreport.git
   cd surfreport
   ```

2. **Install Python**: Ensure you have Python 3.10 or higher installed, as specified in `pyproject.toml`.

3. **Install Dependencies**:
   Install the package with development dependencies:

   ```sh
   pip install -e ".[dev]"
   ```

   This installs the required dependencies (`requests`) and development tools (`ruff`, `pyright`).

4. **Verify Setup**:
   Run the CLI to ensure the setup is correct:

   ```sh
   surfreport --help
   ```

5. **Set Up Linting**:
   The project uses `ruff` for linting and `pyright` for static type checking. Verify they work:
   ```sh
   ruff check .
   pyright
   ```

## Coding Guidelines

To maintain consistency and quality, please adhere to the following guidelines:

- **Code Style**:
  - Follow PEP 8 for Python code style.
  - Use `ruff` for linting and import sorting (configured in `pyproject.toml` with `extend-select = ["I"]`).
  - Ensure type hints are used, as `pyright` is used for static type checking.

- **File Structure**:
  - Place provider-specific code (e.g., Surfline API logic) in `src/surf_report/providers/<provider>/`.
  - Add utility functions to `src/surf_report/utils/`.
  - Update `main.py` for CLI-related changes and `ui.py` for display logic.

- **Logging**:
  - Use the logger from `src/surf_report/utils/logger.py` for consistent logging.
  - Log debug information for API calls and errors, as shown in `surfline.py`.

- **Commit Messages**:
  - Follow the [Conventional Commits](https://www.conventionalcommits.org/) format, enforced by `commitizen` (configured in `pyproject.toml`).
  - Example: `feat: add support for new surf report provider`.

- **Documentation**:
  - Update `README.md` for new features or usage changes.
  - Maintain the `CHANGELOG.md` using `commitizen` to automate version bumps and changelog updates.
  - Add docstrings to new functions and classes, following the style in `models.py` and `helpers.py`.

## Submitting Changes

1. **Create a Branch**:
   Create a branch for your changes:

   ```sh
   git checkout -b feat/your-feature-name
   ```

2. **Make Changes**:
   Implement your feature or bug fix, ensuring adherence to the coding guidelines.

3. **Run Linters and Type Checkers**:
   Before committing, verify your code:

   ```sh
   ruff check .
   pyright
   ```

4. **Commit Changes**:
   Use `commitizen` to create a standardized commit message:

   ```sh
   cz commit
   ```

5. **Push and Create a Pull Request**:
   Push your branch and open a pull request (PR) against the `main` branch:

   ```sh
   git push origin feat/your-feature-name
   ```

   - Ensure your PR description explains the changes and references any related issues.
   - The GitHub Actions workflow (`lint.yml`) will run `ruff` and `pyright` on your PR.

6. **Code Review**:
   Respond to feedback from maintainers. Once approved, your changes will be merged.

## Testing

- **Manual Testing**:
  Test the CLI by running `surfreport` with various options:

  ```sh
  surfreport -s "Huntington State Beach"
  surfreport --days 5
  ```

  Verify that search results, region navigation, and forecast displays work as expected.

- **Automated Testing**:
  Run the pytest suite locally before raising a PR:

  ```sh
  uv pip install -e ".[dev]"  # Installs requests + ruff + pyright + pytest
  uv run pytest -q
  ```

  The suite includes provider, processing, and CLI coverage with mocked Surfline payloads. Add or update fixtures under `tests/fixtures/surfline/` when modifying API contracts.

- **API Testing**:
  When modifying `surfline.py`, test against the Surfline API endpoints listed in `Endpoints(Enum)`. Mock API responses for consistent testing if possible.

## Release Process

- **Bump version and changelog locally**:
  Use Commitizen to update `pyproject.toml` and `CHANGELOG.md`, which also creates the git tag (e.g., `cz bump --changelog`).
- **Push commits and tags**:
  After reviewing the changes, run `git push origin <branch> --follow-tags` so the semantic tag (format `X.Y.Z`) reaches GitHub.
- **Automated publish**:
  Tag pushes trigger the `Publish Release` workflow, which verifies the changelog entry, extracts the matching section for GitHub release notes, builds the distributions with `uv`, and publishes to PyPI via the trusted publisher configuration. No manual uploading is required as long as the changelog contains a matching `## X.Y.Z` heading.

## Roadmap and Feature Ideas

The project’s roadmap (from `README.md`) includes:

- **CLI Enhancements**: Improving the command-line interface and adding more data sources.
- **TUI Development**: Building a Text User Interface for visual surf condition representation.

Consider contributing to:

- New providers in `src/surf_report/providers/` (e.g., or NOAA APIs).
- Enhanced data visualization in `ui.py` (e.g., ASCII charts for wave heights).
- Performance optimizations for API calls in `surfline.py`.
- Automated tests to ensure reliability.

Check the [GitHub Issues](https://github.com/jtabke/surfreport/issues) for open tasks or propose new features.

## Community and Support

- **Report Bugs**: Open an issue on [GitHub](https://github.com/jtabke/surfreport/issues) with a clear description and steps to reproduce.
- **Discuss Features**: Share ideas in the issue tracker or discussions.
- **Stay Updated**: Follow the repository for updates and check `CHANGELOG.md` for recent changes.

Thank you for contributing to `surfreport`! Your efforts help make surf forecasting more accessible from the terminal.
