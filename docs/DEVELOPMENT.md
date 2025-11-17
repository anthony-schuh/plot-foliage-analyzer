# Development Guide

## Setup Development Environment

1. Clone the repository:
```bash
git clone <repository-url>
cd plot-foliage-analyzer
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements-dev.txt
```

## Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_plots_green.py
```

## Code Quality

Format code with Black:
```bash
black src tests
```

Lint with flake8:
```bash
flake8 src tests
```

Type checking with mypy:
```bash
mypy src
```

## Project Structure

```
plot-foliage-analyzer/
├── src/                    # Source code
│   ├── __init__.py
│   └── plots_green.py      # Main application
├── tests/                  # Unit tests
│   ├── __init__.py
│   └── test_plots_green.py
├── data/                   # Data directory
│   ├── input/              # Input images
│   ├── output/             # Processing results
│   └── sample/             # Sample data
├── docs/                   # Documentation
│   ├── USAGE.md
│   └── DEVELOPMENT.md
├── scripts/                # Utility scripts
│   ├── batch_process.sh
│   └── combine_results.py
├── config/                 # Configuration files
│   └── default_config.json
├── .github/                # GitHub workflows
│   └── workflows/
│       └── tests.yml
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── setup.py               # Package setup
├── pytest.ini             # Test configuration
├── .gitignore
└── README.md
```

## Adding New Features

1. Create feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Write tests first (TDD)
3. Implement feature
4. Run tests and linting
5. Update documentation
6. Submit pull request

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Ensure all tests pass
5. Submit pull request with description

## Release Process

1. Update version in `setup.py` and `src/__init__.py`
2. Update CHANGELOG.md
3. Create git tag: `git tag v0.1.0`
4. Push tag: `git push origin v0.1.0`
5. Build and publish: `python setup.py sdist bdist_wheel`
