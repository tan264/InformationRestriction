"""
    This program uses Selenium, BeautifulSoup and Trafilatura to scrape data from URLs.
    So please make sure you have installed them before running it.
"""

import trafilatura
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import json
import random
import re
import time

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=options)
site = "https://baomoi.com"


class Article:
    def __init__(self, originalLink, content, datetime):
        self.originalLink = originalLink
        self.content = content
        self.datetime = datetime
    
    def __str__(self):
        return f"Original Link: {self.originalLink}\nContent: {self.content}\nDatetime: {self.datetime}"

def createArticle(link):
    htmlContent = trafilatura.fetch_url(link)
    content = trafilatura.extract(htmlContent)
    return Article(link, content, str(datetime.now()))

def getOriginalLink(link):
    driver.get(link)
    originalLink = driver.find_element(By.LINK_TEXT, "Gốc")
    originalLink.click()
    time.sleep(1)
    return driver.current_url

if __name__ == "__main__":
    driver.get(site)

    htmlContent = driver.page_source # get html content of the page
    soup = BeautifulSoup(htmlContent, "html.parser") # give the content to BeautifulSoup to analyze the html structure

    elements = soup.find_all("li", class_="parent-category") # find all elements with tag <li> and class "parent-category"
    # print(len(elements)) # 15 main sections
    list_links = list(map(lambda x: site + x.find("a")["href"], elements)) # get the link of each section

    n = random.randint(0, len(list_links)) # random a section
    print("Section:", list_links[n])
    driver.get(list_links[n])
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # scroll to the end of the page to load more articles
    time.sleep(1)
    htmlContent = driver.page_source

    soup = BeautifulSoup(htmlContent, "html.parser")
    elements = soup.find_all(class_=("w-[625px]")) # find all elements with class "w-[625px]"
    elements = elements[0].find_all(class_=("bm-card-header")) # find all elements with class "bm-card-header"
    list_links = list(map(lambda x: getOriginalLink(site + x.find("a").get('href')), elements)) # get the original link of each article
    # print(list_links)

    articles = []
    for link in list_links:
        articles.append(createArticle(link).__dict__)
    # print(json.dumps(articles, ensure_ascii=False))
    with open("DangHuuTan.json", "w", encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    # link1 = "https://www.sggp.org.vn/vu-ngo-doc-nghi-do-an-com-ga-tai-nha-trang-so-ca-ngo-doc-tiep-tuc-tang-post731058.html"
    # link2 = "https://www.sggp.org.vn/chu-tich-ubnd-tphcm-phan-van-mai-mong-bao-chi-cung-tphcm-giai-bai-toan-phat-trien-trong-hanh-trinh-di-len-post730901.html"

    # a = createArticle(link1)
    # b = createArticle(link2)
    # articles = []
    # articles.append(a.__dict__)
    # articles.append(b.__dict__)
    # print(json.dumps(articles, ensure_ascii=False))
    driver.quit()