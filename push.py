import requests
from os import getenv

TGCHATID = getenv('TGCHATID')
BOTTOKEN = getenv('BOTTOKEN')

class tg_push():
    def tg_push(self, text):
        push_url = 'https://api.telegram.org/bot' + BOTTOKEN + '/sendMessage?chat_id=' + TGCHATID + '&text=' + text
        rPush = requests.get(push_url)
        if rPush.status_code == 200 :
            print('推送成功')
        elif rPush.status_code == 400 :
            print('CHATID 填写有误')
        else :
            print('推送失败，未知错误')