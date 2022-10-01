def handle_easy_apply(page):
    applyButton = page.locator("button[aria-label=\"Submit application\"], button[aria-label=\"Continue to next step\"], button[aria-label=\"Review your application\"]")

    while (applyButton.is_visible() == True):
        if(additional_questions):
            answer_questions(page)
        else:
            applyButton.click()
            applyButton = page.locator("button[aria-label=\"Submit application\"], button[aria-label=\"Continue to next step\"], button[aria-label=\"Review your application\"]")

def additional_questions(page):
    questionsHeader = page.locator("h3:has-text('Additional Questions')")

    if(questionsHeader.is_visible() == False):
        return False
    else:
        return True

def answer_questions(page):
    questions = page.query_selector_all("[data-test-form-element-label-title=\"true\"]")

