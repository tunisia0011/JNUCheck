import os
from os import getenv
import re
import cv2
import numpy as np
from io import BytesIO
import time, requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

class CrackSlider():
    """
    通过浏览器截图，识别验证码中缺口位置，获取需要滑动距离，并模仿人类行为破解滑动验证码
    """
    def __init__(self):
        super(CrackSlider, self).__init__()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chromedriver = "/usr/bin/chromedriver"
        os.environ["webdriver.chrome.driver"] = chromedriver
        self.driver = webdriver.Chrome(options=chrome_options,executable_path=chromedriver)
        self.url = 'https://stuhealth.jnu.edu.cn/#/login'  # 测试网站
        self.wait = WebDriverWait(self.driver, 20)
        self.driver.get(self.url)
        time.sleep(2)
    def open(self):
        self.driver.get(self.url)
    def get_pic(self):
        time.sleep(2)
        target = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_bg-img')))
        template = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_jigsaw')))
        target_link = target.get_attribute('src')
        template_link = template.get_attribute('src')
        target_img = Image.open(BytesIO(requests.get(target_link).content))
        template_img = Image.open(BytesIO(requests.get(template_link).content))
        target_img.save('target.jpg')
        template_img.save('template.png')
        size_orign = target.size
        local_img = Image.open('target.jpg')
        size_loc = local_img.size
        self.zoom = 320 / int(size_loc[0])
    def get_tracks(self, distance):
        print(distance)
        distance += 20
        v = 0
        t = 0.2
        forward_tracks = []
        current = 0
        mid = distance * 3/5
        while current < distance:
            if current < mid:
                a = 2
            else:
                a = -3
            s = v * t + 0.5 * a * (t**2)
            v = v + a * t
            current += s
            forward_tracks.append(round(s))
        back_tracks = [-3,-3,-2,-2,-2,-2,-2,-1,-1,-1]
        return {'forward_tracks':forward_tracks,'back_tracks':back_tracks}
    def match(self, target, template):
        img_rgb = cv2.imread(target)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(template,0)
        run = 1
        w, h = template.shape[::-1]
        print(w, h)
        res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED) 
        # 使用二分法查找阈值的精确值 
        L = 0
        R = 1
        while run < 20:
            run += 1
            threshold = (R + L) / 2
            print(threshold)
            if threshold < 0:
                print('Error')
                return None
            loc = np.where( res >= threshold)
            print(len(loc[1]))
            if len(loc[1]) > 1:
                L += (R - L) / 2
            elif len(loc[1]) == 1:
                print('目标区域起点x坐标为：%d' % loc[1][0])
                break
            elif len(loc[1]) < 1:
                R -= (R - L) / 2
        return loc[1][0]
    def crack_slider(self):
        self.open()
        target = 'target.jpg'
        template = 'template.png'
        self.get_pic()
        distance = self.match(target, template)
        tracks = self.get_tracks((distance + 7 )*self.zoom) # 对位移的缩放计算
        print(tracks)
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'yidun_slider')))
        ActionChains(self.driver).click_and_hold(slider).perform()
        for track in tracks['forward_tracks']:
            ActionChains(self.driver).move_by_offset(xoffset=track, yoffset=0).perform()
        time.sleep(0.5)
        for back_tracks in tracks['back_tracks']:
            ActionChains(self.driver).move_by_offset(xoffset=back_tracks, yoffset=0).perform()
        ActionChains(self.driver).move_by_offset(xoffset=-3, yoffset=0).perform()
        ActionChains(self.driver).move_by_offset(xoffset=3, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.driver).release().perform()
        if (self.driver.find_element_by_xpath('//*[@class="yidun_tips__text yidun-fallback__tip"]').get_attribute("innerHTML") == '向右滑动滑块填充拼图'):
            print('滑动验证不通过，正在重试')
            self.crack_slider()
        else:
            print('滑动验证通过')

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

    sl = CrackSlider()
    sl.crack_slider()
    sl.driver.find_element_by_xpath("//input[@name='appId']").send_keys(usr)
    sl.driver.find_element_by_xpath("//input[@name='password']").send_keys(pwd)
    sl.driver.find_element_by_xpath("//button[@type='submit']").click()
    time.sleep(3)

    try:
        sl.driver.find_element_by_xpath('//*[@id="10000"]').click()
        sl.driver.find_element_by_xpath('//*[@id="tj"]').click()
        time.sleep(3)
        try:
            temp = sl.driver.find_element_by_xpath('//*[@style="text-align: center;margin-bottom: 100px"]').get_attribute("innerHTML")
            result = re.split("<[^\u4e00-\u9fa5]+>",temp)
            print(result)
            tg_push(text=result[1])
        except:
            try:
                temp = sl.driver.find_element_by_xpath('//*[@style="text-align: center;margin-bottom: 100px;margin-top: 17px"]').get_attribute("innerHTML")
                result = re.split("<[^\u4e00-\u9fa5]+>",temp)
                print(result)
                tg_push(text=result[1])
            except:
                tg_push(text="签到失败，未知错误")
        sl.driver.close()
    except:
        try:
            temp = sl.driver.find_element_by_xpath('//*[@style="text-align: center;margin-bottom: 100px"]').get_attribute("innerHTML")
            result = re.split("<[^\u4e00-\u9fa5]+>",temp)
            print(result)
            tg_push(text=result[1])
        except:
            try:
                temp = sl.driver.find_element_by_xpath('//*[@style="text-align: center;margin-bottom: 100px;margin-top: 17px"]').get_attribute("innerHTML")
                result = re.split("<[^\u4e00-\u9fa5]+>",temp)
                print(result)
                tg_push(text=result[1])
            except:
                tg_push(text="签到失败，未知错误")
        sl.driver.close()