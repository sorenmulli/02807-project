import os
import time
from typing import Optional, List
from selenium import webdriver
from bs4 import BeautifulSoup
from lxml import html

import requests

SEARCH_URL = "https://twitter.com/search?q={0}&src=unknown&f=user"
DRIVER_FOLDER = "."
os.environ["PATH"] += ":" + DRIVER_FOLDER

def search_user(name: str, driver: webdriver) -> List[str]:
    page = driver.get(SEARCH_URL.format(name))
    time.sleep(5) # Wait for JS to load :-P
    tree = html.fromstring(driver.page_source)
    allres = list()
    m = True
    i = 1
    while m:
        m = tree.xpath(f"/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/section/div/div/div[{i}]/div/div/div/div/div[2]")
        i += 1
        allres.extend(m)
    for res in allres:
        name_div, bio_div = list(res)
        name_div = list(list(name_div)[0])[0]
        display_div, handle_div = list(name_div)
        breakpoint()




    breakpoint()

if __name__ == "__main__":
    driver = webdriver.Firefox()
    search_user("kenneth mikkelsen", driver)

