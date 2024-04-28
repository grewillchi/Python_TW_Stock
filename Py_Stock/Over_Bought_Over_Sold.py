#引入使用套件
import requests
import json
import os
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from linebot.models import TextSendMessage
from linebot import (
    LineBotApi, WebhookHandler
)

# 三大法人買賣超金額
# https://www.twse.com.tw/rwd/zh/fund/BFI82U?type=day&dayDate=20230712
# 台灣證券交易資料_三大法人買賣超
# POST方法，夾帶payload
# url = 'https://www.twse.com.tw/zh/fund/T86'
# GET方法，網址夾帶日期
#url = 'https://www.twse.com.tw/rwd/zh/fund/T86?date=20230414&selectType=ALLBUT0999&response=json'

# 不讓伺服器當作機器人
header = {
    # 用 text/html 方法，以 UTF-8 格式解析
    'content-type' : 'text/html; charset=UTF-8',
    # 用什麼方式執行(Mozilla、AppleWebKit、Chrome)
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.39',}
payload = {
    'response' : 'json',
    'date' : (datetime.datetime.today()+datetime.timedelta(days=-1)).strftime('%Y%m%d'),
    'selectType' : 'ALLBUT0999'
    }

def compare_Buy_Sell(df, Bool, text, date, normal):
  # df:引入 DataFrame、Bool:判斷排序升冪降冪(False、True)、date:日期
  # text:欲進行排序的欄位名稱、normal: 1:判斷為一般資料 or 0:特殊資料
  if normal == 1:
    ID = pd.Series(df.sort_values(by=[text], ascending=Bool).head(30)['證券代號'])
    Name = pd.Series(df.sort_values(by=[text], ascending=Bool).head(30)['證券名稱'])
    Buy_Sell = pd.Series(df.sort_values(by=[text], ascending=Bool).head(30)[text])

    if Bool==False and text=='外資買賣超':
      kind = '外資買超'
    elif Bool==True and text=='外資買賣超':
      kind = '外資賣超'
    elif Bool==False and text=='投信買賣超':
      kind = '投信買超'
    elif Bool==True and text=='投信買賣超':
      kind = '投信賣超'
    elif Bool==False and text=='三大法人買賣超':
      kind = '三大法人買超'
    elif Bool==True and text=='三大法人買賣超':
      kind = '三大法人賣超'

    msg = date + '\n\t代號'.center(4) + '\t' + kind + '\t名稱'

    for i,j,k,c in zip(ID, Name, Buy_Sell, range(len(ID))):
      msg = msg + '\n' + str(c+1).rjust(2) + '\t' + str(i).center(6) + '\t' + str(k).center(10) + '\t' + str(j).center(4)

  elif normal == 0:
    if Bool == False:
      ID = pd.Series(df.sort_values(by=[text], ascending=Bool).loc[(df['外資買賣超']>0) & (df['投信買賣超']>0)].head(30)['證券代號'])
      Name = pd.Series(df.sort_values(by=[text], ascending=Bool).loc[(df['外資買賣超']>0) & (df['投信買賣超']>0)].head(30)['證券名稱'])
      Buy_Sell_1 = pd.Series(df.sort_values(by=[text], ascending=Bool).loc[(df['外資買賣超']>0) & (df['投信買賣超']>0)].head(30)['外資買賣超'])
      Buy_Sell_2 = pd.Series(df.sort_values(by=[text], ascending=Bool).loc[(df['外資買賣超']>0) & (df['投信買賣超']>0)].head(30)['投信買賣超'])
      kind = '外資投信同買'
    elif Bool == True:
      ID = pd.Series(df.sort_values(by=[text], ascending=Bool).loc[(df['外資買賣超']<0) & (df['投信買賣超']<0)].head(30)['證券代號'])
      Name = pd.Series(df.sort_values(by=[text], ascending=Bool).loc[(df['外資買賣超']<0) & (df['投信買賣超']<0)].head(30)['證券名稱'])
      Buy_Sell_1 = pd.Series(df.sort_values(by=[text], ascending=Bool).loc[(df['外資買賣超']<0) & (df['投信買賣超']<0)].head(30)['外資買賣超'])
      Buy_Sell_2 = pd.Series(df.sort_values(by=[text], ascending=Bool).loc[(df['外資買賣超']<0) & (df['投信買賣超']<0)].head(30)['投信買賣超'])
      kind = '外資投信同賣'

    msg = date + '\n\t代號'.center(4) + '\t' + kind + '\t名稱'

    for i,j,m,n,c in zip(ID, Name, Buy_Sell_1, Buy_Sell_2, range(len(ID))):
      msg = msg + '\n' + str(c+1).rjust(2) + '\t' + str(i).center(6) + '\t' + str(m).center(10) + '\t' + str(n).center(10) + '\t' + str(j).center(4)

  return msg

# 查詢個股買賣超
def Self_Buy_Sell(df, date):
  # df:引入 DataFrame、date:日期

  filt_ID = ['2421','1609','6806','1101','5306','3037','2634','4107','2313','5469','3712','2455','2504']

  df = df.sort_values(by='證券代號', ascending=True)

  ID = pd.Series(df.loc[df['證券代號'].isin(filt_ID)]['證券代號'])
  Name = pd.Series(df.loc[df['證券代號'].isin(filt_ID)]['證券名稱'])
  Buy_Sell1 = pd.Series(df.loc[df['證券代號'].isin(filt_ID)]['外資買賣超'])
  Buy_Sell2 = pd.Series(df.loc[df['證券代號'].isin(filt_ID)]['投信買賣超'])
  Buy_Sell3 = pd.Series(df.loc[df['證券代號'].isin(filt_ID)]['三大法人買賣超'])

  msg = date + '集中市場\n\t代號'.center(4) + '\t外資\t投信\t三大法人\t名稱'

  for i,j,k,l,m in zip(ID, Name, Buy_Sell1, Buy_Sell2, Buy_Sell3):
    msg = msg + '\n' + str(i).center(4) + '\t' + str(k).center(6) + '\t' + '\t' + str(l).center(6) + '\t' + str(m).center(6) + str(j).center(4)

  return msg

# LineNotify 應用，需要 token 權杖
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

# 爬取三大法人買賣超資訊
url = 'https://www.twse.com.tw/rwd/zh/fund/T86?date=' + (datetime.datetime.today()+datetime.timedelta(days=cDay)).strftime('%Y%m%d') + '&selectType=ALLBUT0999&response=json'
res = requests.get(url, headers = header)

# res = requests.post(url, headers = header, params = payload)
# price = json.loads(res.text)

# 從當天日期開始查詢，若查無則往前查，依此類推
# print(cDay)

while(res.json()['total']==0):
# while(res.json()['stat']=='很抱歉，沒有符合條件的資料!'):
# while(res.json()['stat']!='OK'):
  print(cDay)
  cDay -= 1
  url = 'https://www.twse.com.tw/rwd/zh/fund/T86?date=' + (datetime.datetime.today()+datetime.timedelta(days=cDay)).strftime('%Y%m%d') + '&selectType=ALLBUT0999&response=json'
  res = requests.get(url, headers = header)

res.json()['stat']

# 將欄內資料存入 data
data = res.json()['data']
# 將資料儲存為 DataFrame
df = pd.DataFrame(data,columns=res.json()['fields'])#,dtype=float)

### 資料清理 ###

# drop(columns=['']) 刪除指定欄位，需使用 inplace=True 才會完整刪除於DataFrame儲存的資料
df.drop(columns=['外陸資買進股數(不含外資自營商)','外陸資賣出股數(不含外資自營商)','外資自營商買進股數','外資自營商賣出股數','外資自營商買賣超股數','投信買進股數','投信賣出股數','自營商買賣超股數','自營商買進股數(自行買賣)','自營商賣出股數(自行買賣)','自營商買賣超股數(自行買賣)','自營商買進股數(避險)','自營商賣出股數(避險)','自營商買賣超股數(避險)'],inplace=True)

# pandas.to_numeric():將字串轉為數字型態
df['外陸資買賣超股數(不含外資自營商)'] = (pd.to_numeric(df['外陸資買賣超股數(不含外資自營商)'].str.replace(',',''))/1000).astype(int)
df['投信買賣超股數'] = (pd.to_numeric(df['投信買賣超股數'].str.replace(',',''))/1000).astype(int)
df['三大法人買賣超股數'] = (pd.to_numeric(df['三大法人買賣超股數'].str.replace(',',''))/1000).astype(int)

# 更改名稱及定義
Text = ['外資買賣超','投信買賣超','三大法人買賣超']
# 選擇查詢名稱
kind = Text[1]
# Bool 布林判斷，True:升冪(賣超)，False:降冪(買超)
B = [False, True]

# pandas.rename(columns={'':''}) 更改欄位名稱
df = df.rename(columns={'外陸資買賣超股數(不含外資自營商)':Text[0],'投信買賣超股數':Text[1],'三大法人買賣超股數':Text[2]})

# Line Notify 練習
if __name__ == "__main__":
  #從LINE Notify取得的權杖(token)
  token = [os.getenv('LINE_USER_ID')]

  if res.json()['stat']=='OK':

    # 外資、投信、三大法人買賣超
    for i in B:
      for j in Text:
        msg = compare_Buy_Sell(df, i, j, res.json()['date'], 1)

        # LineNotify(token, msg)
        for token_i in token:
          LineNotify(token_i, msg)

    # 三大法人排序，篩選出外資&投信同買超、同賣超
    for i in B:
      msg = compare_Buy_Sell(df, i, Text[2], res.json()['date'], 0)

      # LineNotify(token, msg)
      for token_i in token:
        LineNotify(token_i, msg)
      
    msg = Self_Buy_Sell(df, res.json()['date'])
    LineNotify(os.getenv('LINE_USER_ID'), msg)

# 櫃買中心買賣超
cDay = 0
date_stock = str(int((datetime.datetime.today()+datetime.timedelta(days=cDay)).strftime('%Y'))-1911) + (datetime.datetime.today()+datetime.timedelta(days=cDay)).strftime('/%m/%d')
print(date_stock)
# GET方法，網址夾帶日期
url = 'https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_result.php?t=D&d=' + date_stock

res = requests.get(url, headers = header)

while(res.json()['iTotalRecords']==0):
  print(cDay)
  cDay -= 1
  date_stock = str(int((datetime.datetime.today()+datetime.timedelta(days=cDay)).strftime('%Y'))-1911) + (datetime.datetime.today()+datetime.timedelta(days=cDay)).strftime('/%m/%d')
  url = 'https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_result.php?t=D&d=' + date_stock
  res = requests.get(url, headers = header)

# 想查的股票代號
find_stock = ['3163', '3611', '6146']

msg = '\n櫃買中心買賣超\n代號　名稱　外資 投信\n'

for i in res.json()['aaData']:
  if i[0] in find_stock:
    msg = msg + i[0] + ' ' + i[1] + ' ' + str(int(i[10].replace(',',''))/1000) + ' ' + str(int(i[13].replace(',',''))/1000) + '\n'

# Line Notify 練習
if __name__ == "__main__":
  #從LINE Notify取得的權杖(token)
  token = [os.getenv('LINE_USER_ID')]

  if res.json()['iTotalRecords']!='0':
    LineNotify(os.getenv('LINE_USER_ID'), msg) # 個人單獨的 Line Notify
