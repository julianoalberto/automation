import logging
import netrc
import os
import pathlib

from pyexpat.errors import messages
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait

import logging

logger = logging.getLogger("irs_status")
logging.basicConfig(level=logging.INFO)


NETRC_PATH = pathlib.Path(os.environ.get("HOME"), ".netrc")
NETRC = netrc.netrc(NETRC_PATH)

HOST = "portaldasfinancas.gov.pt"
LOGIN_URL = f"https://irs.{HOST}/v2/loginForm?partID=PFAP"
STATUS_URL = f"https://irs.{HOST}/app/consulta"


def get_status(browser):
    logger.debug("Going to status page %s", STATUS_URL)
    browser.get(STATUS_URL)

    WebDriverWait(browser, timeout=30).until(
        lambda x: x.find_element(
            By.XPATH,
            "/html/body/div/main/div/div[2]/div/section/div[5]/div/div/table/tbody/tr/td[1]/p",
        )
    )

    year = browser.find_element(
        By.XPATH,
        "/html/body/div/main/div/div[2]/div/section/div[5]/div/div/table/tbody/tr/td[2]",
    ).text

    status = browser.find_element(
        By.XPATH,
        "/html/body/div/main/div/div[2]/div/section/div[5]/div/div/table/tbody/tr/td[1]/p",
    ).text

    value = browser.find_element(
        By.XPATH,
        "/html/body/div/main/div/div[2]/div/section/div[5]/div/div/table/tbody/tr/td[4]",
    ).text

    logger.debug("Got status: year:%s|statustatus:%s|value:%s", year, status, value)

    return f"Status:\t{status}\nYear:\t{year}\nValue:\t{value}"


def browser_login(login_url, headless=True):
    logger.debug("Logging into %s", LOGIN_URL)
    options = Options()
    options.headless = headless

    browser = Firefox(options=options)

    browser.get(login_url)

    WebDriverWait(browser, timeout=30).until(
        lambda x: x.find_element(By.ID, "sbmtLogin")
    )

    button = browser.find_element(By.ID, "sbmtLogin")
    user = browser.find_element(By.ID, "username")
    password = browser.find_element(By.ID, "password-nif")

    user.send_keys(NETRC.hosts[HOST][0])
    password.send_keys(NETRC.hosts[HOST][2])
    button.click()

    logger.debug("Logged into %s", LOGIN_URL)
    return browser


def main():
    print("Getting status...")
    browser = None
    try:
        browser = browser_login(LOGIN_URL)
        status = get_status(browser)
        print(status)
    finally:
        if browser:
            browser.close()


if __name__ == "__main__":
    main()
