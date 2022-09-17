# coding=UTF-8
import argparse
import json
import os
import platform
import time

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

### 使用的人先改這邊 我懶得寫成config ###
INLINE_URL = "" # Inline訂位頁面
ADULT_NUM = "3"
CHILDREN_NUM = "1"
BOOKING_DATE = "2022-09-25" # yyyy-MM-dd
SLACK_HOOK_URL = "" # Slack hook url using incoming-webhooks
SLACK_HOOK_CHANNEL = "" # 訊息要打到的slack channel
SLACK_MENTION_USER_ID = "" # 有位子時要mention誰
BOOKING_NAME = "" # 餐廳名稱
JOB_TIME_INTERVAL = 10 # 間隔多久查一次, 單位為秒
########


def main():
    driver_path = get_chrome_driver()

    driver = get_driver(driver_path)
    start_new_session(driver, INLINE_URL)

    while True:
        try:
            routine(driver)
        except Exception as e:
            print(e)
            pass
        time.sleep(JOB_TIME_INTERVAL)

def routine(driver):
    select_adult_num(driver, ADULT_NUM)
    select_children_num(driver, CHILDREN_NUM)
    select_booking_date(driver, BOOKING_DATE)
    check_availability(driver, BOOKING_DATE, SLACK_HOOK_URL, SLACK_HOOK_CHANNEL, SLACK_MENTION_USER_ID, INLINE_URL, BOOKING_NAME)
    driver.refresh()


def select_adult_num(driver, num):
    picker = Select(WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "adult-picker")))
    )

    picker.select_by_value(num)

def select_children_num(driver, num):
    picker = Select(WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "kid-picker")))
    )

    picker.select_by_value(num)


def select_booking_date(driver, date):
    date_picker_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "date-picker"))
    )
    date_picker_btn.click()

    date_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR,
                                        'div[data-date=\"'+date+'\"] > span'))
    )
    try:
        driver.execute_script("arguments[0].click();", date_btn)
    except Exception:
        pass

def check_availability(driver, date, slack_hook_url, slack_hook_channel, slack_mention_user_id, inline_url, booking_name):
    available_time = None
    try:
        available_time = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            'button[aria-label*=\"' + date + '\"]'))
        )
    except TimeoutException:
        pass

    if available_time:
        print("Available!")
        payload = "{\"channel\": \"#%s\", \"username\": \"webhookbot\", \"text\": \"[%s] Available in Inline! <%s> <%s |Click here>\", \"icon_emoji\": \":ghost:\"}" % (slack_hook_channel, booking_name, slack_mention_user_id, inline_url)
        r = requests.post(slack_hook_url, data={"payload": payload.encode()})
    else:
        print("Not available!")
        # payload = "{\"channel\": \"#%s\", \"username\": \"webhookbot\", \"text\": \"[%s] Not available seat in Inline\", \"icon_emoji\": \":ghost:\"}" % (slack_hook_channel, booking_name)
        # r = requests.post(slack_hook_url, data={"payload": payload.encode()})

def start_new_session(driver, url):
    driver.get(url)

def get_chrome_driver():
    driver_path = os.path.dirname(os.path.abspath(__file__)) + '/driver/'
    if platform.system() == 'Windows':
        return driver_path + "win32/chromedriver.exe"
    elif platform.system() == 'Darwin':
        return driver_path + "mac64/chromedriver"
    else:
        raise Exception('Not supported os')


def get_driver(driver_path):
    driver = webdriver.Chrome(driver_path)
    return driver

def load_json(path):
    with open(path, 'r', encoding='UTF-8') as f:
        content = json.load(f)

    return content


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple Inline booking notifier')

    args = parser.parse_args()

    main()
