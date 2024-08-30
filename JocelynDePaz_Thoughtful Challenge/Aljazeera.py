import logging
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from robocorp import workitems
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, NoSuchElementException
import time
import re
import os
from CustomSelenium import CustomSelenium  

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Aljazeera:
    def __init__(self):
        self.browser = CustomSelenium()
        self.excel = Files()
        self.http = HTTP()
        self.base_url = "https://www.aljazeera.com/"
        self.search_phrase = None
        self.max_results = None

    def configure(self, search_phrase, max_results, sort_by):
        self.search_phrase = search_phrase
        self.max_results = min(max_results, 100)
        self.sort_by = sort_by
        logging.info(f"Configured scraper with search_phrase: '{search_phrase}' and max_results: {self.max_results}")

    def open_site(self):
        try:
            self.browser.set_webdriver() 
            self.browser.open_url(self.base_url)
            logging.info(f"Opened site: {self.base_url}")
        except Exception as e:
            workitems.inputs.current.fail(
                exception_type='APPLICATION',
                code='OPEN_SITE_FAILED',
                message=f"Failed to open site {self.base_url}: {str(e)}"
            )
            logging.error(f"Failed to open site {self.base_url}: {str(e)}")
            raise

    def close_cookie_banner(self):
        try:
            cookie_button_selector = (By.XPATH, "//button[text()='Allow all']")
            cookie_button = WebDriverWait(self.browser.driver, 10).until(
                EC.element_to_be_clickable(cookie_button_selector)
            )
            cookie_button.click()
            logging.info("Closed cookie consent banner by clicking 'Allow all'.")
        except TimeoutException:
            logging.info("Cookie consent banner did not appear or was not interactable.")
        except Exception as e:
            logging.error(f"Failed to close cookie consent banner: {str(e)}")

    def initiate_search(self):
        try:
            self.close_cookie_banner()

            search_button_selector = (By.CSS_SELECTOR, "div.site-header__search-trigger > button.no-styles-button")
            search_button = WebDriverWait(self.browser.driver, 10).until(
                EC.element_to_be_clickable(search_button_selector)
            )
            search_button.click()
            logging.info("Clicked search button")
        except TimeoutException:
            try:
                burger_menu_selector = (By.CSS_SELECTOR, "button.site-header__menu-trigger")
                burger_menu_button = WebDriverWait(self.browser.driver, 10).until(
                    EC.element_to_be_clickable(burger_menu_selector)
                )
                burger_menu_button.click()
                logging.info("Opened burger menu")
                
                search_box_selector = (By.CSS_SELECTOR, "input.search-bar__input")
                search_box = WebDriverWait(self.browser.driver, 10).until(
                    EC.visibility_of_element_located(search_box_selector)
                )
                search_box.click()
                logging.info("Clicked search box inside burger menu")
            except Exception as e:
                logging.error(f"Search box not found or not interactable after opening burger menu: {str(e)}")
                raise

    def search_news(self):
        try:

            search_box = WebDriverWait(self.browser.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@class='search-bar__input-container']/input[@class='search-bar__input']"))
            )
            search_box.clear() 
            search_box.send_keys(self.search_phrase)
            search_box.send_keys(Keys.ENTER)

            add_element = (By.CLASS_NAME, "ads__close-button")
            add = WebDriverWait(self.browser.driver, 10).until(
                    EC.visibility_of_element_located(add_element)
                )
            add.click()
            
            ads_container = self.browser.driver.find_element(By.CLASS_NAME, "container--ads")
            self.browser.driver.execute_script("arguments[0].style.visibility='hidden'", ads_container)
            logging.info("Ads container hidden.")

            logging.info(f"Searched news with phrase: {self.search_phrase}")
        except TimeoutException as e:
            workitems.inputs.current.fail(
                exception_type='APPLICATION',
                code='SEARCH_NEWS_FAILED',
                message=f"Search box not found or not interactable: {str(e)}"
            )
            logging.error(f"Search box not found or not interactable: {str(e)}")
            raise
        except ElementNotInteractableException as e:
            workitems.inputs.current.fail(
                exception_type='APPLICATION',
                code='SEARCH_NEWS_FAILED',
                message=f"Search box not interactable: {str(e)}"
            )
            logging.error(f"Search box not interactable: {str(e)}")
            raise
        except Exception as e:
            workitems.inputs.current.fail(
                exception_type='APPLICATION',
                code='SEARCH_NEWS_FAILED',
                message=f"Failed to search news with phrase {self.search_phrase}: {str(e)}"
            )
            logging.error(f"Failed to search news with phrase {self.search_phrase}: {str(e)}")
            raise

    def filter_and_sort_results(self):
        try:
            sort_selector = (By.ID, "search-sort-option")
            sort_element = WebDriverWait(self.browser.driver, 10).until(
                EC.element_to_be_clickable(sort_selector)
            )
            
            select = Select(sort_element)
            select.select_by_visible_text(self.sort_by)
            logging.info("Sorted results by date")

        except TimeoutException as e:
            workitems.inputs.current.fail(
                exception_type='APPLICATION',
                code='FILTER_SORT_FAILED',
                message=f"Sort element not found or not interactable: {str(e)}"
            )
            logging.error(f"Sort element not found or not interactable: {str(e)}")
            raise
        except Exception as e:
            workitems.inputs.current.fail(
                exception_type='APPLICATION',
                code='FILTER_SORT_FAILED',
                message=f"Failed to filter and sort results: {str(e)}"
            )
            logging.error(f"Failed to filter and sort results: {str(e)}")
            raise
    
    def get_loaded_articles(self):
        try:
            articles_selector = (By.CLASS_NAME, "gc.u-clickable-card")

            WebDriverWait(self.browser.driver, 10).until(
                EC.visibility_of_element_located(articles_selector)
            )
            
            articles = self.browser.driver.find_elements(*articles_selector)

            return len(articles), articles

        except Exception as e:
            logging.error(f"Failed to get loaded articles: {str(e)}")
            raise

    def load_more_results(self):
        try:
            total_loaded_results = 0

            while total_loaded_results < self.max_results:
                loaded_results, articles = self.get_loaded_articles()
                total_loaded_results += loaded_results
                if total_loaded_results >= self.max_results:
                    break

                show_more_button_selector = (By.CLASS_NAME, "show-more-button")
                try:
                    show_more_button = WebDriverWait(self.browser.driver, 10).until(
                        EC.element_to_be_clickable(show_more_button_selector)
                    )
                    show_more_button.click()
                    logging.info(f"Clicked 'Show more' button, total loaded: {total_loaded_results}")
                except TimeoutException:
                    logging.info("No more articles to load or 'Show more' button not found.")
                    break
            
            logging.info(f"Total articles loaded: {total_loaded_results}")

        except TimeoutException as e:
            workitems.inputs.current.fail(
                exception_type='APPLICATION',
                code='LOAD_MORE_RESULTS_FAILED',
                message=f"Load more button not found or not interactable: {str(e)}"
            )
            logging.error(f"Load more button not found or not interactable: {str(e)}")
            raise
        except Exception as e:
            workitems.inputs.current.fail(
                exception_type='APPLICATION',
                code='LOAD_MORE_RESULTS_FAILED',
                message=f"Failed to load more results: {str(e)}"
            )
            logging.error(f"Failed to load more results: {str(e)}")
            raise

    #@error_handler(code='EXTRACT_LATEST_NEWS_FAILED', message='Failed to extract latest news')
    def extract_latest_news(self):
        """
        Extracts the latest news articles' details such as title, date, description, image name, and other metadata.
        Processes the articles and adds them to a list for further processing.
        """
        try:
            news_data = []
            total_loaded_results = 0

            articles = self.browser.driver.find_elements(By.XPATH, "//article[contains(@class, 'gc u-clickable-card')]")
            time.sleep(2)

            for i in range(len(articles)):
                if total_loaded_results >= self.max_results:
                    break
                
                try:
                    article = self.browser.driver.find_elements(By.XPATH, "//article[contains(@class, 'gc u-clickable-card')]")[i]

                    title_element = article.find_element(By.CLASS_NAME, 'u-clickable-card__link')
                    self.browser.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", title_element)
                    time.sleep(1)
                    
                    title = title_element.text.strip()

                    url = title_element.get_attribute("href")

                    try:
                        date_element = article.find_element(By.CLASS_NAME, "screen-reader-text")
                        date = date_element.text.strip()
                    except NoSuchElementException:
                        date = "N/A"

                    try:
                        description_element = article.find_element(By.CLASS_NAME, 'gc__excerpt')
                        description = description_element.text.strip()
                    except NoSuchElementException:
                        description = "N/A"

                    # Extract image URL, if available
                    try:
                        image_element = WebDriverWait(article, 10).until(
                            EC.visibility_of_element_located((By.CLASS_NAME, 'gc__image'))
                        )
                        image_url = image_element.get_attribute('src') if image_element else 'N/A'
                        image_name = self.download_image(image_url, title)
                    except Exception:
                        logging.warning("No image found for this article.")
                        image_name = 'N/A'

                    search_phrase_count = title.lower().count(self.search_phrase.lower()) + description.lower().count(self.search_phrase.lower())
                    
                    contains_money = self.check_for_money(title + " " + description)

                    news_data.append({
                        "title": title,
                        "date": date,
                        "description": description,
                        "image_name": image_name,
                        "search_phrase_count": search_phrase_count,
                        "contains_money": contains_money,
                        "news_url": url
                    })

                    total_loaded_results += 1
                    logging.info(f"Extracted news: {title} - {date} - {description[:50]}...")

                except Exception as e:
                    logging.error(f"Error processing article: {str(e)}")
                    workitems.inputs.current.fail(
                        exception_type='APPLICATION',
                        code='ARTICLE_PROCESSING_ERROR',
                        message=f"Error processing article: {str(e)}"
                    )
                    continue
            return news_data

        except Exception as e:
            logging.error(f"Failed to extract latest news: {str(e)}")
            workitems.inputs.current.fail(
                exception_type='APPLICATION',
                code='EXTRACT_NEWS_FAILED',
                message=f"Failed to extract latest news: {str(e)}"
            )
            raise

    
    def sanitize_filename(self, filename):
        return re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    def download_image(self, url, title=""):
        try:
            image_name = url.split("/")[-1].split('?')[0]
            logging.info(f"Raw extracted image name: {image_name}")

            sanitized_title = self.sanitize_filename("_".join(title.split()[:3])) 
            image_name = f"{sanitized_title}.jpg"

            image_path = os.path.join(os.getcwd(), "output", image_name)
            self.http.download(url, image_path)
            logging.info(f"Downloaded image: {image_name} from {url}")
            return image_name
        except Exception as e:
            workitems.inputs.current.fail(
                exception_type='APPLICATION',
                code='DOWNLOAD_IMAGE_FAILED',
                message=f"Failed to download image from {url}: {str(e)}"
            )
            logging.error(f"Failed to download image from {url}: {str(e)}")
            raise

    def check_for_money(self, text):
        money_patterns = [
            r"\$\d+(?:\.\d{1,2})?",  
            r"\d+(?:,\d{3})*(?:\.\d{1,2})?\s+dollars?",  
            r"\d+(?:,\d{3})*(?:\.\d{1,2})?\s+USD",  
            r"£\d+(?:,\d{3})*(?:\.\d{1,2})?",  
            r"\d+(?:,\d{3})*(?:\.\d{1,2})?\s+pounds?",  
            r"€\d+(?:,\d{3})*(?:\.\d{1,2})?",  
            r"\d+(?:,\d{3})*(?:\.\d{1,2})?\s+euros?"
        ]
        for pattern in money_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logging.info(f"Money pattern found in text: {text}")
                return True
        return False

    def save_to_excel(self, news_data):
        try:
            output_path = os.path.join(os.getcwd(), "output", "task_extracted.xlsx")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            sheet_name = "Sheet" 
            sheet_name = "News"

            if os.path.exists(output_path):
                self.excel.open_workbook(output_path)
                logging.info(f"Opened existing Excel workbook at {output_path}")

            else:
                self.excel.create_workbook(output_path)
                logging.info(f"Created new Excel workbook at {output_path}")
            self.excel.create_workbook(output_path)
            logging.info(f"Created new Excel workbook at {output_path}")

            processed_data = []
            for item in news_data:
                processed_data.append({
                    "title": item["title"],
                    "date": item["date"],
                    "description": item["description"],
                    "image_name": item["image_name"],
                    "search_phrase_count": item["search_phrase_count"],
                    "contains_money": item["contains_money"],
                    "news_url": item["news_url"]
                })
                
            if self.excel.worksheet_exists(sheet_name):
                    self.excel.remove_worksheet(sheet_name)
                    logging.info(f"Removed existing worksheet '{sheet_name}'")

            self.excel.create_worksheet(sheet_name)
            self.excel.set_active_worksheet(sheet_name)
            logging.info(f"Created and set active worksheet '{sheet_name}'")

            self.excel.append_rows_to_worksheet(processed_data, header=True)

            self.excel.save_workbook(output_path)
            logging.info(f"Saved data to Excel workbook at {output_path}")
            

        except Exception as e:
            workitems.inputs.current.fail(
                exception_type='APPLICATION',
                code='SAVE_TO_EXCEL_FAILED',
                message=f"Failed to save data to Excel: {str(e)}"
            )
            logging.error(f"Failed to save data to Excel: {str(e)}")
            raise

    
    def close_browser(self):
        try:
            self.browser.close_browser()
            logging.info("Closed browser successfully")
        except Exception as e:
            workitems.inputs.current.fail(
                exception_type='APPLICATION',
                code='CLOSE_BROWSER_FAILED',
                message=f"Failed to close browser: {str(e)}"
            )
            logging.error(f"Failed to close browser: {str(e)}")
            raise
