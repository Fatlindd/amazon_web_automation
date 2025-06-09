import random
import json
import os
import re
import time
import logging
import pandas as pd
import undetected_chromedriver as uc

from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.json_to_csv import save_json_to_csv
from typing import List, Dict, Any, Optional, Tuple, Union

from utils.setup_logger import LoggerSetup
from utils.price_utils import format_price, get_price_difference

 
class AmazonUPCProcessor:
    def __init__(self, excel_file_path: str, results_file: str, proxies_file_path: str) -> None:
        """
            Initialize the scraper with specified file paths and setup.

            Args:
                excel_file_path (str): The path to the Excel file containing product information.
                results_file (str): The path to the results file where product details will be saved.
                proxies_file_path (str): The path to the file containing proxy settings.

            This constructor initializes the following attributes:
            - `excel_file_path`: Path to the input Excel file.
            - `proxies_file_path`: Path to the proxy settings file.
            - `results_file_path`: Path to the output results file.
            - `driver`: Initializes as None to later hold the web driver instance.
            - `logger_setup`: Instance of LoggerSetup for logging purposes.
            - `logger`: Access to the logger for logging messages.
            - `user_agent`: Instance of UserAgent for managing user-agent strings.
            - `product_details`: List to store details of the products scraped.
        """
        self.excel_file_path = excel_file_path
        self.proxies_file_path = proxies_file_path
        self.results_file_path = results_file
        self.driver = None
        
        self.logger_setup = LoggerSetup()  # Create an instance of LoggerSetup
        self.logger_setup.setup_logger()  # Set up the logger
        self.logger = self.logger_setup.logger  # Access the logger

        self.user_agent = UserAgent()
        self.product_details = []  # List to store product details
        # self.proxies = self.load_proxies()
    
    def load_proxies(self) -> List[Dict[str, Any]]:
        """
            Load proxies from a JSON file.

            This method checks if the specified proxies file exists. If it does, 
            it attempts to open the file, read its content, and parse it as JSON. 
            It then extracts and returns a list of proxies from the parsed data.

            Returns:
                List[Dict[str, Any]]: A list of proxies loaded from the JSON file. 
                Each proxy is represented as a dictionary. If the file does not exist, 
                an empty list is returned.
        """
        if os.path.exists(self.proxies_file_path):
            with open(self.proxies_file_path, 'r') as proxies_file:
                data = json.load(proxies_file)
                return data.get("proxies", [])
        else:
            print(f"Proxies file not found at: {self.proxies_file_path}")
            return []
    
    def rotate_proxy(self) -> Optional[Dict[str, Any]]:
        """
            Select a random proxy from the list of proxies.

            This method checks if there are any available proxies in the internal
            list. If there are, it randomly selects and returns one proxy. If
            no proxies are available, it prints a warning message and returns
            None.

            Returns:
                Optional[Dict[str, Any]]: A randomly selected proxy represented as a 
                dictionary, or None if no proxies are available.
        """
        if self.proxies:
            return random.choice(self.proxies)
        else:
            print("No proxies available.")
            return None

    def start_driver(self) -> None:
        """
            Initialize the Chrome driver with a Mac OS and desktop user agent.

            This method configures and starts the Chrome driver for web scraping. 
            It randomly selects a user agent string that indicates a Mac OS desktop 
            environment, ensuring it does not include any mobile or tablet identifiers.
            The method also sets a default zip code for Amazon and prepares to process 
            UPC codes.

            The method will run indefinitely until a valid user agent is found. 
            Once a valid user agent is selected, the Chrome driver is launched with 
            the specified user agent, and the window is maximized.

            Returns:
                None: This method does not return any value.
        """
        while True:
            user_agent_string = self.user_agent.random
            # Ensure user agent contains Mac OS and is for a desktop (no 'Mobile' or 'Tablet')
            if "Macintosh" in user_agent_string and "Mobile" not in user_agent_string and "Tablet" not in user_agent_string:
                break
            
        self.logger.info(f"We are using user agent: {user_agent_string}")

        options = uc.ChromeOptions()
        options.add_argument(f'--user-agent={user_agent_string}')
        
        # proxy = self.rotate_proxy()
        # print(f"We are using proxy: {proxy}\n\n")
        # if proxy:
            # options.add_argument(f'--proxy-server={proxy}')

        self.driver = uc.Chrome(options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 3)

        # Set the zip code to amazon
        self.set_zip_code("10001")

        # Start process all upc codes with process_upc_code() method
        self.process_upc_codes()

    def close_driver(self) -> None:
        """Close the Chrome driver."""
        if self.driver:
            self.driver.quit()
            time.sleep(2)
            self.start_driver()
    
    def read_excel(self, last_upc: Optional[str]) -> Optional[pd.DataFrame]:
        """
            Read data from an Excel file and return a DataFrame based on the last UPC.

            This method checks if the specified Excel file exists. If it does, 
            it reads the content into a DataFrame, ensuring that the UPC codes are 
            treated as strings. If a last UPC code is provided, it searches for 
            this UPC in the DataFrame. If found, it returns all rows starting 
            from the next UPC code. If the last UPC is not found or if it is 
            None, the method logs the appropriate message and returns either 
            the entire DataFrame or an empty DataFrame if no UPC codes are 
            available.

            Args:
                last_upc (Optional[str]): The last UPC code to search for in the DataFrame. 
                                        It should be provided as a string. If None, the 
                                        entire DataFrame will be returned.

            Returns:
                Optional[pd.DataFrame]: A DataFrame containing the data from the Excel file. 
                                        If the file does not exist, it returns None. If the 
                                        last UPC is found, it returns the DataFrame sliced 
                                        from the next index; otherwise, it may return the 
                                        entire DataFrame or an empty DataFrame.
        """
        if os.path.exists(self.excel_file_path):
            df = pd.read_excel(self.excel_file_path, dtype={'upc_code': str})
            # df = pd.read_excel(self.excel_file_path)
            print("DF: ", df)

            if last_upc is not None:
                # Convert last_upc to an integer
                target_upc_code = int(last_upc)  # The UPC code you are looking for
                index = df.index[df['upc_code'] == target_upc_code]

                if not index.empty:
                    # Get the next index if it exists
                    next_index = index[0] + 1
                    if next_index < len(df):
                        # Slice the DataFrame from the next index
                        df_from_target = df.loc[next_index:]
                        print("DataFrame starting from the next UPC code:")
                        print(df_from_target)
                        return df_from_target
                    else:
                        self.logger.info(f"No more UPC codes available after the specified UPC")
                        return df.iloc[0:0]  # Return an empty DataFrame
                else:
                    self.logger.info(f"UPC code {target_upc_code} not found.")
                    return df
            else:
                # No last UPC found, return the whole DataFrame
                self.logger.info("No last UPC code found, returning all data from Excel.")
                return df
        else:
            self.logger.error(f"Excel file not found at: {self.excel_file_path}")
            return None

    def get_asin_code(self, url: str) -> str:
        """
            Extract the ASIN code from a given Amazon product URL.

            This method uses a regular expression to search for the ASIN (Amazon 
            Standard Identification Number) within the provided URL. If a valid 
            ASIN is found, it returns the ASIN code. If the ASIN is not found, 
            it returns "N/A".

            Args:
                url (str): The Amazon product URL from which to extract the ASIN.

            Returns:
                str: The extracted ASIN code if found; otherwise, "N/A".
        """
        
        asin = re.search(r'/dp/([A-Z0-9]{10})', url)

        if asin:
            return asin.group(1)
        else:
            return "N/A"
    
    def is_deliver_to_avaiable(self) -> bool:
        """
            Check if the 'Deliver to' option is available on the page.

            This method attempts to locate the 'Deliver to' button on the webpage 
            using a specified XPath. If the button is clickable within a 10-second 
            wait time, it logs that the option is available and returns True. 
            If the button is not found or not clickable, it logs that the option 
            is not available and returns False.

            Returns:
                bool: True if the 'Deliver to' option is available; False otherwise.
        """
        try:
            deliver_to_btn_elem = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@id='nav-global-location-popover-link']"))
            )
            self.logger.info("Deliver to option is available!")
            return True
        except:
            self.logger.error("Deliver to option is not available!")
            return False

    def set_zip_code(self, zip_code: str) -> None:
        """
            Set the delivery ZIP code on Amazon using JavaScript injection.

            This method navigates to the Amazon homepage and checks if the 
            'Deliver to' option is available. If it is, the method uses 
            JavaScript to open the delivery change section, sets the provided 
            ZIP code, and clicks the "Apply" button to confirm the change. 
            Finally, it clicks the "Continue" button to complete the process. 
            If the 'Deliver to' option is not available, it closes the driver.

            Args:
                zip_code (str): The ZIP code to be set for delivery.

            Returns:
                None
        """
        try:
            self.driver.get("https://www.amazon.com")
            time.sleep(3)  # Allow page to load
            
            # Controll if Deliver to is not available
            if self.is_deliver_to_avaiable():
                time.sleep(2)
                # Open the delivery change section using JavaScript
                self.driver.execute_script("""
                    document.getElementById('nav-global-location-popover-link').click();
                """)
                time.sleep(3)

                # Set the ZIP code
                self.driver.execute_script(f"""
                    document.getElementById('GLUXZipUpdateInput').value = '{zip_code}';
                """)
                time.sleep(3)

                # Click the "Apply" button
                apply_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[@id='GLUXZipUpdate']//input[@aria-labelledby='GLUXZipUpdate-announce']"))
                )
                apply_button.click()
                self.logger.info(f"ZIP code {zip_code} applied successfully!")

                # Click the "Continue" button inside the popup
                continue_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@id='GLUXConfirmClose']"))
                )
                continue_button.click()
                self.logger.info("Continue button clicked successfully!")

            else:
                self.close_driver()

        except Exception:
            self.logger.error(f"An error occurred while setting the ZIP code!")

    def get_last_upc(self) -> str:
        """
            Retrieve the last saved UPC code from the JSON file.

            This method checks if a specified JSON file exists. If it does, 
            it attempts to load the data and retrieve the last UPC code 
            from the list of saved entries. If the file does not exist or 
            if there is an error reading the file, appropriate error 
            messages are logged.

            Returns:
                str: The last saved UPC code if available; None if the file 
                does not exist or if an error occurs.
        """
        json_file_path = os.path.join(os.getcwd(), self.results_file_path)

        # Check if the file exists
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as json_file:
                try:
                    data = json.load(json_file)
                    if data:  # Check if there is data
                        last_upc = data[-1]["UPC"]  # Get the last UPC from the last dictionary
                        return last_upc
                except json.JSONDecodeError:
                    self.logger.error(f"Error reading JSON file {json_file_path}.")
        else:
            self.logger.error(f"JSON file not found at: {json_file_path}")
        
        return None

    def is_page_active(self) -> None:
        """
            Check if the current page is accessible by examining the title.

            This method retrieves the title of the current page in the 
            web driver and checks if it starts with the specified text 
            indicating that access is blocked. If the page is blocked, 
            it logs an error message and refreshes the page after a brief 
            pause.

            Returns:
                None
        """
        page_title = self.driver.title

        # Check if the title starts with the specified text
        if page_title.startswith("Sorry!"):
            self.logger.error("!!! We are blocked by Amazon. Please try again later!!!")
            time.sleep(3)
            self.driver.refresh()

    def process_upc_codes(self) -> None:
        """
            Process UPC codes by reading from an Excel file, searching on Amazon, and collecting product details.

            This method performs the following steps:
            1. Reads the last saved UPC code from a JSON file.
            2. Reads UPC codes from an Excel file starting from the last saved UPC.
            3. Constructs Amazon search URLs for each UPC code and retrieves product details.
            4. Collects product information and saves it to a JSON file.
            5. Saves the collected data to a CSV file.

            Returns:
                None
        """
        last_upc = self.get_last_upc()
        self.logger.info(f"\n\nlast_upc: {last_upc}")

        # Step 2: Read from the Excel file
        df = self.read_excel(last_upc)

        # Step 3: Process each UPC code from the DataFrame
        if df is not None and not df.empty:
            # Determine the starting index
            if last_upc is None:
                start_index = 0  # Start from the first row
            else:
                # Find the index of the last UPC code
                start_index = df[df['upc_code'].astype(str).str.zfill(12) == last_upc].index
                if not start_index.empty:
                    start_index = start_index[0] + 1  # Start from the next row
                else:
                    start_index = 0  # If last_upc not found, start from the first row

            # Process from the determined start index
            for index in range(start_index, len(df)):
                row = df.iloc[index]
                upc_code_original = row['upc_code']
                zoro_no = row['zoro_no']
                upc_code = str(row['upc_code']).zfill(12)
                sales_price = row['sales_price']

                self.logger.info(f"upc_code_original: {upc_code_original}")
                self.logger.info(f"upc_code: {upc_code}, {type(upc_code)}")

                # Construct Amazon search URL with the upc_code
                search_url = f"https://www.amazon.com/s?k={upc_code}"
                self.logger.info(f"\n\nsearch_url: {search_url}")

                # Navigate to the search URL
                self.driver.get(search_url)

                self.is_page_active()
                time.sleep(5)

                try:
                    self.wait.until(EC.presence_of_element_located((By.XPATH, "//span[normalize-space()='No results for']")))
                    self.logger.error(f"We don't have products for UPC code: {upc_code}")

                    # Collect the details in a dictionary
                    product_detail = {
                        "UPC": upc_code_original,
                        "Zoro_No": zoro_no,
                        "url": self.driver.current_url,
                        "ASIN": "N/A",
                        "BSR": "N/A",
                        "Price": "N/A",
                        "Price difference": "N/A",
                        "First Category": "N/A",
                        "Seller": "N/A"
                    }

                    # Append the product detail to the list
                    self.product_details.append(product_detail)

                    # Save details to JSON file
                    self.save_details_to_json()

                except Exception:
                    self.logger.info(f"We have some products for UPC code: {upc_code}!")

                try:
                    all_upc_products = self.wait.until(
                        EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'puis-card-border')]"))
                    )
                    products_href = []
                    for product in all_upc_products:
                        href_elem = product.find_element(By.XPATH, ".//h2//a")
                        href = href_elem.get_attribute("href")
                        products_href.append(href)

                    self.get_details_of_products(products_href, upc_code_original, zoro_no, sales_price)

                except:
                    pass
        
        # Call the function to save JSON data to CSV
        time.sleep(3)
        save_json_to_csv(self.results_file_path, 'src/csv/03_amazon_data.csv')

        # In the end stop the driver
        self.close_driver()
    
    def get_first_category(self, parent_text: str) -> str:
        """
            Extract the first category from the given text.

            This method uses a regular expression to find the text that follows the word 'in' and
            precedes any parentheses or line breaks. It returns the cleaned category string.

            Args:
                parent_text (str): The input text from which to extract the category.

            Returns:
                str: The extracted category if found; otherwise, returns None.
        """
        match = re.search(r'in\s+([A-Za-z\s&]+)\s*(?:\(|$)', parent_text)
        
        if match:
            return match.group(1).strip()  # Return the category
        else:
            return None

    def get_bsr_number(self, bsr_text: str) -> str:
        """
            Extract the Best Seller Rank (BSR) number from the given text.

            This method uses a regular expression to find the numeric portion of the BSR
            within the text. It returns the BSR number as a string or None if not found.

            Args:
                bsr_text (str): The input text that may contain the BSR number.

            Returns:
                str: The extracted BSR number if found; otherwise, returns None.
        """
        match = re.search(r'#([\d,]+)', bsr_text)
        return match.group(1) if match else None
        
    def extract_bsr_and_first_category(self) -> Tuple[Union[str, None], Union[str, None]]:
        """
            Extract the Best Seller Rank (BSR) number and the first category from the item details.

            This method attempts to find the Best Seller Rank and its corresponding category
            from the item details section on an Amazon product page. It performs two attempts 
            to locate the relevant information using different XPaths. If successful, it 
            returns the BSR number and first category. If not found, it returns "N/A".

            Returns:
                Tuple[Union[str, None], Union[str, None]]: A tuple containing the BSR number and
                first category. Both values will be "N/A" if not found, or None in case of an error.
        """
        try:
            WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@role='button' and contains(@class, 'a-expander-header') and contains(.//span, 'Item details')]"))
            ).click()

        except:
            self.logger.info(f"Item Detail Table is not present!")

        try:
            best_seller_th = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//th[contains(text(), 'Best Sellers Rank')]"))
            )

            if best_seller_th:
                best_seller_td = best_seller_th.find_element(By.XPATH, "./following-sibling::td")
                best_seller_text = best_seller_td.text.strip()

                bsr_number = self.get_bsr_number(best_seller_text) if best_seller_text else "N/A"
                first_category = self.get_first_category(best_seller_text) if best_seller_text else "N/A"

                return bsr_number, first_category
        except:
            self.logger.error(f"First attempt to get bsr failed.")

        try:
            best_seller_ranks_elem = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='detailBulletsWrapper_feature_div']//span[contains(text(), 'Best Sellers Rank')]"))
            )

            if best_seller_ranks_elem:
                parent_element = best_seller_ranks_elem.find_element(By.XPATH, "..")
                parent_text = parent_element.text.strip()
                bsr_number = self.get_bsr_number(parent_text) if parent_text else "N/A"
                first_category = self.get_first_category(parent_text) if parent_text else "N/A"
                return bsr_number, first_category

        except:
            self.logger.error(f"Second attempt to get bsr failed.")

        return "N/A"
    
    def get_details_of_products(
            self, 
            urls: list[str], 
            upc_code: str, 
            zoro_no: str, 
            sales_price: str
            ) -> None:
        """
            Retrieve details of products from Amazon using the provided URLs.

            This method navigates to each product URL, attempts to retrieve 
            the product's price, seller information, Best Sellers Rank (BSR), 
            and the first category. If successful, it compiles this data into 
            a dictionary and appends it to the product details list.

            Args:
                urls (list[str]): A list of product URLs to retrieve details from.
                upc_code (str): The UPC code associated with the product.
                zoro_no (str): The Zoro number for the product.
                sales_price (str): The sales price for comparison to the found price.

            Returns:
                None
        """
        for url in urls:
            self.driver.get(url)
            self.is_page_active()
            time.sleep(1)
            url = self.driver.current_url
            asin = self.get_asin_code(url)
            
            price_found = False
            try:
                price_elem = self.driver.find_element(By.CSS_SELECTOR, "#buybox-see-all-buying-choices .a-button-text")
                price_elem.click()
                time.sleep(3)

                price_text = self.driver.find_element(By.CSS_SELECTOR, ".a-section.a-spacing-none.aok-align-center.aok-relative")
                price_to_format = price_text.text
                price = format_price(price_to_format)

                price_found = True
            except:
                self.logger.error("We can not get price with clicking right window...")

            if not price_found:
                price_xpaths = [
                    "(//div[@class='a-spacing-top-mini']/span)[1]",
                    "(//span[@class='a-price aok-align-center reinventPricePriceToPayMargin priceToPay'])[1]",
                    "(//div[@class='a-section a-spacing-micro']/span)[1]",
                    "(//div[@class='a-section a-spacing-none aok-align-center aok-relative']/span)[1]",
                    "//span[@id='kindle-price']",
                    "(//span[@class='slot-price']/span)[1]",
                    "//span[contains(text(),'Buy')]",
                    "//*[(@id = 'tvod-btn-ab-movie-hd-tvod_purchase')]//*[contains(concat( " ", @class, " " ), concat( " ", '_36qUej', " " ))]"
                ]
                for price_xpath in price_xpaths:
                    try:
                        price_elem = self.wait.until(
                            EC.presence_of_element_located((By.XPATH, price_xpath))
                        )
                        price_text = price_elem.text
                        price = format_price(price_text)

                        try:
                            price_value = float(price)
                            self.logger.info(f"Price found: {price_value}")
                            break
                        except ValueError:
                            self.logger.error(f"Invalid price format: {price}")
                            price = "N/A" 
                    except:
                        price = "N/A"
            
            
            price_difference = get_price_difference(price, sales_price)

            try:
                seller_elem = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.offer-display-feature-text span.offer-display-feature-text-message"))
                )
                seller = seller_elem.text
            except:
                seller = "N/A"

            try:
                bsr, first_category = self.extract_bsr_and_first_category()
            except:
                bsr = "N/A"
                first_category = "N/A"

            # Collect the details in a dictionary
            product_detail = {
                "UPC": upc_code,
                "Zoro_No": zoro_no,
                "url": url,
                "ASIN": asin,
                "BSR": bsr,
                "Price": price,
                "Price difference": price_difference,
                "First Category": first_category,
                "Seller": seller
            }

            # Append the product detail to the list
            self.product_details.append(product_detail)

        # Save details to JSON file
        self.save_details_to_json()

    def save_details_to_json(self) -> None:
        """
            Append the product details to an existing JSON file or create a new one.

            This method checks if a specified JSON file exists. If it does, it 
            loads the existing data, filters out any duplicate UPCs from the 
            new product details, and then appends only the unique entries. 
            Finally, it saves the updated data back to the JSON file.

            Returns:
                None
        """
        json_file_path = os.path.join(os.getcwd(), self.results_file_path)
        
        # Check if the file exists
        if os.path.exists(json_file_path):
            # Load the existing data
            with open(json_file_path, 'r') as json_file:
                try:
                    existing_data = json.load(json_file)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        # Create a set of existing UPCs to avoid duplicates
        existing_upcs = {item['UPC'] for item in existing_data}

        # Filter out duplicates from self.product_details
        new_data = [item for item in self.product_details if item['UPC'] not in existing_upcs]

        # Append only new data (non-duplicates)
        existing_data.extend(new_data)

        # Save the updated data back to the JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)
        
        self.logger.info(f"Details appended to {json_file_path}")
