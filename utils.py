import time

from re import Pattern
from typing import List, Dict, Union
from selenium.webdriver import Firefox
from selenium.webdriver.chromium.webdriver import ChromiumDriver


def wait_until_text_on_page(
        driver: Union[ChromiumDriver, Firefox],
        texts: List[str],
        timeout: float = 5,
        poll: float = 0.5,
) -> bool:
    """
    Ожидание, пока со страницы не появится какая-либо строка из texts
    :param driver: драйвер (ChromDriver)
    :param texts: строки для проверки на наличие присутствия на странице
    :param timeout: максимальное время ожидания
    :param poll: шаг времени
    :return: Правда, если строка появилась, и ложь, если никакой строки нет
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        if any(url in driver.page_source.lower() for url in texts):
            return True
        time.sleep(poll)

    return False


def get_parse_result(compiled_reg: Pattern, text: str) -> Dict:
    """
    :param compiled_reg: регулярка с параметрами
    :param text: текст, к которой будет применена регулярка
    :return: словарь с параметрами или пустой словарь
    """

    if not text:
        return {}

    searched_info = compiled_reg.search(text)
    return {} if searched_info is None else searched_info.groupdict()
