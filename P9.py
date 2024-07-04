import requests
from bs4 import BeautifulSoup
import json
import time
import os

# 從環境變量中獲取LINE Notify的Token和TinyURL API URL
line_token = 'f2uwke7YMV0rXbIDQragycDNf8bw0vjFLe8rWjHEFQQ'
tinyurl_api_url = "http://tinyurl.com/api-create.php?url="

# 發送LINE通知的函數
def send_line_notify(message):
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": "Bearer " + line_token
    }
    payload = {
        "message": message
    }
    response = requests.post(url, headers=headers, data=payload)
    return response.status_code

# 縮短URL的函數
def shorten_url(url):
    response = requests.get(tinyurl_api_url + url)
    return response.text

# 主循環
while True:
    try:
        # 指定要追蹤的網站URL
        url = "https://www.p9.com.tw/Forum/ForumSection.aspx?Id=1&Sort=Post_Time"

        # 發送HTTP GET請求以獲取網頁內容
        response = requests.get(url)

        # 使用BeautifulSoup解析HTML內容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到所有文章標題（假設文章標題在 <a class="a18"> 標籤內）
        articles = soup.find_all('a', class_='a18')

        # 提取所有文章標題文本及其URL，並縮短URL
        base_url = "https://www.p9.com.tw"
        article_data = []
        for article in articles:
            full_url = base_url + article['href']
            short_url = shorten_url(full_url)
            article_data.append({"title": article.text.strip() + f" ({short_url})", "url": short_url})

        # 讀取之前保存的文章標題列表
        try:
            with open('articles.json', 'r') as file:
                old_article_titles = json.load(file)
        except FileNotFoundError:
            old_article_titles = []

        # 比較新抓取的文章標題列表與之前的列表
        new_articles = [article for article in article_data if article['title'] not in old_article_titles]

        # 如果有新文章，發送LINE通知
        if new_articles:
            message = "p9！\n" + "\n".join([article['title'] for article in new_articles])
            send_line_notify(message)
            print("p9！")
            for article in new_articles:
                print(article['title'])
        else:
            print("沒有新文章。")

        # 更新保存的文章標題列表
        with open('articles.json', 'w') as file:
            json.dump([article['title'] for article in article_data], file)

    except Exception as e:
        print(f"發生錯誤：{e}")

    # 等待5秒後再次運行
    time.sleep(5)
