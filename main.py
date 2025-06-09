import os
from amazon_scraper import AmazonUPCProcessor


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_file_path = os.path.join(base_dir, 'src', 'csv', 'data.xlsx')
    results_file_path = os.path.join(base_dir, 'src', 'json', '03_amazon_data.json')
    proxies_file_path = os.path.join(base_dir, 'src', 'json', 'proxies.json')

    amazon_upc_processor = AmazonUPCProcessor(excel_file_path, results_file_path, proxies_file_path)
    amazon_upc_processor.start_driver()
    