---

# Automated Job Search & Scraper

A modular Python application designed to automate the process of finding and collecting job postings from multiple online sources. It fetches job listings from APIs, scrapes the full job descriptions using a headless browser, and saves the enriched data to both CSV and JSONL files for further processing.

This project is built to be extensible, allowing new job board APIs to be easily integrated.

## Features

-   **Multi-Source Job Aggregation**: Fetches job listings from multiple APIs (currently Adzuna and Arbeitnow).
-   **Intelligent Scraping**: Uses Playwright with stealth measures to scrape full job descriptions and contact emails, bypassing common bot-detection systems.
-   **Language Filtering**: Automatically detects and filters job postings that are not in the specified language (defaults to English).
-   **Data Enrichment**: Populates a structured data model with scraped details.
-   **Robust, Streaming Exports**: Saves all collected data record-by-record into clean, timestamped CSV and JSONL files, preventing data loss on errors.
-   **Configurable & Flexible**:
    -   Secrets are managed securely via a `.env` file.
    -   Search parameters (keywords, location, language, remote-only) are provided via command-line arguments at runtime.

## Project Structure

```
.
├── api/                # API client modules (Adzuna, Arbeitnow, JobClient base class)
├── data/               # Default output directory for CSV and JSONL files
├── models/             # Data models (e.g., the Job dataclass)
├── services/           # Business logic (JobSearch, ScraperService, Writers)
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
git clone https://github.com/SageTheThird/hunter.git
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

c. **Important**: The provided `.gitignore` is already configured to ignore the `.env` file, but always double-check to ensure you never commit your secrets to a public repository.

## Usage

The application is run from the command line, providing the search query and location as arguments.

### Basic Usage

The two required arguments are `search_what` and `search_where`.

```bash
# Example: Search for Software Engineer jobs in the USA
python main.py "software engineer" "USA"
```

### Advanced Usage

You can combine flags for more specific searches.

```bash
# Example: Search for remote Data Analyst jobs in Canada, limited to English,
# and only process the first 5 results for a quick test.
python main.py "data analyst" "Canada" --remote --lang en --limit 5
```

The output CSV and JSONL files will be saved in the `data/` directory by default, with a filename like `remote_software_engineer_20250908_103000.csv`.

---

## Contributing: How to Add a New Job API

This project is designed to be easily extended with new job sources. If you want to add a new API, follow these steps to integrate it into the existing modular structure.

### Step 1: Create a New API Client

- In the `api/` directory, create a new Python file (e.g., `newapi_client.py`).
- Inside this file, create a class that inherits from the abstract base class `JobClient` (found in `api/job_client.py`).

### Step 2: Implement the `get_jobs` Method

- Your new class must implement the `get_jobs` method. This method receives `what`, `where`, and `remote_only` as arguments.
- Inside this method, write the logic to:
  1.  Authenticate with the new API (if required).
  2.  Make one or more requests to the API's search endpoint.
  3.  Implement **pagination** logic to fetch multiple pages of results.
  4.  Handle any API-specific parameters (like filtering for remote jobs).

### Step 3: Normalize the Data

- The `get_jobs` method **must** return a list of `Job` objects (imported from `models.job`).
- For each job returned by the API, you will map its fields to the fields of our internal `Job` dataclass (`title`, `company_name`, `location`, `url`). This is the most important step, as it ensures all data has a consistent format.

Here is a simple boilerplate to get you started:

```python
# in api/newapi_client.py
from models.job import Job
from .job_client import JobClient
from typing import List

class NewApiClient(JobClient):
    def get_jobs(self, what: str, where: str, remote_only: bool = False) -> List[Job]:
        all_jobs = []
        # --- Your API logic goes here ---

        # api_results = your_api.search(...)

        # for job_data in api_results:
        #     normalized_job = Job(
        #         title=job_data.get("job_title"),
        #         company_name=job_data.get("company"),
        #         location=job_data.get("job_location"),
        #         url=job_data.get("link_to_posting")
        #     )
        #     all_jobs.append(normalized_job)

        return all_jobs
```

### Step 4: Integrate Your New Client

- Finally, open `main.py`.
- Import your new client class.
- In the `main` function, instantiate your client and add the instance to the `clients` list when creating the `JobSearch` object.

```python
# in main.py
from api.newapi_client import NewApiClient # 1. Import

# ... inside main()
new_api_client = NewApiClient() # 2. Instantiate
job_search = JobSearch(clients=[adzuna_client, arbeitnow_client, new_api_client]) # 3. Add to list
```

That's it! The existing scraping and writing services will automatically work with the data provided by your new client.
