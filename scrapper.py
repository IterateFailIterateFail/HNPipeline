"""
TODO

Author: Darren Li
"""
import re
import math
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup

import WebTools as wt


HN_ROOT = 'https://www.harveynorman.com.au/'
PAGE_SIZE = 40


def get_page(cat_href, cat_name, folder_path=None, page=1, root_url=HN_ROOT):
    """Gets Page soruce and saves it somewhere, and returns it from function"""

    url = f'{root_url}{cat_href}?p={page}'
    resp = wt.get_(url)
    if not resp:
        raise ValueError('No Soup found')
    
    soup = BeautifulSoup(resp.content, features="html.parser")

    cur_date = datetime.now().strftime('%Y%m%d')

    if folder_path:
        soup_path = folder_path.joinpath(f'{cat_name}_{page}_{cur_date}.html')

        # Save HTML to a file
        with open(soup_path, "w", encoding='utf-8') as file:
            # prettify the soup object and convert it into a string  
            file.write(str(soup.prettify()))

    return soup


def get_item_num(cat_href, cat_name, root_url=HN_ROOT):
    """Get number of items in a category"""
    soup = get_page(cat_href, cat_name, root_url=root_url)
    prod_count_text = soup.find('div', attrs={'data-testid': 'product-count'}).text

    if not prod_count_text:
        raise ValueError('Could not get Product Count (Check website?)')
    
    prod_count_text = re.search(r'of (\d+)', prod_count_text).group()
    prod_count_text = prod_count_text.replace('of ', '')
    prod_count = int(prod_count_text)

    return prod_count
    

def get_categories(root_url=HN_ROOT):
    """Gets all categories from the root Harvey Norman url as Dataframe"""
    resp = wt.get_(root_url)
    soup = BeautifulSoup(resp.content, features="lxml")

    macro_cat_list = []
    cat_list = []
    href_list = []

    nav_div = soup.find('div', id='sf-page-nav')
    lev_1_divs = nav_div.find_all('li', 'level1')
    for lev_1 in lev_1_divs:

        lev_1_text = lev_1.find('span').text
        lev_2_divs = lev_1.find_all('li', 'level2')

        for lev_2 in lev_2_divs:

            lev_2_text = lev_2.find('span').text
            lev_2_href = lev_2.find('a')['href']
            macro_cat_list.append(lev_1_text)
            cat_list.append(lev_2_text)
            href_list.append(lev_2_href)

    cat_df = pd.DataFrame({
        'Macro Category': macro_cat_list,
        'Category': cat_list,
        'Href': href_list
    })
    return cat_df


if __name__ == "__main__":

    folder_path = wt.WEB_ROOT_FILE.joinpath('HN_Cache')
    cat_df = get_categories()

    # We're limiting it to just Laptops at the moment
    cat_df = cat_df[cat_df['Category'] == 'Laptops']

    for cat_row in cat_df.itertuples():
        cat = cat_row.Category
        href = cat_row.Href
        prod_count = get_item_num(href, cat)
        print(f'{cat}: {prod_count}')
        expected_pages = math.ceil(prod_count/40)
        for i in range(1, expected_pages + 1):
            get_page(href, cat, folder_path=folder_path, page=i)
