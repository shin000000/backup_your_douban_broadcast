import logging
import os 
import random
import sys
import time
import urllib.request

from openpyxl import Workbook

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 添加log
if not os.path.exists("log"):
    os.makedirs("log")

log_file_path = "log/{}.log".format(time.strftime("%Y-%m-%d"))
fh = logging.FileHandler(filename=log_file_path, encoding="UTF-8")
logging.basicConfig(
    handlers=[fh], format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("whatever")

# 在当前目录下创建用于存放图片的文件夹
path = os.path.join("pictures")
if not os.path.exists(path):
    os.makedirs(path)

# 配置chromedriver
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
options.add_argument('User-Agent=Mozilla/5.0 '
	'(Windows NT 10.0,  Win64,  x64,  rv:96.0) Gecko/20100101 Firefox/96.0 ')
options.add_argument("disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options)

# 打开豆瓣提示用户登入，如果用cookie的方式，可以把下面input那一行注释掉。。
driver.get('https://www.douban.com/') 
input("【请在打开的标签页中登入豆瓣！登录完毕后请按任意键跳转】")

# # 把你的cookie写在这里
# cookies = []
# for cookie in cookies:
#     driver.add_cookie(cookie)

# 跳转到用户豆瓣主页
driver.get("https://www.douban.com/mine")
time.sleep(3)

# 打印cookies
cookies = driver.get_cookies()
print(cookies)

# 跳转到用户豆瓣广播页地址
hp_url = driver.current_url.partition('?')[0]
status_url = hp_url + "statuses?p="
print(status_url)

print("你想从广播第一页下载到第几页？")
start = input("起始页：")
end = input("结束页：")

wb = Workbook()
ws = wb.active
ws.append(['people', 'content', 'created_date', 'homepage', 'broadcast_url'])
page = 1

try:
    for i in range(int(start), int(end)):
        driver.get(status_url + str(i))
        time.sleep(3)
        broadcasts = driver.find_elements(By.CSS_SELECTOR, ".status-item>.mod")
        for broadcast in broadcasts:
            people = broadcast.find_elements(By.CSS_SELECTOR, 'div.hd>div.text>a')
            people = people[0].text if people else ''
            homepage = broadcast.find_elements(By.CSS_SELECTOR, 'div.hd>div.text>a')
            homepage = homepage[0].get_attribute('href') if homepage else ''
            content = broadcast.find_elements(By.CSS_SELECTOR, 'blockquote')
            content = content[0].text if content else ''
            created_date = broadcast.find_elements(By.CSS_SELECTOR, '.created_at')
            created_date = created_date[0].get_attribute('title') if created_date else ''
            broadcast_url = broadcast.find_elements(By.CSS_SELECTOR, '.hd')
            broadcast_url = broadcast_url[0].get_attribute('data-status-url') if broadcast_url else ''
            ws.append([people, content, created_date, homepage, broadcast_url])
        print(f'sucessfully fetched information from {page}th page!')
        page += 1

except Exception as e:
    logger.info(f'exception on page {page}')
    print(e)
finally:
    wb.save('broadcast.xlsx')
