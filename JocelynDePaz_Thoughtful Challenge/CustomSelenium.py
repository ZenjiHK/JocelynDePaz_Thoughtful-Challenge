from RPA.core.webdriver import start
import logging
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import os

class CustomSelenium:

    def __init__(self):
        self.driver = None
        self.logger = logging.getLogger(__name__)

    def set_chrome_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument('--disable-web-security')
        options.add_argument("--start-maximized")
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--disable-dev-shm-usage')  
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        return options

    def set_webdriver(self, browser="Chrome"):
        options = self.set_chrome_options()
        try:
            self.driver = start(browser, options=options)
            self.driver.set_window_size(1920, 1080)
        except WebDriverException as e:
            self.logger.error(f"Error starting the WebDriver: {e}")
            self.driver = None

    def open_url(self, url: str, screenshot: str = None):
        try:
            self.driver.get(url)
            if screenshot:
                self.driver.get_screenshot_as_file(screenshot)
        except WebDriverException as e:
            self.logger.error(f"Error opening URL {url}: {e}")
            self.restart_driver()
            self.driver.get(url)
            if screenshot:
                self.driver.get_screenshot_as_file(screenshot)

    def driver_quit(self):
        if self.driver:
            self.driver.quit()

    def full_page_screenshot(self, name="screenshot.png"):
        try:
            page_width = self.driver.execute_script('return document.body.scrollWidth')
            page_height = self.driver.execute_script('return document.body.scrollHeight')
            self.driver.set_window_size(page_width, page_height)
            screenshot_path = os.path.join(os.getcwd(), "output", name)
            self.driver.save_screenshot(screenshot_path)
            self.logger.info(f"Full page screenshot saved: {screenshot_path}")
        except WebDriverException as e:
            self.logger.error(f"Error taking full page screenshot: {e}")


    def restart_driver(self):
        self.driver_quit()
        self.set_webdriver()

    def close_browser(self):
        try:
            self.driver_quit()
            self.logger.info("Browser closed successfully")
        except WebDriverException as e:
            self.logger.error(f"Error closing the browser: {e}")