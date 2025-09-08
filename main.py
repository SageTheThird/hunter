import asyncio
import argparse
import os
import random
from dotenv import load_dotenv
from api.adzuna import AdzunaClient
from api.arbetnow import ArbeitnowClient
from services.job_search import JobSearch
from services.csv_writer import CSVWriter
from services.jsonl_writer import JSONLWriter
from services.scraper import ScraperService


async def main(
    search_what: str, search_where: str, remote_only: bool, test_limit: int = 0
):
    """
    Main asynchronous function to run the job search and scraping pipeline.
    """
    # --- Configuration ---
    # Load environment variables from .env file
    load_dotenv()
    ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
    ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("Error: ADZUNA_APP_ID and ADZUNA_APP_KEY must be set in the .env file.")
        return

    # --- Initialization ---
    adzuna_client = AdzunaClient(app_id=ADZUNA_APP_ID, app_key=ADZUNA_APP_KEY)
    arbeitnow_client = ArbeitnowClient()
    job_search = JobSearch(clients=[adzuna_client, arbeitnow_client])
    scraper_service = ScraperService()

    # Create a dynamic search term for the filename
    search_term_prefix = "remote_" if remote_only else ""
    search_term = f"{search_term_prefix}{search_what}"
    csv_writer = CSVWriter(search_term=search_term)
    jsonl_writer = JSONLWriter(search_term=search_term)
    writers = [csv_writer, jsonl_writer]

    # 1. Fetch the initial list of all jobs
    print(
        f"Searching for '{search_what}' jobs in '{search_where}' (Remote: {remote_only})..."
    )
    initial_jobs = job_search.search(
        what=search_what, where=search_where, remote_only=remote_only
    )

    if not initial_jobs:
        print("No jobs found from APIs. Exiting.")
        return

    if test_limit > 0:
        initial_jobs = initial_jobs[:test_limit]

    print(f"Found {len(initial_jobs)} jobs. Starting scraping and saving process...")

    # 2. Loop through each job, enrich it, and save it immediately
    for index, job in enumerate(initial_jobs):
        print(f"--- Processing job {index + 1}/{len(initial_jobs)} ---")

        enriched_job = await scraper_service.enrich_job(job)

        if enriched_job:
            # Save the result to all configured writers
            for writer in writers:
                writer.append_job(enriched_job)

        # Add a small, respectful delay between scraping individual jobs
        if index < len(initial_jobs) - 1:
            await asyncio.sleep(random.uniform(1, 3))

    print("Job search and export complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Automated Job Search and Scraper Tool"
    )
    parser.add_argument(
        "search_what",
        type=str,
        help="The job title or keyword to search for (e.g., 'software engineer').",
    )
    parser.add_argument(
        "search_where", type=str, help="The location to search in (e.g., 'USA')."
    )
    parser.add_argument(
        "--remote",
        action="store_true",
        help="Add this flag to search for remote-only jobs.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit the number of jobs to scrape for testing purposes (e.g., --limit 5).",
    )

    args = parser.parse_args()

    # Run the main asynchronous function with parsed arguments
    asyncio.run(
        main(
            search_what=args.search_what,
            search_where=args.search_where,
            remote_only=args.remote,
            test_limit=args.limit,
        )
    )
