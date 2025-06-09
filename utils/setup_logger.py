"""
    logger_setup.py

    This module provides a LoggerSetup class to facilitate logging in Python applications.
    The LoggerSetup class allows for easy configuration of logging to a file, including 
    creating the log directory, setting the logging level, and formatting log messages.

    Classes:
        LoggerSetup: A class to set up and manage a logger that logs messages to a specified file.

    Usage:
        To use the LoggerSetup class, create an instance of the class and call the 
        setup_logger method to initialize logging. For example:

        >>> logger_setup = LoggerSetup()
        >>> logger_setup.setup_logger()
        >>> logger_setup.logger.info("Logger is set up and ready to log.")
"""

import os
import logging


class LoggerSetup:
    def __init__(self):
        """Initialize the LoggerSetup class."""
        self.logger = None

    def setup_logger(self, level: int = logging.INFO) -> None:
        """
            Set up the logger to log messages to a file.

            This method configures a logger that writes log messages to a 
            specified log file. It creates the necessary directory if it 
            does not exist, clears any existing log file content, and sets 
            up the logger with the specified logging level.

            Parameters:
                level (int): The logging level to set for the logger. 
                            Default is logging.INFO.

            Returns:
                None: This method does not return any value.
        """
        log_dir = 'src/logs/'
        # Create the directory if it does not exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file_path = os.path.join(log_dir, 'amazon_upc_processor.log')

        # Clear the log file before adding new logs
        with open(log_file_path, "w") as file:
            file.write("")  # This effectively clears the file content

        # Remove any existing handlers to avoid duplication
        if self.logger is not None and self.logger.hasHandlers():
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
                handler.close()

        # Create a logger
        self.logger = logging.getLogger("default")
        self.logger.setLevel(level)

        # Create and configure the file handler
        file_handler = logging.FileHandler(
            log_file_path, mode="w"
        )  # Mode 'w' clears the file
        file_handler.setLevel(level)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
