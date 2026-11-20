import uuid

import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")

    browser = webdriver.Chrome(options=options)
    yield browser
    browser.quit()


def add_task(driver, text, priority="Medium"):
    driver.find_element(By.ID, "task-input").send_keys(text)
    driver.find_element(By.ID, "priority-select").send_keys(priority)
    driver.find_element(By.ID, "add-task").click()


def find_task(driver, text):
    return driver.find_element(
        By.XPATH,
        f"//li[@data-testid='task-item'][.//span[@class='task-text' and text()='{text}']]",
    )


def test_add_task_with_priority(driver):
    driver.get(BASE_URL)
    text = f"Test task {uuid.uuid4()}"

    add_task(driver, text, "High")
    time.sleep(2)

    wait = WebDriverWait(driver, 5)
    task = wait.until(lambda d: find_task(d, text))
    assert "(High)" in task.text


def test_complete_task_and_filter_completed(driver):
    driver.get(BASE_URL)
    text = f"Complete me {uuid.uuid4()}"
    add_task(driver, text)
    time.sleep(2)

    wait = WebDriverWait(driver, 5)
    task = wait.until(lambda d: find_task(d, text))
    task.find_element(By.CLASS_NAME, "toggle-task").click()

    completed_task = wait.until(
        EC.visibility_of_element_located((
            By.XPATH,
            f"//li[@data-testid='task-item' and @data-status='completed']"
            f"[.//span[@class='task-text' and text()='{text}']]",
        ))
    )

    driver.find_element(By.CSS_SELECTOR, "[data-filter='completed']").click()
    assert completed_task.is_displayed()


def test_search_shows_matching_task(driver):
    driver.get(BASE_URL)
    text = f"Searchable {uuid.uuid4()}"
    add_task(driver, text)
    time.sleep(2)

    wait = WebDriverWait(driver, 5)
    task = wait.until(lambda d: find_task(d, text))
    driver.find_element(By.ID, "search-input").send_keys(text)

    wait.until(lambda _: task.is_displayed())
    assert task.is_displayed()


def test_delete_task(driver):
    driver.get(BASE_URL)
    text = f"Delete me {uuid.uuid4()}"
    add_task(driver, text)
    time.sleep(2)

    wait = WebDriverWait(driver, 5)
    task = wait.until(lambda d: find_task(d, text))
    task.find_element(By.CLASS_NAME, "delete-task").click()

    wait.until(EC.staleness_of(task))
    assert text not in driver.page_source
