import re
import json
import time
import logging

from random import random
from scrapy import Selector
from datetime import datetime
from selenium import webdriver
from typing import Optional, Tuple
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from configs import GECKODRIVER_PATH, ADDRESSES_FILE, NEW_ADDRESSES_FILE, URL
from utils import get_parse_result

SECOND_TO_WAIT_INPUT = 20
SECOND_TO_WAIT_BUTTON = 20

logging.basicConfig(
    level=logging.INFO,
    filename=f"{hash(datetime.utcnow().strftime('%Y%m%d%H%M%S'))}.log",
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("FireFox")


def parse_coordinates(
    address: str, driver: Firefox
) -> Tuple[str, Optional[str], Optional[str]]:
    input_xpath = (
        "//span[@class='input__context']/input[@placeholder='Поиск мест и адресов']"
    )
    try:
        WebDriverWait(driver, SECOND_TO_WAIT_INPUT).until(
            EC.presence_of_element_located((By.XPATH, input_xpath))
        )
    except TimeoutException:
        msg = "Timeout waiting for input to appear"
        return msg, None, None

    field = driver.find_element(by="xpath", value=input_xpath)
    field.clear()
    field.send_keys(address)

    button_xpath = (
        "//div[@class='small-search-form-view__button']/button[@aria-label='Найти']"
    )
    try:
        WebDriverWait(driver, SECOND_TO_WAIT_BUTTON).until(
            EC.presence_of_element_located((By.XPATH, button_xpath))
        )
    except TimeoutException:
        msg = f"{address} is not a valid address"
        return msg, None, None

    button = driver.find_element(by="xpath", value=button_xpath)
    button.click()

    timeout = random() * 2.5
    time.sleep(timeout)

    coordinates_pattern = re.compile(r"(?P<lat>.+), (?P<lng>.+)")

    data = Selector(text=driver.page_source)

    coordinates_item = data.xpath(
        "//div[@class='clipboard__content']/div/div[@class='toponym-card-title-view__coords-badge']/text()"
    ).get()

    coordinates_info = get_parse_result(coordinates_pattern, coordinates_item)

    lng = coordinates_info.get("lng", "")
    lat = coordinates_info.get("lat", "")

    return "", lng, lat


def main(url: str, driver: Firefox) -> None:
    try:
        driver.get(url)
    except WebDriverException as exc:
        logger.error(f"Can't get {url}: {exc}")
        return

    time.sleep(10)

    with open(ADDRESSES_FILE, "r", encoding="utf-8") as readable_file:
        with open(NEW_ADDRESSES_FILE, "a+", encoding="utf-8") as writable_file:
            for line in readable_file:
                address_dict = json.loads(line)
                district = (
                    address_dict["district"]
                    if any(
                        settlement in address_dict["district"]
                        for settlement in ["деревня", "посёлок"]
                    )
                    else "Москва"
                )
                address = f"{district}, {address_dict['street']}"
                error_message, lng, lat = parse_coordinates(address, driver)
                if error_message:
                    logger.error(error_message)
                    continue

                new_address_dict = {
                    "district": address_dict["district"],
                    "street": address_dict["street"],
                    "lng": lng,
                    "lat": lat,
                }
                logger.info(f"SUCCESS: {new_address_dict}")
                writable_file.write(
                    json.dumps(new_address_dict, ensure_ascii=False) + "\n"
                )


if __name__ == "__main__":
    service = Service(GECKODRIVER_PATH)
    driver = webdriver.Firefox(service=service)
    driver.maximize_window()
    main(
        url=URL,
        driver=driver,
    )
