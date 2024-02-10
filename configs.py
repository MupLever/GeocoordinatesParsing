import os

from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("URL")

GECKODRIVER_PATH = os.getenv("GECKODRIVER_PATH")
ADDRESSES_FILE = os.getenv("ADDRESSES_FILE")
NEW_ADDRESSES_FILE = os.getenv("NEW_ADDRESSES_FILE")
