import os
import cv2
import time
import random
import requests
import numpy as np
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Slider():
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.url = 'https://stuhealth.jnu.edu.cn/#/login'  # 测试网站
        self.wait = WebDriverWait(self.driver, 20)
        self.driver.get(self.url)
        time.sleep(2)

    def get_img(self):
        target_link = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_bg-img'))).get_attribute('src')
        template_link = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_jigsaw'))).get_attribute('src')
        target_img = Image.open(BytesIO(requests.get(target_link).content))
        template_img = Image.open(BytesIO(requests.get(template_link).content))
        target_img.save('target.jpg')
        template_img.save('template.png')
        size_loc = target_img.size
        zoom = 320 / int(size_loc[0])  # 耦合像素
        return zoom

    def change_size(self, file):
        image = cv2.imread(file, 1)  # 读取图片 image_name应该是变量
        img = cv2.medianBlur(image, 5)  # 中值滤波，去除黑色边际中可能含有的噪声干扰
        b = cv2.threshold(img, 15, 255, cv2.THRESH_BINARY)  # 调整裁剪效果
        binary_image = b[1]  # 二值图--具有三通道
        binary_image = cv2.cvtColor(binary_image, cv2.COLOR_BGR2GRAY)
        x, y = binary_image.shape
        edges_x = []
        edges_y = []
        for i in range(x):
            for j in range(y):
                if binary_image[i][j] == 255:
                    edges_x.append(i)
                    edges_y.append(j)

        left = min(edges_x)  # 左边界
        right = max(edges_x)  # 右边界
        width = right - left  # 宽度
        bottom = min(edges_y)  # 底部
        top = max(edges_y)  # 顶部
        height = top - bottom  # 高度
        pre1_picture = image[left:left + width, bottom:bottom + height]  # 图片截取
        return pre1_picture  # 返回图片数据

    def match(self):
        img_gray = cv2.imread('target.jpg', 0)
        img_rgb = self.change_size('template.png')
        template = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        # cv2.imshow('template', template)
        # cv2.waitKey(0)
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        run = 1

        # 使用二分法查找阈值的精确值
        L = 0
        R = 1
        while run < 20:
            run += 1
            threshold = (R + L) / 2
            if threshold < 0:
                print('Error')
                return None
            loc = np.where(res >= threshold)
            if len(loc[1]) > 1:
                L += (R - L) / 2
            elif len(loc[1]) == 1:
                break
            elif len(loc[1]) < 1:
                R -= (R - L) / 2
        return loc[1][0]

    def move_to_gap(self, tracks):
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'yidun_slider')))
        ActionChains(self.driver).click_and_hold(slider).perform()
        while tracks:
            x = tracks.pop(0)
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
            time.sleep(0.05)
        time.sleep(0.05)
        ActionChains(self.driver).release().perform()

    def get_tracks(self, distance, seconds, ease_func):
        distance += 20
        tracks = [0]
        offsets = [0]
        for t in np.arange(0.0, seconds, 0.1):
            ease = ease_func
            offset = round(ease(t / seconds) * distance)
            tracks.append(offset - offsets[-1])
            offsets.append(offset)
        tracks.extend([-3, -2, -3, -2, -2, -2, -2, -1, -0, -1, -1, -1])
        return tracks

    def ease_out_quart(self, x):
        return 1 - pow(1 - x, 4)


if __name__ == '__main__':

    sl = Slider()
    while True:
        zoom = sl.get_img()
        distance = sl.match()
        track = sl.get_tracks((distance + 7) * zoom, random.randint(2, 4), sl.ease_out_quart)
        sl.move_to_gap(track)
        time.sleep(5)
        try:
            failure = sl.wait.until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, 'yidun_tips__text yidun-fallback__tip'), '向右拖动滑块填充拼图'))
            print(failure)
        except:
            print('验证成功')
            break
        if failure:
            print('验证失败')
            pass
        else:
            print('验证成功')
            break


    usr = getenv('USERNAME')
    pwd = getenv('PASSWORD')
    sl.driver.find_element_by_xpath("//input[@name='appId']").send_keys(usr)
    sl.driver.find_element_by_xpath("//input[@name='password']").send_keys(pwd)
    sl.driver.find_element_by_xpath("//button[@type='submit']").click()
    time.sleep(3)
    try:
        sl.driver.find_element_by_xpath('//*[@id="10000"]').click()
        sl.driver.find_element_by_xpath('//*[@id="tj"]').click()
        time.sleep(3)
        sl.driver.close()
    except:
        sl.driver.close()