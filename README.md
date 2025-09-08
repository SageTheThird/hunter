# Automated Job Search & Scraper

A modular Python application designed to automate the process of finding and collecting job postings from multiple online sources. It fetches job listings from APIs, scrapes the full job descriptions using a headless browser, and saves the enriched data to a CSV file for further processing.

## Features

- **Multi-Source Job Aggregation**: Fetches job listings from multiple APIs (currently Adzuna and Arbeitnow).
- **Intelligent Scraping**: Uses Playwright with stealth measures to scrape full job descriptions and contact emails, bypassing common bot-detection systems.
- **Data Enrichment**: Populates a structured data model with scraped details.
- **CSV Export**: Saves all collected data into a clean, timestamped CSV file.
- **Configurable & Flexible**:
  - Secrets are managed securely via a `.env` file.
  - Search parameters (keywords, location, remote-only) are provided via command-line arguments at runtime.

## Project Structure

```
.
├── api/                # API client modules (Adzuna, Arbeitnow)
├── data/               # Default output directory for CSV files
├── models/             # Data models (e.g., the Job dataclass)
├── services/           # Business logic (JobSearch, ScraperService, CSVWriter)
├── .env                # Stores secret API keys (must be created manually)
├── .gitignore          # Git ignore file
├── main.py             # Main entry point of the application
├── README.md           # This file
└── requirements.txt    # Python package dependencies
```

## Setup and Installation

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository

```bash
git https://github.com/SageTheThird/hunter
cd hunter
```

### 2. Create a Python Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install all required Python packages from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

Playwright requires downloading browser binaries for its automation.

```bash
playwright install
```

### 5. Create and Configure the `.env` File

This is a crucial step for providing your API credentials.

a. Create a file named `.env` in the root of the project directory.

b. Add your Adzuna API credentials to it. The file should look like this:

```
# .env file
ADZUNA_APP_ID="YOUR_ADZUNA_APP_ID"
ADZUNA_APP_KEY="YOUR_ADZUNA_APP_KEY"
```

c. **Important**: Add `.env` to your `.gitignore` file to ensure you never commit your secrets to a public repository.

## Usage

The application is run from the command line, providing the search query and location as arguments.

### Basic Usage

The two required arguments are `search_what` and `search_where`.

```bash
# Example: Search for Software Engineer jobs in the USA
python main.py "software engineer" "USA"
```

### Searching for Remote Jobs

To filter for remote-only jobs, add the `--remote` flag.

```bash
# Example: Search for remote Python Developer jobs
python main.py "python developer" "USA" --remote
```

### Limiting Results for Testing

During testing, you might not want to scrape all results. Use the `--limit` flag to process only the first N jobs.

```bash
# Example: Search for remote Data Analyst jobs and only scrape the first 5
python main.py "data analyst" "Canada" --remote --limit 5
```

The output CSV files will be saved in the `data/` directory by default, with a filename like `remote_software_engineer_20250908_103000.csv`.
