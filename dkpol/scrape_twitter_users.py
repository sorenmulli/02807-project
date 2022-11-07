from __future__ import annotations

import os
import time
from selenium import webdriver
from lxml import html

SEARCH_URL = "https://twitter.com/search?q={0}&src=unknown&f=user"
DRIVER_FOLDER = "."
os.environ["PATH"] += ":" + DRIVER_FOLDER

def search_user(name: str, driver: webdriver) -> tuple[str, str, str]:
    driver.get(SEARCH_URL.format(name))
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
        try:
            name_div, bio_div = list(res)
            name_div = list(list(name_div)[0])[0]
            display_div, handle_div = list(name_div)
            name = display_div[0][0][0][0][0].text
            handle = handle_div[0][0][0][0][0].text
            bio = bio_div[0].text
        except ValueError:
            # No bio (probably, at least in one case)
            name_div = res[0]
            name_div = list(list(name_div)[0])[0]
            display_div, handle_div = list(name_div)
            name = display_div[0][0][0][0][0].text
            handle = handle_div[0][0][0][0][0].text
            bio = ""
        print(name, handle)
        print(bio)
        # return name, handle, bio

if __name__ == "__main__":
    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    search_user("pia kærsgaard", driver)

