import time, os
from EmailVerification import *
from JobScraping import *

from dotenv import load_dotenv
from types import NoneType
from playwright.sync_api import Playwright, sync_playwright, expect, TimeoutError as PlaywrightTimeoutError


# Main function that runs Playwright.
def run(playwright: Playwright) -> None:
    # Load the environment variable.
    load_dotenv()

    blackListedCompanies = ["Amazon", "Microsoft", "Google", "Liberty Mutual", "Uber", "Eaton"]

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()

    context.set_default_timeout(120000)

    # Open new page
    page = context.new_page()

    # Call method to navigate to the list of jobs.
    navigate_to_job_list(page)

    print(get_total_num_jobs(page))

    # Call method to begin scraping of each job.
    scrape_job_details(page, context, blackListedCompanies=blackListedCompanies, PlaywrightTimeoutError=PlaywrightTimeoutError)

    # ---------------------
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
