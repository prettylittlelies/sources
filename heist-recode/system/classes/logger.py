import logging
import sys
from datetime import datetime
from pathlib import Path

class Logger:
    def __init__(self):
        self.logger = logging.getLogger('Heist')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        self.clear_log_file()
        
        formatter = logging.Formatter(
            '(%(asctime)s) -> %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler = logging.FileHandler(
            filename="logs/bot.log",
            encoding='utf-8',
            mode='a'
        )
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def clear_log_file(self):
        with open("logs/bot.log", "w") as _:
            pass
    
    def debug(self, message: str) -> None:
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        self.logger.error(message)
