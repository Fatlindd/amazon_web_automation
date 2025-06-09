from utils.setup_logger import LoggerSetup

logger_setup = LoggerSetup()  # Create an instance of LoggerSetup
logger_setup.setup_logger()  # Set up the logger
logger = logger_setup.logger  # Access the logger


def format_price(price: str) -> str:
    """
        Format a price string to a standardized decimal format.

        This method takes a price string, removes any dollar signs and 
        currency indicators, and formats it into a standard decimal form. 
        If the price contains multiple parts separated by line breaks, 
        it concatenates them into a valid price format.

        Args:
            price (str): The price string to format, which may include 
                        dollar signs and other non-numeric characters.

        Returns:
            str: The formatted price as a string in decimal format.
    """
    price_text = price.strip().replace('$', '').replace('UHD', '').strip()
    price_parts = price_text.split('\n')
    correct_price = f"{price_parts[0].strip()}.{price_parts[1].strip()}" if len(price_parts) == 2 else price_text

    return correct_price
    

def get_price_difference(price: str, zoro_price: str) -> float:
    """
        Calculate the price difference between a given price and a Zoro price adjusted for a specific factor.

        This method performs the following steps:
        1. Converts the input prices from strings to floats.
        2. Computes the price difference based on the following conditions:
            - If the Zoro price is greater than 50, an additional 5 is added to the Zoro price before adjustment.
            - Otherwise, the Zoro price is adjusted by multiplying it by a constant factor (1.203).
        3. Returns the computed price difference.

        Args:
            price (str): The price from the primary source as a string.
            zoro_price (str): The price from Zoro as a string.

        Returns:
            float: The calculated price difference.
                If an error occurs during conversion, returns 'N/A'.
    """
    try:
        price, zoro_price = float(price), float(zoro_price)
        diff = price - zoro_price * 1.203
        if zoro_price > 50:
            diff = price - ((zoro_price + 5) * 1.203)
        return diff
    except ValueError:
        logger.error(f"Something went wrong during conversion for the price: {price}")
        return 'N/A'
