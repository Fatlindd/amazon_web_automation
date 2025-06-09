import json
import csv
import os

def save_json_to_csv(json_results_file, csv_file):
    # Ensure the directory structure exists
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    
    # Load the JSON data from the file
    try:
        with open(json_results_file, 'r') as file:
            # Check if the file is empty
            if file.readable():
                data = json.load(file)
            else:
                print(f"Error: The file '{json_results_file}' is empty.")
                return
    except FileNotFoundError:
        print(f"Error: The file '{json_results_file}' does not exist.")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON. {e}")
        return
    
    # Define the CSV columns
    columns = ["UPC", "Zoro_No", "URL", "ASIN", "BSR", "Price", "Price difference", "First Category", "Seller"]
    
    # Open the CSV file and write the data
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        
        # Write the header
        writer.writeheader()
        
        # Write the data rows
        for item in data:
            writer.writerow({
                "UPC": item.get("UPC"),
                "Zoro_No": item.get("Zoro_No"),
                "URL": item.get("url"),
                "ASIN": item.get("ASIN"),
                "BSR": item.get("BSR"),
                "Price": item.get("Price"),
                "Price difference": item.get("Price difference"),
                "First Category": item.get("First Category"),
                "Seller": item.get("Seller")
            })

# Call the function to save JSON data to CSV
# save_json_to_csv('02_amazon_data.json', 'src/csv/amazon_data.csv')
