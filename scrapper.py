"""
TODO

Author: Darren Li
"""
from datetime import datetime

import WebTools as wt
from bs4 import BeautifulSoup


HN_ROOT = 'https://www.harveynorman.com.au/'

def get_page(url):
    """TODO"""
    resp = wt.get_(url)
    if not resp:
        raise ValueError('No Soup found')
    soup = BeautifulSoup(resp.content, features="html.parser")

    cur_date = datetime.now().strftime('%Y%m%d')
    print(cur_date)
    soup_path = wt.WEB_ROOT_FILE.joinpath(f'{cur_date}.html')

    # Save HTML to a file
    with open(soup_path, "w", encoding = 'utf-8') as file:
        # prettify the soup object and convert it into a string  
        file.write(str(soup.prettify()))


if __name__ == "__main__":

    url = HN_ROOT +'computers-tablets/computers/laptops?p=1'
