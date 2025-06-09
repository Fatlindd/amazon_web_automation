# Amazon Scraper Module Overview

This project consists of several Python modules designed to scrape product data from the Amazon website using UPC codes. Below is a brief description of each module and its key functionalities.

We have some Python Modules inside project for scraping Amazon website:
### 📄 main.py
    This module is designed to set up file paths and start the Amazon UPC scraping process using the AmazonUPCProcessor class. It ensures the necessary files are correctly located and prepares the environment for data extraction.

### 📄 amazon_scraper.py
    The amazon_scraper.py module is designed to automate the process of searching for products on Amazon using UPC codes, extracting detailed product information, and saving the results for further analysis. The module is built with the following key functionalities:
     - UPC Code Processing
     - Automated Product Search
     - Detailed Product Information Extraction
        For each product found, the module collects crucial information including:
         - ASIN (Amazon Standard Identification Number)
         - Price: Retrieves the current price and compares it with the original sales price for analysis.
         - Best Sellers Rank (BSR): Indicates the product's ranking within its category.
         - First Category: Identifies the primary category of the product.
         - Seller Information: Provides details about the seller offering the product.
     - Error Handling and Logging
     - Data Storage:
        - Saves the collected product details in both JSON and CSV formats. This facilitates easy access and integration with other systems or data analysis tools.
    - Category and Rank Extraction
    - Duplication Prevention

### 📄 utils/price_utils.py
    - The price_utils.py module provides essential functions for handling price data within the amazon_scraper.py

### 📄 utils/setup_logger.py
    - The logger_setup.py module is an integral part of the Amazon UPC Processor project, designed to streamline logging across the application. This module features the LoggerSetup class, which provides a robust framework for logging important events and errors during the scraping and data processing operations.

    Key Features:
     - Automated Log Directory Management: Automatically creates a dedicated log directory (src/logs/) to ensure that all logs are organized and easily accessible.
     - Flexible Logging Configuration
     - Clear and Concise Log Formatting
     File Handling: Ensures that log files are cleared before each run, preventing data from previous executions from cluttering the logs.

### 📄 utils/json_to_csv.py  
        - The save_json_to_csv function is designed to convert JSON data from a specified file into a CSV format. This is particularly useful for organizing and analyzing data extracted from sources like Amazon. 


### Structure of project is like below at the moment:
├── README.md
├── Tests
│   ├── __init__.py
│   └── test.py
├── amazon_scraper.py
├── main.py
├── src
│   ├── Backup
│   │   └── backup_amazon_scrapper.py
│   ├── csv
│   │   ├── 02_amazon_data.csv
│   │   ├── data.xlsx
│   │   └── final_amazon_details.csv
│   ├── json
│   │   ├── 02_amazon_data.json
│   │   ├── 03_amazon_data.json
│   │   └── proxies.json
│   └── logs
│       └── amazon_upc_processor.log
└── utils
    ├── __init__.py
    ├── json_to_csv.py
    ├── price_utils.py
    └── setup_logger.py