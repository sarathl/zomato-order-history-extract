import pandas as pd
import numpy as np
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait



def get_orders_displayed(showing_el):
    temp = re.search('Showing (.*?) of', showing_el.text).group(1)
    return int(temp.split("-")[-1]), int(temp.split("-")[0])


def get_total_orders(showing_el):
    temp = re.search('of (.*?) orders', showing_el.text).group(1)
    return int(temp)


def get_profile_url(page_source):
    return re.search(r'profile_url\\":\\"(.*?)\\",\\"profile_picture', page_source).group(1)


def check_if_last_page(total_orders, max_order_displayed):
    if max_order_displayed == total_orders:
        return 1
    return 0


def quit_driver(driver):
    try:
        driver.quit()
    except:
        pass


def login(driver):
    driver.get('https://www.zomato.com/')
    login_xpath = '/html/body/div[1]/div/div[2]/header/nav/ul[2]/li[3]/a'
    try:
        login_button = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, login_xpath)))
        login_button.click()
    except:
        try:
            profile_xpath = '/html/body/div[1]/div/div[2]/header/nav/ul[2]/li[3]/div/div/div[1]/span'
            profile_xpathbutton = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, profile_xpath)))
            print("Already signed in")
            profile_url = get_profile_url(driver.page_source)
            driver.get('https://www.zomato.com{}/ordering'.format(profile_url))
            return driver
        except:
            print("Some issue with finding login button")
        return 0
    
    print("Input Phone number")
    phone_num = input()
    ph_input_xpath = '/html/body/div[4]/div/div[2]/section[2]/section/div[1]/div/input'
    ph_input = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, ph_input_xpath)))
    ph_input.send_keys(phone_num)
    
    send_otp_xpath = '/html/body/div[4]/div/div[2]/section[2]/section/button/span'
    send_otp = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, send_otp_xpath)))
    send_otp.click()
    
    print("Input OTP")
    otp = str(input())
    for otp_digit, otp_box in zip(list(otp), driver.find_elements_by_class_name('sc-hp56s6-1')):
        otp_box.send_keys(otp_digit)
        print("Typed digit {}".format(otp_digit))
    print("Done typing OTP")
    time.sleep(2)
    profile_url = get_profile_url(driver.page_source)
    driver.get('https://www.zomato.com{}/ordering'.format(profile_url))
    return driver


def extract_orders(driver, df_list):
    driver = login(driver)
    print(driver)
    if driver != 0:
        driver.get('https://www.zomato.com/users/sarath-lavu-76481316/ordering')
        showing_xpath = '/html/body/div[1]/div/main/div/div[2]/div[2]/section/div/div[2]/div[1]'
        showing_el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, showing_xpath)))
        total_orders = get_total_orders(showing_el)
        page_num = 1
        order_count = 0
        while True:
            showing_xpath = '/html/body/div[1]/div/main/div/div[2]/div[2]/section/div/div[2]/div[1]'
            showing_el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, showing_xpath)))
            max_order, min_order = get_orders_displayed(showing_el)
            num_orders = max_order - min_order + 1
            print("Number of orders displayed in this page = {}".format(num_orders))
            for i in range(1, num_orders + 1):
                time.sleep(0.5)
                order_count+= 1
                order_xpath = '/html/body/div[1]/div/main/div/div[2]/div[2]/section/div/div[1]/div[{}]'.format(i)
                order_el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, order_xpath)))
                df_list.append(order_el.text.split("\n"))
                print("Data extracted for order number {}".format(order_count))
            page_row_xpath = '/html/body/div[1]/div/main/div/div[2]/div[2]/section/div/div[2]/div[2]/div'
            page_row = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, page_row_xpath)))
            print("Data Extracted for page {}".format(page_num))
            page_num += 1
            if check_if_last_page(total_orders, max_order):
                print("This is the last page")
                break
            else:
                page_row.find_elements_by_xpath('./*')[-1].click()
            time.sleep(2)
    else:
        print("Some issue with the process of login")
    # quit_driver(driver)
    return df_list

if __name__ == "__main__":
    exe_path = 'C:\\Users\\SHRI\\Downloads\\chromedriver.exe'
    timeout = 10
    driver = webdriver.Chrome(executable_path=exe_path)

    df_list = []
    df_list = extract_orders(driver, df_list)

    pd.DataFrame(df_list).to_csv('Zomato Order History.csv', index=False)

