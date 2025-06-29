# UC Berkeley Transfer Equivalency Reverse Search

This project was originally forked from [ccc_transfers](https://github.com/jacobtbigham/ccc_transfers). Many thanks to Jacob Bigham for creating this foundational tool!

## Project Overview

[Assist.org](https://www.assist.org) is an essential resource for UC Berkeley students, providing officially approved course equivalencies between California Community Colleges (CCCs) and UC/CSU systems. However, the site only allows searching one CCC-to-UC articulation agreement at a time, making it tedious to find equivalent courses across **100+** articulation agreements.This project aims to remedy this issue by retrieving all articulated courses for a specific UC course across multiple community colleges at once.

### The Problem

Previously, accessing articulation data required:

- Manually downloading PDFs for each agreement
- Complex text extraction and parsing
- Dealing with inconsistent formatting across agreements

### Our Solution

We've developed a modern approach that bypasses PDF processing entirely by intercepting ASSIST's internal API calls. When you visit an articulation agreement on ASSIST's website, the site makes API calls in the background to fetch JSON data. Our tool intercepts these API responses to directly access the structured articulation data.

## Setup & Installation

### Prerequisites

This project uses [uv](https://docs.astral.sh/uv/) for Python package management. If you don't have uv installed:

```bash
# Install uv (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via homebrew (macOS)
brew install uv

# Or via pip
pip install uv
```

### Project Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd berkeley-equivalency
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Install Playwright browsers** (required for web scraping)

   ```bash
   uv run playwright install
   ```

## Development Workflow

### Running Scripts

Execute Python scripts using uv:

```bash
# Run a specific script
uv run python src/scraper.py

# Run with arguments
uv run python src/get_institution_id.py --help
```

### Testing

Run tests using pytest:

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_scraper.py

# Run with verbose output
uv run pytest -v
```

### Code Quality

Lint your code using ruff:

```bash
# Check for linting issues
uv run ruff check

# Auto-fix issues where possible
uv run ruff check --fix

# Format code
uv run ruff format
```

### Jupyter Notebook Development

For data exploration and iterative development, use the included `explore.ipynb` notebook.

**Recommended Setup for Notebooks:**

- Use conda environments for Jupyter notebook development
- Install required packages in your conda environment:

```bash
# Create conda environment
conda create -n berkeley-transfer python=3.11
conda activate berkeley-transfer

# Install required packages
conda install jupyter beautifulsoup4 requests
pip install playwright
playwright install
```

**Required packages for notebook:**

- `beautifulsoup4` (bs4) - HTML parsing
- `playwright` - Browser automation for web scraping  
- `requests` - HTTP requests
- `json` - JSON data handling

## Project Structure

```text
├── src/                    # Main source code
│   ├── scraper.py         # Core scraping functionality
│   ├── parse_json.py      # JSON data parsing
│   ├── get_institution_id.py  # Institution ID utilities
│   └── json_grabber.py    # API data extraction
├── tests/                 # Test suite
├── data/                  # Data files
├── docs/                  # Documentation and examples
├── explore.ipynb          # Jupyter notebook for development
└── pyproject.toml         # Project configuration
```

## How It Works

### Modern API Interception Approach

Instead of parsing PDFs, our system:

1. **Identifies Target Agreements**: Uses institution IDs and program codes
2. **Automated Browser Navigation**: Uses Playwright to navigate ASSIST pages
3. **API Interception**: Captures JSON responses from ASSIST's internal API calls
4. **Data Processing**: Parses structured JSON data directly
5. **Aggregation**: Combines data across multiple institutions

### Key Advantages

| Old Approach (PDFs) | New Approach (API) |
|-------------------|------------------|
| ❌ Complex text extraction | ✅ Direct JSON access |
| ❌ Formatting inconsistencies | ✅ Structured data |
| ❌ Error-prone parsing | ✅ Reliable data extraction |
| ❌ Manual PDF downloads | ✅ Automated data collection |

## Usage Examples

### Basic Usage

```python
# Get institution data
from src.get_institution_id import get_institution_id
berkeley_id = get_institution_id("UC Berkeley")

# Scrape articulation data
from src.scraper import ArticulationScraper
scraper = ArticulationScraper()
data = scraper.get_articulation_data(
    sending_institution="Irvine Valley College",
    receiving_institution="UC Berkeley", 
    program="Data Science"
)

# Parse the results
from src.parse_json import parse_articulation_data
courses = parse_articulation_data(data)
```

### Implementation Steps

1. **Explore data structure** using `explore.ipynb`
2. **Write/modify scraping logic** in `src/`
3. **Test changes** with `uv run pytest`
4. **Lint code** with `uv run ruff check`
5. **Iterate** until desired functionality is achieved

## Contributing

1. Set up the development environment as described above
2. Make your changes
3. Run tests: `uv run pytest`
4. Check code quality: `uv run ruff check`
5. Submit a pull request

## Useful Resources

- [ASSIST.org](https://www.assist.org) - Original articulation agreement database
- [uv Documentation](https://docs.astral.sh/uv/) - Python package manager
- [Playwright Documentation](https://playwright.dev/python/) - Browser automation
- [Institution IDs API](https://assist.org/api/institutions) - ASSIST institution database
