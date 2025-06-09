import json
import os
import re
import time
import pandas as pd
import random
import undetected_chromedriver as uc

from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.json_to_csv import save_json_to_csv


class AmazonUPCProcessor:
    def __init__(self, excel_file_path, proxies_file_path):
        self.excel_file_path = excel_file_path
        self.proxies_file_path = proxies_file_path
        self.driver = None
        self.user_agent = UserAgent()
        self.product_details = []  # List to store product details
        # self.proxies = self.load_proxies()
    
    def load_proxies(self) -> list:
        """
            Load proxies from a JSON file.

            This method attempts to load the list of proxies from a specified JSON file. If the file exists, it reads
            the file and extracts the "proxies" key's value, which should be a list of proxy addresses. If the "proxies" key is not found, it returns an empty list.

            If the file does not exist, a message is printed indicating the file was not found and not an empty list is returned. 

            Returns:
            list: A list of proxies loaded from the JSON file, or an empty list if the file does not exists or the "proxies" key is not found.
        """
        if os.path.exists(self.proxies_file_path):
            with open(self.proxies_file_path, 'r') as proxies_file:
                data = json.load(proxies_file)
                return data.get("proxies", [])
        else:
            print(f"Proxies file not found at: {self.proxies_file_path}")
            return []
    
    def rotate_proxy(self) -> str | None:
        """
            Select a random proxy from the list of proxies.

            This method chooses a random proxy from the list of available proxies.
            If the proxy list is not empty, a randomly selected proxy is returned.
            If no proxies are available, a message is printed, and the method returns None.

            Returns:
            str | None: A randomly selected proxy string if proxies are available, 
                        otherwise None.
        """
        if self.proxies:
            return random.choice(self.proxies)
        else:
            print("No proxies available.")
            return None

    def start_driver(self) -> None:
        """
            Initialize the Chrome driver with a Mac OS and PC user agent.

            This method sets up a Chrome driver using a randomly selected user agent that meets
            specific criteria: it must be for a Mac OS desktop and not contain 'Mobile' or 'Tablet' 
            in the user agent string. Once a valid user agent is found, it is added to the Chrome 
            options. The driver is then initialized with these options and maximized.

            Additionally, a proxy can be set up if needed by uncommenting the relevant code.
            
            The method also sets up an explicit WebDriver wait with a timeout of 3 seconds for the driver.

            Returns:
            None
        """
        while True:
            user_agent_string = self.user_agent.random
            # Ensure user agent contains Mac OS and is for a desktop (no 'Mobile' or 'Tablet')
            if "Macintosh" in user_agent_string and "Mobile" not in user_agent_string and "Tablet" not in user_agent_string:
                break

        print(f"We are using user agent: {user_agent_string}\n\n")

        options = uc.ChromeOptions()
        options.add_argument(f'--user-agent={user_agent_string}')
        
        # proxy = self.rotate_proxy()
        # print(f"We are using proxy: {proxy}\n\n")
        # if proxy:
            # options.add_argument(f'--proxy-server={proxy}')

        self.driver = uc.Chrome(options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 3)

    def close_driver(self) -> None:
        """Close the Chrome driver."""
        if self.driver:
            self.driver.quit()
    
    def read_excel(self, last_upc: str | None) -> pd.DataFrame | None:
        """
            Read data from an Excel file and return a DataFrame starting from a specified UPC code.

            This method reads an Excel file at the specified file path into a pandas DataFrame,
            ensuring the 'upc_code' column is treated as a string. If a `last_upc` is provided,
            the method searches for this UPC code within the DataFrame and returns all rows
            starting from the next row after the found UPC code. If the UPC code is not found
            or there are no more rows, it returns an appropriate message and an empty DataFrame.

            If no `last_upc` is given, the method returns the entire DataFrame. If the file
            does not exist, it returns None.

            Parameters:
            last_upc (str | None): The last UPC code to start reading from. If None, the entire
                                DataFrame will be returned.

            Returns:
            pd.DataFrame | None: A DataFrame containing rows starting from the specified UPC code,
                                the entire DataFrame if `last_upc` is not specified, or None if 
                                the file does not exist.
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
                        print("No more UPC codes available after the specified UPC.")
                        return df.iloc[0:0]  # Return an empty DataFrame
                else:
                    print(f"UPC code {target_upc_code} not found.")
                    return df
            else:
                # No last UPC found, return the whole DataFrame
                print("No last UPC code found, returning all data from Excel.")
                return df
        else:
            print(f"Excel file not found at: {self.excel_file_path}")
            return None

        
    def get_asin_code(self, url: str) -> str:
        """
            Extract the ASIN code from a given URL.

            This method uses a regular expression to search for an Amazon Standard Identification Number (ASIN)
            in the specified URL. The ASIN is typically a 10-character alphanumeric code found in URLs containing
            "/dp/". If a valid ASIN is found, it is returned; otherwise, the method returns "N/A".

            Parameters:
            url (str): The URL string from which to extract the ASIN code.

            Returns:
            str: The extracted ASIN code if found, otherwise "N/A".
        """
        asin = re.search(r'/dp/([A-Z0-9]{10})', url)

        if asin:
            return asin.group(1)
        else:
            return "N/A"

    def set_zip_code(self, zip_code: str) -> None:
        """
            Set the delivery ZIP code on the Amazon website using JavaScript injection.

            This method navigates to the Amazon homepage and uses JavaScript to interact with the
            delivery change section. It sets the specified ZIP code in the relevant input field,
            clicks the "Apply" button, and confirms the change by clicking the "Continue" button
            in the popup. It includes error handling to print an error message if any exceptions occur.

            Parameters:
            zip_code (str): The delivery ZIP code to be set on the Amazon website.

            Returns:
            None
        """
        try:
            self.driver.get("https://www.amazon.com")  # Open Amazon
            time.sleep(5)  # Allow page to load

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
            print(f"ZIP code {zip_code} applied successfully!")

            # Click the "Continue" button inside the popup
            continue_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='GLUXConfirmClose']"))
            )
            continue_button.click()
            print("Continue button clicked successfully!")

        except Exception:
            print(f"An error occurred while setting the ZIP code!")

    def get_last_upc(self) -> str:
        """
            Retrieve the last saved UPC code from the JSON file.

            This method checks for the existence of a JSON file named '02_amazon_data.json' in the current
            working directory. If the file exists and contains data, it retrieves and returns the last UPC
            code stored in the file. If the file does not exist or cannot be read, it prints an error message
            and returns None.

            Returns:
            str: The last UPC code if found, otherwise None.
        """
        json_file_path = os.path.join(os.getcwd(), '02_amazon_data.json')

        # Check if the file exists
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as json_file:
                try:
                    data = json.load(json_file)
                    if data:  # Check if there is data
                        last_upc = data[-1]["UPC"]  # Get the last UPC from the last dictionary
                        return last_upc
                except json.JSONDecodeError:
                    print("Error reading JSON file.")
        else:
            print(f"JSON file not found at: {json_file_path}")
        
        return None

    def is_page_active(self):
        # Get the title of the page
        page_title = self.driver.title

        # Check if the title starts with the specified text
        if page_title.startswith("Sorry! Something went wrong..."):
            print("\n\nWe are blocked by Amazon. Please try again later.\n\n")

    def process_upc_codes(self):
        # Step 1: Read the last saved UPC code from the JSON file
        last_upc = self.get_last_upc()
        print(f"\n\nlast_upc: {last_upc}")

        # Step 2: Read from the Excel file
        df = self.read_excel(last_upc)

        # Step 3: Process each UPC code from the DataFrame
        if df is not None and not df.empty:
            for _, row in df.iterrows():
                upc_code_original = row['upc_code']

                zoro_no = row['zoro_no']
                upc_code = str(row['upc_code']).zfill(12)
                sales_price = row['sales_price']

                print(f"upc_code_original: {upc_code_original}")
                print(f"zoro_no: {zoro_no}, {type(zoro_no)}")
                print(f"upc_code: {upc_code}, {type(upc_code)}")

                # Construct Amazon search URL with the upc_code
                search_url = f"https://www.amazon.com/s?k={upc_code}"
                print(f"\n\nsearch_url: {search_url}")

                # Navigate to the search URL
                self.driver.get(search_url)
                self.is_page_active()
                time.sleep(5)

                try:
                    self.wait.until(EC.presence_of_element_located((By.XPATH, "//span[normalize-space()='No results for']")))
                    print("We don't have products!")

                    # Collect the details in a dictionary
                    product_detail = {
                        "UPC": upc_code,
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
                    print("We have some products!")

                try:
                    all_upc_products = self.wait.until(
                        EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'puis-card-border')]"))
                    )
                    products_href = []
                    for product in all_upc_products:
                        href_elem = product.find_element(By.XPATH, ".//h2//a")
                        href = href_elem.get_attribute("href")
                        products_href.append(href)

                    self.get_details_of_products(products_href, upc_code, zoro_no, sales_price)

                except:
                    print(f"For UPC {upc_code}, we don't have any product!\n\n")
    
    def get_price_difference(self, price, zoro_price):
        try:
            price, zoro_price = float(price), float(zoro_price)
            diff = price - zoro_price * 1.203
            if zoro_price > 50:
                diff = price - ((zoro_price + 5) * 1.203)
            return diff
        except ValueError:
            return 'N/A'
    
    def get_first_category(self, parent_text):
        # Use regex to find text after 'in' and before any parentheses or line break
        match = re.search(r'in\s+([A-Za-z\s&]+)\s*(?:\(|$)', parent_text)
        
        if match:
            return match.group(1).strip()  # Return the category
        else:
            return None

    def get_bsr_number(self, bsr_text):
        match = re.search(r'#([\d,]+)', bsr_text)
        return match.group(1) if match else None
        
    def extract_bsr_and_first_category(self):
        try:
            WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@role='button' and contains(@class, 'a-expander-header') and contains(.//span, 'Item details')]"))
            ).click()

        except:
            print(f"Item Detail Table is not present!")

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
            print(f"First attempt to get bsr failed.")

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
            print(f"Second attempt to get bsr failed.")

        return "N/A"
    
    def format_price(self, price: str) -> str:
        """
            Format the price string by stripping, replacing symbols, and splitting into parts.

            This method cleans the input price string by:
            - Stripping any leading or trailing whitespace.
            - Removing the '$' symbol and any occurrences of 'UHD'.
            - Splitting the price string on newline characters.
            - Formatting the price as 'part1.part2' if two parts are found, otherwise returning the cleaned string.

            Parameters:
            price (str): The original price string.

            Returns:
            str: The correctly formatted price string.
        """

        price_text = price.strip().replace('$', '').replace('UHD', '').strip()
        price_parts = price_text.split('\n')
        correct_price = f"{price_parts[0].strip()}.{price_parts[1].strip()}" if len(price_parts) == 2 else price_text

        return correct_price
        
    def get_details_of_products(self, urls, upc_code, zoro_no, sales_price):
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
                price = self.format_price(price_to_format)

                print(f"Price: {price}")
                price_found = True
            except:
                print("We can not get price with clicking right window...")

            if not price_found:
                price_xpaths = [
                    "(//div[@class='a-spacing-top-mini']/span)[1]",
                    "(//span[@class='a-price aok-align-center reinventPricePriceToPayMargin priceToPay'])[1]",
                    "(//div[@class='a-section a-spacing-micro']/span)[1]",
                    "(//div[@class='a-section a-spacing-none aok-align-center aok-relative']/span)[1]",
                    "(//span[@class='slot-price']/span)[1]",
                    "//span[@id='kindle-price']"
                    "//span[contains(text(),'Buy')]",
                    "//*[(@id = 'tvod-btn-ab-movie-hd-tvod_purchase')]//*[contains(concat( " ", @class, " " ), concat( " ", '_36qUej', " " ))]"
                ]
                for price_xpath in price_xpaths:
                    try:
                        price_elem = self.wait.until(
                            EC.presence_of_element_located((By.XPATH, price_xpath))
                        )
                        price_text = price_elem.text
                        price = self.format_price(price_text)

                        try:
                            price_value = float(price)
                            print(f"Price found: {price_value}")
                            break
                        except ValueError:
                            print(f"Invalid price format: {price}")
                            price = "N/A"  # Continue searching
                    except:
                        price = "N/A"
            
            
            price_difference = self.get_price_difference(price, sales_price)

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

    def save_details_to_json(self):
        """Append the product details to an existing JSON file or create a new one."""
        json_file_path = os.path.join(os.getcwd(), '02_amazon_data.json')
        
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
        
        print(f"Details appended to {json_file_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_file_path = os.path.join(base_dir, 'data', 'data.xlsx')
    proxies_file_path = os.path.join(base_dir, 'data', 'proxies.json')

    amazon_upc_processor = AmazonUPCProcessor(excel_file_path, proxies_file_path)
    amazon_upc_processor.start_driver()

    amazon_upc_processor.set_zip_code("10001")
    amazon_upc_processor.process_upc_codes()
    amazon_upc_processor.close_driver()

    time.sleep(3)
    # Call the function to save JSON data to CSV
    save_json_to_csv('02_amazon_data.json', '02_amazon_data.csv')



"""
<div id="g">
  <div><a href="/ref=cs_503_link"><img src="https://images-na.ssl-images-amazon.com/images/G/01/error/500_503.png" alt="Sorry! Something went wrong on our end. Please go back and try again or go to Amazon's home page."></a>
  </div>
  <a href="/dogsofamazon/ref=cs_503_d" target="_blank" rel="noopener noreferrer"><img id="d" alt="Dogs of Amazon" src="https://images-na.ssl-images-amazon.com/images/G/01/error/36._TTD_.jpg"></a>
  <script>document.getElementById("d").src = "https://images-na.ssl-images-amazon.com/images/G/01/error/" + (Math.floor(Math.random() * 43) + 1) + "._TTD_.jpg";</script>
</div>
"""