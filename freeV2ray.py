# -*- coding: utf-8 -*-
"""
Created on Thu Jul  8 06:12:28 2021

@author: zhuangweibin
"""


import requests
from bs4 import BeautifulSoup
import bs4

def getHTMLText(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ""
    
     
def main():
    url = 'https://github.com/freefq/free'
    html = getHTMLText(url)
    soup = BeautifulSoup(html, "html.parser")
    article = soup.select('article[class="markdown-body entry-content container-lg"]')
    pt = article[0].find_all('p')
    print(pt[4].get_text())
    with open("v2ray.txt","w") as f:
        f.write(pt[4].get_text())
        

if __name__ == '__main__':
    main()
        
            
        
