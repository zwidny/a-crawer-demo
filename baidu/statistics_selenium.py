# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging  
from base64 import b64decode
from PIL import Image
from StringIO import StringIO
from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.common.by import By
from selenium.common import exceptions

import pytesseract


def screenshot(driver, element):
    im = Image.open(StringIO(b64decode(driver.get_screenshot_as_base64())))
    location, size = element.location, element.size
    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    return im.crop((left, top, right, bottom))


if __name__ == '__main__':

    def login(driver, username, password, wait):
        try:
            # get captcha
            captcha = wait.until(lambda _driver: _driver.find_element_by_id('cas_code'))
            captcha = pytesseract.image_to_string(screenshot(driver, captcha), config="-psm 8")
            logging.warning(captcha)
            # input
            driver.find_element(By.ID, 'UserName').clear()
            driver.find_element(By.ID, 'UserName').send_keys(username)
            driver.find_element(By.ID, 'Password').clear()
            driver.find_element(By.ID, 'Password').send_keys(password)
            driver.find_element(By.ID, 'Valicode').clear()
            driver.find_element(By.ID, 'Valicode').send_keys(captcha)
            # submit
            # driver.find_element(By.ID, 'Submit').click()
        except UnicodeDecodeError:
            driver.find_element(By.ID, 'Valicode').clear()
            driver.find_element(By.ID, 'Valicode').send_keys('')
        finally:
            submit_tag = wait.until(lambda _driver: _driver.find_element(By.ID, 'Submit'))
            submit_tag.click()


    def main(username=u"我们", password=u"Yndiwz1225"):
        # driver = webdriver.PhantomJS()
        driver = webdriver.Firefox()
        driver.set_page_load_timeout(15)
        try:
            url = 'http://tongji.baidu.com'
            driver.get(url)
        except exceptions.TimeoutException as e:
            logging.error(e.message, exc_info=True)

        _main(driver, password, username)


    def _main(driver, password, username):
        login_bth_css_selector = 'html body div.container div.constent div.tabs div.tab-list.span1 span.login-container a.no-select.dazzle-button.login-trigger'
        login_btn = driver.find_element_by_css_selector(login_bth_css_selector)
        login_btn.click()
        wait = ui.WebDriverWait(driver, 10)
        login(driver, username, password, wait)
        # 假设未登录成功
        logined = False
        body = wait.until(lambda _driver: _driver.find_element(By.TAG_NAME, 'body'))
        # 验证码输入为空或者输入错误的处理
        while not logined:
            try:
                # 验证码输入为空的处理
                if driver.find_element(By.ID, 'ErrorNoSubmit').is_displayed():
                    driver.find_element(By.ID, 'change_cas').click()
                    login(driver, username, password, wait)

                # 验证码输入错误的处理
                if body.find_element(By.ID, 'ErrorTip'):
                    login(driver, username, password, wait)
                    body = wait.until(lambda _driver: _driver.find_element(By.TAG_NAME, 'body'))
                if (not driver.find_element(By.ID, 'ErrorNoSubmit').is_displayed() and
                        not body.find_element(By.ID, 'ErrorTip')):
                    logined = True
            except exceptions.StaleElementReferenceException as e:
                logging.error(e.message, exc_info=True)
                login(driver, username, password, wait)
            except exceptions.NoSuchElementException as e:
                logging.error(e.message, exc_info=True)
                wait.until(lambda _driver: _driver.find_element(By.ID, 'ErrorNoSubmit'))
            except exceptions.TimeoutException as e:
                logging.error(e.message, exc_info=True)
            except Exception as e:
                logging.error(e.message, exc_info=True)
                break

    main()



