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

from .proxy_manager import ProxyManager


class ScraperService:
    EMAIL_REGEX = r"[\w\.\-]+@[\w\.\-]+\.[\w]+"
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0",
    ]
    MAX_RETRIES = 3  # Configure how many times to retry a failed scrape

    def __init__(self, proxy_manager: ProxyManager | None = None):
        """
        Initializes the scraper.
        Accepts an optional ProxyManager instance for robust scraping.
        """
        self.proxy_manager = proxy_manager
        if self.proxy_manager and self.proxy_manager.proxies:
            print(
                f"Scraper initialized with ProxyManager ({len(self.proxy_manager.proxies)} proxies available)."
            )
        else:
            print("Scraper initialized without proxies. Scraping may be less reliable.")

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

    async def enrich_job(self, job: Job) -> Job:
        if not job.url:
            return job

        print(f"Scraping URL: {job.url}")

        for attempt in range(self.MAX_RETRIES):
            browser = (
                None  # Initialize browser to None to ensure it's in scope for finally
            )
            proxy_details = (
                self.proxy_manager.get_random_proxy() if self.proxy_manager else None
            )
            launch_options = {"headless": True}
            if proxy_details:
                launch_options["proxy"] = proxy_details["playwright_format"]
                print(
                    f"  -> Attempt {attempt + 1}/{self.MAX_RETRIES} using proxy from {proxy_details['location']}"
                )
            else:
                print(f"  -> Attempt {attempt + 1}/{self.MAX_RETRIES} using local IP.")

            try:
                async with Stealth().use_async(async_playwright()) as p:
                    browser = await p.chromium.launch(**launch_options)
                    context = await browser.new_context(
                        user_agent=random.choice(self.USER_AGENTS),
                        viewport={"width": 1920, "height": 1080},
                        extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
                    )
                    page = await context.new_page()

                    await page.goto(
                        job.url, timeout=10000, wait_until="domcontentloaded"
                    )
                    body_text = await page.locator("body").inner_text(timeout=15000)

                    if (
                        "suspicious behaviour" in body_text
                        or "access denied" in body_text.lower()
                    ):
                        raise ValueError("Blocked by bot detection")

                    # --- Success Case ---
                    job.job_description = body_text.strip()
                    found_emails = re.findall(self.EMAIL_REGEX, body_text)
                    if found_emails:
                        for email in found_emails:
                            if "example.com" not in email and "sentry.io" not in email:
                                job.email = email
                                break
                    print("  -> Scrape successful.")
                    return job  # Return immediately on success

            except Exception as e:
                print(f"  -> Attempt failed: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(random.uniform(2, 5))
                # The loop continues to the next attempt

            finally:
                # ---  CLEANUP ---
                # This block runs every time, whether the 'try' succeeded or failed.
                if browser:
                    await browser.close()

        # --- All Retries Failed Case ---
        print(f"  -> All {self.MAX_RETRIES} attempts failed for this URL.")
        job.job_description = "SCRAPING_BLOCKED_MAX_RETRIES"
        return job
