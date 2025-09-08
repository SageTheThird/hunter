import asyncio
import random
import re
from typing import List
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
    Page,
)
from playwright_stealth import Stealth

from models.job import Job


class ScraperService:
    EMAIL_REGEX = r"[\w\.\-]+@[\w\.\-]+\.[\w]+"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"

    async def enrich_jobs_with_details(self, jobs: List[Job]) -> List[Job]:
        print(f"Starting SIMPLIFIED scraping process for {len(jobs)} jobs...")

        async with Stealth().use_async(async_playwright()) as p:
            # You can set headless=False here to watch it work
            browser = await p.chromium.launch(headless=False)

            for index, job in enumerate(jobs):
                if not job.url:
                    continue

                print(f"[{index + 1}/{len(jobs)}] Scraping URL: {job.url}")

                context = await browser.new_context(
                    user_agent=self.USER_AGENT,
                    viewport={"width": 1920, "height": 1080},
                    extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
                )
                page = await context.new_page()

                try:
                    # Step 1: Navigate to the job page provided by the API
                    await page.goto(
                        job.url, timeout=60000, wait_until="domcontentloaded"
                    )

                    # Step 2: Scrape the content directly from this page's body
                    body_text = await page.locator("body").inner_text(timeout=15000)

                    # Step 3: Check for block pages and save the data
                    if (
                        "suspicious behaviour" in body_text
                        or "access denied" in body_text.lower()
                    ):
                        print("  -> BLOCKED by bot detection.")
                        job.job_description = "SCRAPING_BLOCKED"
                    else:
                        job.job_description = body_text.strip()
                        print("  -> Successfully scraped job description.")
                        found_emails = re.findall(self.EMAIL_REGEX, body_text)
                        if found_emails:
                            for email in found_emails:
                                if (
                                    "example.com" not in email
                                    and "sentry.io" not in email
                                ):
                                    job.email = email
                                    print(f"  -> Found email: {job.email}")
                                    break

                except Exception as e:
                    print(f"  -> An unexpected error occurred: {e}")
                finally:
                    await context.close()
                    sleep_time = random.uniform(3, 7)
                    print(f"  -> Waiting for {sleep_time:.2f} seconds...")
                    await asyncio.sleep(sleep_time)

            await browser.close()
        print("Scraping process complete.")
        return jobs

    async def enrich_job(self, job: Job) -> Job | None:
        """
        Takes a single Job object, scrapes its URL, and returns the enriched object.
        Returns None if a critical error occurs.
        """
        if not job.url:
            return job  # Return as-is if no URL

        print(f"Scraping URL: {job.url}")

        async with Stealth().use_async(async_playwright()) as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self.USER_AGENT,
                # ... (other context settings) ...
            )
            page = await context.new_page()

            try:
                await page.goto(job.url, timeout=60000, wait_until="domcontentloaded")
                body_text = await page.locator("body").inner_text(timeout=15000)

                if (
                    "suspicious behaviour" in body_text
                    or "access denied" in body_text.lower()
                ):
                    print("  -> BLOCKED by bot detection.")
                    job.job_description = "SCRAPING_BLOCKED"
                else:
                    job.job_description = body_text.strip()
                    print("  -> Successfully scraped job description.")
                    found_emails = re.findall(self.EMAIL_REGEX, body_text)
                    if found_emails:
                        for email in found_emails:
                            if "example.com" not in email and "sentry.io" not in email:
                                job.email = email
                                print(f"  -> Found email: {job.email}")
                                break

                return job

            except Exception as e:
                print(
                    f"  -> An unexpected error occurred while scraping {job.url}: {e}"
                )
                job.job_description = f"SCRAPING_FAILED: {e}"
                return job  # Return the job with an error message
            finally:
                await context.close()
                await browser.close()
