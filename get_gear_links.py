import requests
import re
import json
import get_gear
import time
import random
from bs4 import BeautifulSoup



def get_sites(site_url):
    if site_url != '':
        time.sleep(random.randint(0, 10))
        res= requests.get(site_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        })

        urls = []
        soup = BeautifulSoup(res.text, 'html.parser')

        tr_odd = soup.find_all('tr',class_="ak-bg-odd")
        for a in tr_odd:
            urls.append('https://www.dofus-touch.com' + a.span.a['href'])

        tr_even = soup.find_all('tr',class_="ak-bg-even")
        for b in tr_even:
            urls.append('https://www.dofus-touch.com' + b.span.a['href'])

        get_gear.create_gear_json(urls)

        res_next_page = soup.find('ul',class_="ak-pagination pagination ak-ajaxloader").find_all('a')
        for next_page in res_next_page:
            if next_page.text.strip() == '›':
                next = next_page['href']
                get_sites('https://www.dofus-touch.com' + next)
            elif next_page.text.strip() == '':
                break

get_sites("https://www.dofus-touch.com/en/mmorpg/encyclopedia/equipment")
