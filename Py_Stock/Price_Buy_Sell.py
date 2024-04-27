# 三大法人買賣超金額
#引入使用套件
import os
import requests
import json
import datetime
from linebot.models import TextSendMessage
from linebot import (
    LineBotApi, WebhookHandler
)

# 不讓伺服器當作機器人
header = {
    # 用 text/html 方法，以 UTF-8 格式解析
    'content-type' : 'text/html; charset=UTF-8',
    # 用什麼方式執行(Mozilla、AppleWebKit、Chrome)
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.39'}

def LineNotify(token, msg):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = {
        "message": msg
    }
    # image = {'imageFile': file}
    r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=params)#, files = image)

cDay = 0

# 爬取三大法人買賣超金額
url = 'https://www.twse.com.tw/rwd/zh/fund/BFI82U?type=day&dayDate=' + (datetime.datetime.today()+datetime.timedelta(days=cDay)).strftime('%Y%m%d')
res = requests.get(url, headers = header)

# while(res.json()['total']==0):
while(res.json()['stat']=='很抱歉，沒有符合條件的資料!'):
# while(res.json()['stat']!='OK'):
  cDay -= 1
  url = 'https://www.twse.com.tw/rwd/zh/fund/BFI82U?type=day&dayDate=' + (datetime.datetime.today()+datetime.timedelta(days=cDay)).strftime('%Y%m%d')
  res = requests.get(url, headers = header)

res.json()['stat']

msg = res.json()['date'] + '\n集中市場買賣超金額'

# Line Notify 練習
if __name__ == "__main__":
  # 從LINE Notify取得的權杖(token)
  # LINE_USER_ID 個人單獨的
  token = [os.getenv('LINE_USER_ID')]

  if res.json()['stat']=='OK':

    # 外資、投信、三大法人買賣超
    for i in range(0,6):
      print(res.json()['data'][i][0])
      msg = msg + '\n' +  res.json()['data'][i][0] + '\n'
      for j in range(1,4):
        print(res.json()['fields'][j],":",format(int(res.json()['data'][i][j].replace(',',''))/100000000,'.2f'),"億")
        msg = msg + res.json()['fields'][j] + "：" + str(format(int(res.json()['data'][i][j].replace(',',''))/100000000,'.2f')) + " 億" + '\n'

    for token_i in token:
      LineNotify(token_i, msg)
