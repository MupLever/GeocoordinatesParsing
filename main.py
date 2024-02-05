import json
import re

from typing import Any
from selenium import webdriver
from selenium.webdriver import Firefox
# from selenium.webdriver import ActionChains
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from scrapy import Selector

from configs import GECKODRIVER_PATH, ADDRESSES_FILE, NEW_ADDRESSES_FILE
from utils import wait_until_text_on_page, get_parse_result

SECOND_TO_WAIT_INPUT = 20
SECOND_TO_WAIT_BUTTON = 20


def parse_coordinates(address: str, driver: Firefox) -> (float, float):
    input_xpath = (
        "//span[@class='input__context']/input[@placeholder='Поиск мест и адресов']"
    )
    try:
        WebDriverWait(driver, SECOND_TO_WAIT_INPUT).until(
            EC.presence_of_element_located((By.XPATH, input_xpath))
        )
    except TimeoutException:
        msg = "Error"
        print(msg)
        return None, None

    field = driver.find_element(by="xpath", value=input_xpath)
    field.send_keys("")
    field.send_keys(address)

    button_xpath = (
        "//div[@class='small-search-form-view__button']/button[@aria-label='Найти']"
    )
    try:
        WebDriverWait(driver, SECOND_TO_WAIT_BUTTON).until(
            EC.presence_of_element_located((By.XPATH, button_xpath))
        )
    except TimeoutException:
        msg = "Error"
        print(msg)
        return None, None

    button = driver.find_element(by="xpath", value=button_xpath)
    button.click()
    wait_until_text_on_page(driver=driver, texts=["Координаты:"], timeout=20)
    coordinates_pattern = re.compile(r"(?P<lat>.+), (?P<lng>.+)")
    data = Selector(text=driver.page_source)
    text = data.xpath(
        "//div[@class='clipboard__content']/div/div[@class='toponym-card-title-view__coords-badge']/text()"
    ).get()
    coordinates_info = get_parse_result(coordinates_pattern, text)
    lng = coordinates_info.get("lng", "")
    lat = coordinates_info.get("lat", "")
    return lng, lat


def main(url: str, driver: Firefox, **kwargs: Any) -> None:
    try:
        driver.get(url)
    except WebDriverException as exc:
        print(f"Can't get {url}: {exc}")
        return None

    with open(ADDRESSES_FILE, "r", encoding="utf-8") as readable_file:
        with open(NEW_ADDRESSES_FILE, "w+", encoding="utf-8") as writable_file:
            for line in readable_file:
                address_dict = json.loads(line)
                for house in address_dict["houses"]:
                    address = (
                        f"{address_dict['district']}, {address_dict['street']}, {house}"
                    )
                    lng, lat = parse_coordinates(address, driver)
                    new_address_dict = {
                        "district": address_dict["district"],
                        "street": address_dict["street"],
                        "house": house,
                        "lng": lng,
                        "lat": lat
                    }

                    writable_file.write(json.dumps(new_address_dict, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    service = Service(GECKODRIVER_PATH)
    driver = webdriver.Firefox(service=service)
    driver.maximize_window()
    main(
        url="https://yandex.ru/maps/213/moscow/",
        driver=driver,
    )
