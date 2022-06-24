# -*- encoding: utf-8 -*-
import os
import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pyvirtualdisplay import Display

from yidun import yidun_crack
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--start-maximized")


class chrome_test(object):
    def __init__(self):
        display = Display(visible=0, size=(800, 600))
        display.start()
        chrome_options = webdriver.ChromeOptions()
        '''chrome_options.add_argument('--headless')'''
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chromedriver = "/usr/bin/chromedriver"
        os.environ["webdriver.chrome.driver"] = chromedriver
        self.driver = webdriver.Chrome(options=chrome_options,executable_path=chromedriver)
        self.driver.get('https://stuhealth.jnu.edu.cn/#/login')
        # self.driver.get('https://dun.163.com/trial/jigsaw')
        # self.driver.get('http://localhost:63342/yidun/slider.html?_ijt=1v4ljncju1r9naf69h6p4nt0k6')

    def run(self):
        # 网页异步加载，等待拖动按钮出现
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'yidun_slider'))
        )
        time.sleep(2)
        button_element = self.driver.find_element_by_class_name('yidun_slider')
        ActionChains(self.driver).move_to_element(button_element).perform()
        # 下载验证码进行识别
        yidun = yidun_crack()
        bg_img_src = self.driver.find_element_by_class_name("yidun_bg-img").get_attribute("src")
        bg_img_path = yidun.download_img(bg_img_src)
        front_img_src = self.driver.find_element_by_class_name("yidun_jigsaw").get_attribute("src")
        front_img_path = yidun.download_img(front_img_src)
        yidun.bg_img_path = bg_img_path
        yidun.front_img_path = front_img_path
        distance = yidun.tell_location()
        tracks = yidun.generate_tracedata(distance)
        print(tracks)
        # 进行拖动
        ActionChains(self.driver).click_and_hold(button_element).perform()
        t1 = int(time.time() * 1000)
        for i in range(len(tracks)):
            x = tracks[i]
            x_offset = x[0] if i == 0 else x[0] - tracks[i - 1][0]  # x轴距离差
            y_offset = x[1]
            ActionChains(self.driver).move_by_offset(x_offset, y_offset).perform()
            t = int(time.time() * 1000) - t1
            print(t, x_offset)
            tracks[i][2] = t
        ActionChains(self.driver).release().perform()
        time.sleep(2)
        if (self.driver.find_element_by_xpath('//*[@class="yidun_tips__text yidun-fallback__tip"]').get_attribute("innerHTML") == '向右拖动滑块填充拼图'):
            print('滑动验证不通过，正在重试')
            # self.driver.refresh()
            self.run()
        else:
            print(self.driver.find_element_by_xpath('//*[@class="yidun_tips__text yidun-fallback__tip"]').get_attribute("innerHTML") + '滑动验证通过')

    #def __del__(self):
    #    self.driver.close()


if __name__ == '__main__':
    c = chrome_test()
    c.run()
