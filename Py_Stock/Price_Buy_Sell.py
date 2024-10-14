# 三大法人買賣超金額
#引入使用套件
import os
import requests
import json
# import time
import datetime
import telebot
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

def send_message_to_telegram(message):
    API_TOKEN = os.getenv('TG_MYBOT_TOKEN')
    chat_id = [os.getenv('TG_MYCHATID'), os.getenv('TG_TWOCHATID')]
    
    bot = telebot.TeleBot(API_TOKEN)
    for id in chat_id:
        bot.send_message(chat_id, message)

def chat(chanel_list, authorization_list, msg_stock):
    for authorization in authorization_list:
        header = {
            "Authorization": f"Bot authorization",
            "Content-Type": "application/json",
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.39',
            # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
        }
        for chanel_id in chanel_list:
            msg = {
                # "content": get_context(),
                "content": msg_stock,
                # "nonce": "82329451214{}33232234".format(random.randrange(0, 1000)),
                "tts": False,
            }
            # url = "https://discord.com/api/v10/channels/{}/messages".format(chanel_id)
            url = f"https://discord.com/api/v10/channels/{chanel_id}/messages"
            try:
                # res = requests.post(url=url, headers=header, data=json.dumps(msg))
                # print(res.content)
                res = requests.post(url=url, headers=header, json=msg)  # 使用 json 參數
                
                print(f"Response: {res.status_code}, {res.content}")
                
                if res.status_code == 403:
                    print(f"Permission issue: Unable to send message to channel {chanel_id}. Please check bot permissions.")
                elif res.status_code != 200 and res.status_code != 204:
                    print(f"Failed to send message to channel {chanel_id}, response: {res.content}")
                else:
                    print(f"Message sent to channel {chanel_id} successfully.")
            except Exception as e:
                print(f"Error occurred: {e}")
            pass
        # time.sleep(random.randrange(1, 3))

# ====================================================================================================

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
  token = [os.getenv('LINE_USER_ID'),os.getenv('LINE_GROUP_TEST'),os.getenv('LINE_GROUP_CCFU')]

  Discord_list = [ os.getenv('DISCORD_CHANEL_LIST_STOCK') ]
  Discord_token = [ os.getenv('DISCORD_TOKEN') ]
    
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

    send_message_to_telegram(msg)
    # for tokenD in Discord_token:
    #     for listD in Discord_list:
    #         chat( listD, tokenD , msg)
    
    # LineNotify(os.getenv('LINE_USER_ID'), msg)
    # LineNotify(os.getenv('LINE_GROUP_TEST'), msg)
    # LineNotify(os.getenv('LINE_GROUP_CCFU'), msg)
