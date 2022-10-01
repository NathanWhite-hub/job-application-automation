# job-application-automation
This is a WIP LinkedIn job application bot designed in Python and utilizing Playwright web automation.

## What It Does
The bot will open to LinkedIn.com and begin the login process. Upon logging in it will navigate to "Jobs" page where it then select the last saved job search. Once here, the true funtionality of the bot begins. It will move over each job card in the list, clicking on each one, and gathering the company name and the job title. Once those are stored, it will then check to see if the apply button says "Apply" or "Easy Apply". It then clicks the button and navigates to the opened pop up in a new tab.

### Workday
Current functionality is designed for Workday websites as their layout was the most user friendly. It will check the link and see if it is a Workday link, if it's not, it will close the tab and continue onto the next job.

#### Current Use
If it's a Workday link, the bot will check the page for another button title "Apply" as many companies often have their apply button navigate to the job posting. The bot will then click the apply button, and that link is stored into an Excel file for future use. This link should direct to the Workday login portal.

### Blacklisted Companies
In the code is an array of strings, each of which are a company name. This array is checked against when the bot looked at the company name, and if the company is within that array, it will immediately continue onto the next job.

## Future Plans
Planned functionality is for the bot to immediately begin application procedures rather than only saving the link. Jobs that are applied to will also be stored in an additional Excel file which are marked with the company name, job title, and date of application. I would also like to expand functionality to other HR software such as ICIMS and Lever. However, the dynamic nature of these the differing websites may create issues as companies often have the ability to customize their application pages. As such, a seperate script for each of the supported HR software companies, or a robust dynamic script containing logic checks for the web layout may be considered solutions. I also currently plan to have the bot create accounts for the various HR software sites, which may be required to complete the application. This then takes me onto my next point below.

### Automatic Email Verification
Using Gmail's API, I have been experimenting with a solution to verification emails sent after an account is created, particularly for Workday (which often requires account creation). Using Gmail filters, I was able to funnel verification emails into a label, which the Gmail API then scans. Being that no unread email should be in that label, it will request the complete text data from the first email, then regex for a link. The link is grabbed and then sent to Playwright to navigate to, which completes the email verification process.
