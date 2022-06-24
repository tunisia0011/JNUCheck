import re
from os import getenv
import time, requests
from chrome_test import chrome_test
from selenium.webdriver.common.by import By

def tg_push(text):
    push_url = 'https://api.telegram.org/bot' + BOTTOKEN + '/sendMessage?chat_id=' + TGCHATID + '&text=' + text
    rPush = requests.get(push_url)
    if rPush.status_code == 200 :
        print('推送成功')
    elif rPush.status_code == 400 :
        print('CHATID 填写有误')
    else :
        print('推送失败，未知错误')

if __name__ == '__main__':
    TGCHATID = getenv('TGCHATID')
    BOTTOKEN = getenv('BOTTOKEN')
    usr = getenv('USERNAME')
    pwd = getenv('PASSWORD')

    sl = chrome_test()
    sl.run()
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
            tg_push(text=result[1])
        except:
            try:
                temp = sl.driver.find_element(By.XPATH, '//*[@style="text-align: center;margin-bottom: 100px;margin-top: 17px"]').get_attribute("innerHTML")
                result = re.split("<[^\u4e00-\u9fa5]+>",temp)
                print(result)
                tg_push(text=result[1])
            except:
                tg_push(text="签到失败，未知错误")
        sl.driver.close()
    except:
        try:
            temp = sl.driver.find_element(By.XPATH, '//*[@style="text-align: center;margin-bottom: 100px"]').get_attribute("innerHTML")
            result = re.split("<[^\u4e00-\u9fa5]+>",temp)
            print(result)
            tg_push(text=result[1])
        except:
            try:
                temp = sl.driver.find_element(By.XPATH, '//*[@style="text-align: center;margin-bottom: 100px;margin-top: 17px"]').get_attribute("innerHTML")
                result = re.split("<[^\u4e00-\u9fa5]+>",temp)
                print(result)
                tg_push(text=result[1])
            except:
                tg_push(text="签到失败，未知错误")
        sl.driver.close()
