import re,time
from os import getenv
from push import tg_push
from chrome_test import chrome_test
from selenium.webdriver.common.by import By

if __name__ == '__main__':
    usr = getenv('USERNAME')
    pwd = getenv('PASSWORD')

    sl = chrome_test()
    sl.run()
    push = tg_push()
    sl.driver.find_element(By.XPATH, '//input[@name="appId"]').send_keys(usr)
    sl.driver.find_element(By.XPATH, '//input[@name="password"]').send_keys(pwd)
    sl.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    time.sleep(3)

    try:
        sl.driver.find_element(By.XPATH, '//*[@id="10000"]').click()
        sl.driver.find_element(By.XPATH, '//*[@id="tj"]').click()
        time.sleep(3)
        try:
            temp = sl.driver.find_element(By.XPATH, '//*[@style="text-align: center;margin-bottom: 100px"]').get_attribute("innerHTML")
            result = re.split("<[^\u4e00-\u9fa5]+>",temp)
            print(result)
            push.tg_push(text=result[1])
        except:
            try:
                temp = sl.driver.find_element(By.XPATH, '//*[@style="text-align: center;margin-bottom: 100px;margin-top: 17px"]').get_attribute("innerHTML")
                result = re.split("<[^\u4e00-\u9fa5]+>",temp)
                print(result)
                push.tg_push(text=result[1])
            except:
                push.tg_push(text="签到失败，未知错误")
        sl.driver.close()
    except:
        try:
            temp = sl.driver.find_element(By.XPATH, '//*[@style="text-align: center;margin-bottom: 100px"]').get_attribute("innerHTML")
            result = re.split("<[^\u4e00-\u9fa5]+>",temp)
            print(result)
            push.tg_push(text=result[1])
        except:
            try:
                temp = sl.driver.find_element(By.XPATH, '//*[@style="text-align: center;margin-bottom: 100px;margin-top: 17px"]').get_attribute("innerHTML")
                result = re.split("<[^\u4e00-\u9fa5]+>",temp)
                print(result)
                push.tg_push(text=result[1])
            except:
                push.tg_push(text="签到失败，未知错误")
        sl.driver.close()
