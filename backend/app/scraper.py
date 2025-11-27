# app/scraper.py

from playwright.sync_api import sync_playwright
from .crud_scraper import log_scraper_event, save_scraper_result

class RcmScraper:

    def __init__(self, session_id: int):
        self.session_id = session_id

    def login_and_scrape(self, payer, username, password, task_type, payload):
        log_scraper_event(self.session_id, "START", f"{task_type} for {payer}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            log_scraper_event(self.session_id, "LOGIN_ATTEMPT", payer)

            # -----------------------------
            # PAYER SPECIFIC LOGIN LOGIC
            # -----------------------------
            if payer.lower() == "availity":
                page.goto("https://apps.availity.com/availity/web/public.elegLogin")
                page.fill("#username", username)
                page.fill("#password", password)
                page.click("#loginButton")

            elif payer.lower() == "officeally":
                page.goto("https://pm.officeally.com/")
                page.fill("#UserID", username)
                page.fill("#Password", password)
                page.click("#LoginButton")

            else:
                raise Exception("Unsupported payer")

            page.wait_for_timeout(3000)

            log_scraper_event(self.session_id, "LOGIN_SUCCESS")

            # --------------- TASKS -----------------
            if task_type == "claim_status":
                save_scraper_result(self.session_id, "claim_status", '{"status":"SUBMITTED"}')

            elif task_type == "eligibility":
                save_scraper_result(self.session_id, "eligibility", '{"eligible": true}')

            elif task_type == "eob":
                save_scraper_result(self.session_id, "eob", '{"message": "EOB downloaded"}')

            browser.close()

        log_scraper_event(self.session_id, "FINISHED")