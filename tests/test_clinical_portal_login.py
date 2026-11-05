import os
from dataclasses import dataclass

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@dataclass(frozen=True)
class PortalConfig:
    url: str
    username: str
    password: str
    username_selector: str
    password_selector: str
    submit_selector: str
    success_selector: str
    error_selector: str
    failure_username: str
    failure_password: str


def portal_config() -> PortalConfig:
    required = ("PORTAL_URL", "PORTAL_USERNAME", "PORTAL_PASSWORD")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        pytest.skip(
            "Set portal test configuration to run Selenium login tests: "
            + ", ".join(missing)
        )

    return PortalConfig(
        url=os.environ["PORTAL_URL"],
        username=os.environ["PORTAL_USERNAME"],
        password=os.environ["PORTAL_PASSWORD"],
        username_selector=os.getenv(
            "PORTAL_USERNAME_SELECTOR", "input[name='username']"
        ),
        password_selector=os.getenv(
            "PORTAL_PASSWORD_SELECTOR", "input[name='password']"
        ),
        submit_selector=os.getenv(
            "PORTAL_SUBMIT_SELECTOR", "button[type='submit']"
        ),
        success_selector=os.getenv(
            "PORTAL_SUCCESS_SELECTOR", "[data-testid='dashboard']"
        ),
        error_selector=os.getenv("PORTAL_ERROR_SELECTOR", "[role='alert']"),
        failure_username=os.getenv(
            "PORTAL_FAILURE_USERNAME", "invalid-user@example.invalid"
        ),
        failure_password=os.getenv(
            "PORTAL_FAILURE_PASSWORD", "not-a-valid-password"
        ),
    )


@pytest.fixture
def portal():
    config = portal_config()
    options = Options()
    if os.getenv("PORTAL_HEADLESS", "true").lower() in {"1", "true", "yes"}:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(0)
    try:
        yield driver, config
    finally:
        driver.quit()


def login(driver, config: PortalConfig, username: str, password: str) -> None:
    wait = WebDriverWait(driver, 10)
    driver.get(config.url)
    wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, config.username_selector))
    ).send_keys(username)
    wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, config.password_selector))
    ).send_keys(password)
    wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, config.submit_selector))
    ).click()


def test_successful_login_shows_authenticated_page(portal) -> None:
    driver, config = portal
    wait = WebDriverWait(driver, 10)

    login(driver, config, config.username, config.password)

    dashboard = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, config.success_selector))
    )
    assert dashboard.is_displayed()


def test_unsuccessful_login_shows_error(portal) -> None:
    driver, config = portal
    wait = WebDriverWait(driver, 10)

    login(
        driver,
        config,
        config.failure_username,
        config.failure_password,
    )

    error = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, config.error_selector))
    )
    assert error.is_displayed()
    assert error.text.strip()
    assert driver.find_element(
        By.CSS_SELECTOR, config.username_selector
    ).is_displayed()
