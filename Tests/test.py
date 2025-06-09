# # import pandas as pd


# # def split_excel_data(file_path):
# #     # Read the data from the main Excel file
# #     df = pd.read_excel(file_path)

# #     # Define row ranges and corresponding output filenames
# #     ranges = {
# #         'data/data1.xlsx': (100, 200),  # Rows 101-201
# #         'data/data2.xlsx': (200, 300),  # Rows 201-301
# #         'data/data3.xlsx': (300, 400),  # Rows 301-401
# #         'data/data4.xlsx': (400, 500)  # Rows 401-500
# #     }

# #     # Loop through the defined ranges and save to new Excel files
# #     for file_name, (start, end) in ranges.items():
# #         # Extract the relevant rows and save to a new Excel file
# #         df.iloc[start:end].to_excel(file_name, index=False)


# # # Call the function with your data file path
# # split_excel_data('data/data.xlsx')

# # import pandas as pd
# # import json
# #
# # # Step 1: Read the Excel file
# # excel_data = pd.read_excel('data/data.xlsx')
# # upc_codes = set(excel_data['upc_code'].astype(str))  # Use set for faster lookup
# #
# # # Step 2: Load the JSON file
# # with open('updated_new_data.json', 'r') as file:
# #     json_data = json.load(file)
# #
# # # Step 3: Filter the JSON data
# # filtered_data = [entry for entry in json_data if entry['UPC'] in upc_codes]
# #
# # # Step 4: Write the filtered data back to JSON (if needed)
# # with open('updated_new_data.json', 'w') as file:
# #     json.dump(filtered_data, file, indent=4)
# #
# # print("Filtered JSON data saved.")
# #



# # import pandas as pd
# #
# #
# # def count_upcs_starting_with_zero(file_path):
# #     # Load the Excel file with UPC codes as strings
# #     data = pd.read_excel(file_path, dtype={'upc_code': str})
# #
# #     # Count the number of UPC codes that start with '0'
# #     count = sum(upc.startswith('0') for upc in data['upc_code'] if pd.notna(upc))
# #
# #     # Print the result
# #     print(f"Number of UPC codes starting with '0': {count}")
# #
# #
# # # Example usage
# # file_path = 'data/data.xlsx'  # Update this with your actual file path
# # count_upcs_starting_with_zero(file_path)



# # import json
# # import pandas as pd
# #
# # # Load the JSON file
# # json_file_path = 'new_data.json'  # Update this with your actual file path
# # with open(json_file_path, 'r') as file:
# #     json_data = json.load(file)
# #
# # # Load the Excel file
# # excel_file_path = 'data/data.xlsx'  # Update this with your actual file path
# # data = pd.read_excel(excel_file_path, dtype={'upc_code': str})
# #
# # # Convert the data DataFrame to a dictionary for faster lookup
# # upc_to_zoro_no = dict(zip(data['upc_code'], data['zoro_no']))
# #
# # # Update the JSON data with the corresponding zoro_no
# # for item in json_data:
# #     upc = item['UPC']
# #     if upc in upc_to_zoro_no:
# #         item['zoro_no'] = upc_to_zoro_no[upc]
# #     else:
# #         item['zoro_no'] = 'N/A'  # If no match found, set it to 'N/A'
# #
# # # Save the updated JSON data back to the file
# # updated_json_file_path = 'updated_new_data.json'  # Update this if needed
# # with open(updated_json_file_path, 'w') as file:
# #     json.dump(json_data, file, indent=4)
# #
# # print(f"Updated JSON file saved to {updated_json_file_path}")



# # import pandas as pd

# # class DataReader:
# #     def __init__(self, file_path):
# #         self.file_path = file_path

# #     def read_excel(self):
# #         # Read the Excel file with 'upc_code' as string
# #         try:
# #             df = pd.read_excel(self.file_path, dtype={'upc_code': str})

# #             # Check if the 'upc_code' column exists
# #             if 'upc_code' in df.columns:
# #                 # Print all UPC codes
# #                 upc_codes = df['upc_code'].tolist()
# #                 for upc in upc_codes:
# #                     print(upc)
# #             else:
# #                 print("Column 'upc_code' not found in the Excel file.")
# #         except Exception as e:
# #             print(f"Error reading the Excel file: {e}")

# # # Example usage
# # if __name__ == "__main__":
# #     reader = DataReader('data/data.xlsx')
# #     reader.read_excel()

# # import pandas as pd
# # import os

# # def read_excel(last_upc=None, start_row=100, end_row=200):
# #     if os.path.exists(excel_file_path):
# #         # Read the Excel file with 'upc_code' as string
# #         df = pd.read_excel(excel_file_path, dtype={'upc_code': str})

# #         # If start_row and end_row are specified, slice the DataFrame
# #         if start_row is not None and end_row is not None:
# #             # Ensure the row indices are within the range of the DataFrame
# #             if start_row < 0:
# #                 start_row = 0
# #             if end_row > len(df):
# #                 end_row = len(df)
            
# #             # Slice the DataFrame from start_row to end_row
# #             df = df.iloc[start_row:end_row]
# #             print(f"DataFrame rows from {start_row} to {end_row}:")
# #             print(df)
            
# #             # Print all UPC codes in this range
# #             upc_codes = df['upc_code'].tolist()
# #             print("UPC codes in the specified range:")
# #             print(upc_codes)
# #             return df

# #         if last_upc is not None:
# #             # Ensure last_upc is a string for comparison
# #             target_upc_code = str(last_upc)  # The UPC code you are looking for
# #             index = df.index[df['upc_code'] == target_upc_code]

# #             if not index.empty:
# #                 # Get the next index if it exists
# #                 next_index = index[0] + 1
# #                 if next_index < len(df):
# #                     # Slice the DataFrame from the next index
# #                     df_from_target = df.loc[next_index:]
# #                     print("DataFrame starting from the next UPC code:")
# #                     print(df_from_target)
# #                     return df_from_target
# #                 else:
# #                     print("No more UPC codes available after the specified UPC.")
# #                     return df.iloc[0:0]  # Return an empty DataFrame
# #             else:
# #                 print(f"UPC code {target_upc_code} not found.")
# #                 return df
# #         else:
# #             # No last UPC found, return the whole DataFrame
# #             print("No last UPC code found, returning all data from Excel.")
# #             return df
# #     else:
# #         print(f"Excel file not found at: {excel_file_path}")
# #         return None

# # Example usage
# # base_dir = os.path.dirname(os.path.abspath(__file__))  
# # excel_file_path = os.path.join(base_dir, 'data', 'data.xlsx')
# # read_excel(last_upc=None, start_row=300, end_row=400)


# # import pandas as pd

# # # Read the data from the Excel file, ensuring upc_code is read as a string
# # file_path = 'data/data.xlsx'  # Replace with your actual file path
# # data = pd.read_excel(file_path, dtype={'upc_code': str})

# # # Check the first few rows of the dataframe to understand its structure
# # print(data.head())

# # # Filter upc_code less than 12 digits in length
# # short_upc_codes = data[data['upc_code'].str.len() < 12]['upc_code']

# # # Print the filtered UPC codes
# # print("UPC codes less than 12 digits long:")
# # count = 0
# # for code in short_upc_codes:
# #     count += 1
# #     print(f"{code}, {len(str(code))}")

# # print(f"Number of upc_codes: {count}")

def get_price_difference(price, zoro_price):
        try:
            price, zoro_price = float(price), float(zoro_price)
            diff = price - zoro_price * 1.203
            if zoro_price > 50:
                diff = price - ((zoro_price + 5) * 1.203)
            return diff
        except ValueError:
            return 'N/A'
        

# print(get_price_difference('45.07', '28.52'))



import time
import random
import undetected_chromedriver as uc

from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.json_to_csv import save_json_to_csv



# driver = webdriver.Chrome()

# # driver.get("https://www.amazon.com/Man-Betrayed-Blu-ray-John-Wayne/dp/B00B1CGEI8/ref=sr_1_1_sspa?keywords=190735983966&qid=1729141031&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9idGY&psc=1")
# # driver.get("https://www.amazon.com/Man-Betrayed-Blu-ray-John-Wayne/dp/B00B1CGEI8/ref=sr_1_1_sspa?keywords=190735983966&qid=1729141031&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9idGY&psc=1")

# driver.get("https://www.amazon.com/")
# time.sleep(10)
# wait = WebDriverWait(driver, 3)

# def format_price(price):
#         price_text = price.strip().replace('$', '').replace('UHD', '').strip()
#         price_parts = price_text.split('\n')
#         correct_price = f"{price_parts[0].strip()}.{price_parts[1].strip()}" if len(price_parts) == 2 else price_text

#         return correct_price

# def test_get_price():
#     price_found = False
#     try:
#         price_elem = driver.find_element(By.CSS_SELECTOR, "#buybox-see-all-buying-choices .a-button-text")
#         price_elem.click()
#         time.sleep(3)

#         price_text = driver.find_element(By.CSS_SELECTOR, ".a-section.a-spacing-none.aok-align-center.aok-relative")
#         price_to_format = price_text.text
#         price = format_price(price_to_format)

#         print(f"Price: {price}")
#         price_found = True
#     except:
#         print("We can not get price with clicking right window...")

#     if not price_found:
#         price_xpaths = [
#             "(//div[@class='a-spacing-top-mini']/span)[1]",
#             "(//span[@class='a-price aok-align-center reinventPricePriceToPayMargin priceToPay'])[1]",
#             "(//div[@class='a-section a-spacing-micro']/span)[1]",
#             "(//div[@class='a-section a-spacing-none aok-align-center aok-relative']/span)[1]",
#             "(//span[@class='slot-price']/span)[1]",
#             "//span[@id='kindle-price']"
#             "//span[contains(text(),'Buy')]",
#             "//*[(@id = 'tvod-btn-ab-movie-hd-tvod_purchase')]//*[contains(concat( " ", @class, " " ), concat( " ", '_36qUej', " " ))]"
#         ]
#         for price_xpath in price_xpaths:
#             try:
#                 price_elem = wait.until(
#                     EC.presence_of_element_located((By.XPATH, price_xpath))
#                 )
#                 price_text = price_elem.text
#                 price = format_price(price_text)

#                 try:
#                     price_value = float(price)
#                     print(f"Price found: {price_value}")
#                     break
#                 except ValueError:
#                     print(f"Invalid price format: {price}")
#                     price = "N/A"  # Continue searching
#             except:
#                 price = "N/A"

# test_get_price()


# import pandas as pd

# # Read the Excel file with 'upc_code' as a string
# df_read = pd.read_excel('test_data.xlsx', dtype={'upc_code': str})

# # Display the DataFrame to verify
# upc_codes = df_read['upc_code']
# print(upc_codes)


def is_page_active():
    # Get the title of the page
    page_title = driver.title
    print(f"Title: {page_title}")

    # Check if the title starts with the specified text
    if page_title.startswith("Sorry!"):
        print("\n\n!!!We are blocked by Amazon. Please try again later!!!\n\n")


driver = webdriver.Chrome()
driver.get("https://www.amazon.com/s?k=087302660521&crid=3LZVTLCLZQ1CH&sprefix=087302660521%2Caps%2C163&ref=nb_sb_noss")

is_page_active()
print("We are refresh the page...")
time.sleep(3)
driver.refresh()
time.sleep(100)

"""

<title>Sorry! Something went wrong!</title>

<div id="g">
  <div><a href="/ref=cs_503_link"><img src="https://images-na.ssl-images-amazon.com/images/G/01/error/500_503.png" alt="Sorry! Something went wrong on our end. Please go back and try again or go to Amazon's home page."></a>
  </div>
  <a href="/dogsofamazon/ref=cs_503_d" target="_blank" rel="noopener noreferrer"><img id="d" alt="Dogs of Amazon" src="https://images-na.ssl-images-amazon.com/images/G/01/error/22._TTD_.jpg"></a>
  <script>document.getElementById("d").src = "https://images-na.ssl-images-amazon.com/images/G/01/error/" + (Math.floor(Math.random() * 43) + 1) + "._TTD_.jpg";</script>
</div>
"""