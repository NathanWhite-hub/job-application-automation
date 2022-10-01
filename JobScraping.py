import time, os
import openpyxl
from Excel import *
from datetime import date

def navigate_to_job_list(page):
    # Go to https://www.linkedin.com/
    page.goto("https://www.linkedin.com/")
    time.sleep(2)

    # Click input[name="session_key"]
    page.locator("input[name=\"session_key\"]").fill(os.getenv('LINKEDIN_USERNAME'))
    time.sleep(2)

    # Click text=Password Show >> [placeholder=" "]
    page.locator("text=Password Show >> [placeholder=\" \"]").fill(os.getenv('LINKEDIN_PASSWORD'))
    time.sleep(2)

    # Click text=Sign in >> nth=1
    page.locator("text=Sign in").nth(1).click()
    time.sleep(5)

    # Click li:nth-child(3) > .app-aware-link > .ivm-image-view-model > .ivm-view-attr__img-wrapper > li-icon > .mercado-match
    page.locator("li:nth-child(3) > .app-aware-link > .ivm-image-view-model > .ivm-view-attr__img-wrapper > li-icon > .mercado-match").click()
    time.sleep(5)

    # Click li:has-text("software developer · 399 new Cleveland, Ohio, United States · Full-time · Remote") >> nth=0
    page.locator("li:has-text(\"software developer\")").first.click()
    time.sleep(5)

def get_total_num_jobs(page):
    # Get total number of jobs in the list.
    totalNumOfJobs = page.query_selector(".jobs-search-results-list__title-heading >> small.display-flex").text_content()

    # Format the string to convert it to an int.
    totalNumOfJobs = totalNumOfJobs.replace(",", "").strip()
    totalNumOfJobs = totalNumOfJobs.replace("results", "").strip()
    totalNumOfJobs = int(totalNumOfJobs)
    return totalNumOfJobs

def scrape_job_details(page, context, blackListedCompanies, PlaywrightTimeoutError):

    # Initialize variables.
    data = {1:"Company", 2:"Job", 3:"URL", 4: "Application Type"}
    numJobs = 0
    jobsSeen = 0
    jobsApplied = 0
    jobs = True
    today = date.today()

    # Begin a loop to navigate to each page.
    while jobs:
        jobCard = page.locator(".scaffold-layout__list-container >> css=[data-occludable-job-id]").nth(numJobs)

        # Check if the nth job card exists. If it's false, it means the bot has reached the bottom of the list. 
        # It will then navigate to the next page.
        if (jobCard.is_visible() == False):
            currentPage = page.locator(".artdeco-pagination__pages >> css=[aria-current=true] >> span").text_content()
            print(currentPage)
            currentPage = currentPage.strip()
            currentPage = int(currentPage)
            currentPage = currentPage + 1
            print(currentPage)
            nextPage = page.locator(f'css=[aria-label="Page {str(currentPage)}"]')

            if (nextPage.is_visible() == False):
                print("END")
                jobs = False
                break
            else:
                try:
                    nextPage.click()
                except PlaywrightTimeoutError:
                    print("Timeout Exception when going to next LinkedIn Page.")
                    page.reload()

            numJobs = 0
            time.sleep(2)
            continue

        # Click on the nth job card to bring up the details about it, then get the text content.
        jobCard.click()
        time.sleep(1)
        jobTitle = page.query_selector(".scaffold-layout__detail >> h2").text_content()
        jobCompany = page.query_selector(".scaffold-layout__detail >> .jobs-unified-top-card__company-name >> a").text_content()
        jobCompany = jobCompany.strip()

        if any(company in jobCompany for company in blackListedCompanies):
            print("Black listed company found. Continuing")
            numJobs = numJobs + 1
            continue

        applyButton = page.locator(".jobs-apply-button--top-card >> button >> span:text-is(\"Apply\")").first

        if (applyButton.is_visible() == False):
            # Check for Easy Apply button.
            applyButton = page.locator(".jobs-apply-button--top-card >> button >> span:has-text(\"Easy Apply\")").first

            if(applyButton.is_visible() == False):
                print("No Apply button found on LinkedIn. Continuing.")
                numJobs = numJobs + 1
                jobsApplied = jobsApplied + 1
                continue
            else:
                print("Easy Apply Button Found.")
                numJobs = numJobs + 1
                jobsApplied = jobsApplied + 1
                continue
        else:
            print("Apply button found. clicking and expecting page.")
            try:
                with context.expect_page() as apply_page:
                    applyButton.click()
                applyLinkPage = apply_page.value

            except PlaywrightTimeoutError:
                print("Timeout Exception. Continuing.")
                applyLinkPage = apply_page.value
                applyLinkPage.close(run_before_unload=True)
                time.sleep(2)
                numJobs = numJobs + 1
                continue
        
        applyLinkPage.wait_for_load_state('load')

        if(get_apply_url(applyLinkPage, context) == False):
            print("Get apply is false")
        else:
            print("Get apply is true")
            data.update({1:jobCompany, 2:jobTitle, 3:applyLinkPage.url, 4:""})
            append_job_information(data=data)
            jobsApplied = jobsApplied + 1


        applyLinkPage.close(run_before_unload=True)
        time.sleep(2)
        page.bring_to_front()

        # Increment numJobs to keep track of which nth job card element is next.
        numJobs = numJobs + 1
        jobsSeen = jobsSeen + 1
        print("Jobs Applied to: " + str(jobsApplied))
        print("Jobs I've Seen in Total: " + str(jobsSeen))

def get_apply_url(applyLinkPage, context):
    print("LinkedIn Apply button clicked. Navigating to new website and checking URL.")

    if "workday" in applyLinkPage.url:
        print("Workday URL found. Returning the URL.")
        print(applyLinkPage.url)
    else:
        applyButton = applyLinkPage.locator("button[text=\"Apply\"]")
        if (applyButton.is_visible() == False):
            applyButton = applyLinkPage.locator("a:has-text(\"Apply\")").first
            if (applyButton.is_visible() == False):
                applyButton = applyLinkPage.locator("span:has-text(\"Apply\")").first
                if (applyButton.is_visible() == False):
                    return False

        applyButton.click(force=True)
        print("Apply button on company website found. Clicking.")

        time.sleep(4)

        context.on("page", handle_page(applyLinkPage))

        if "workday" in applyLinkPage.url:
            print("Workday URL found. Returning the URL.")
            return applyLinkPage.url
        else:
            print("This website is not workday. Returning false.")
            return False


def handle_page(applyLinkPage):
    print("New page created. Handling load state.")
    applyLinkPage.wait_for_load_state()
