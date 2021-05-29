import tkinter as tk
from connector import *
from window import Window
import requests as req
import pandas as pd
import sys

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
# доробити паралельні запити threat для швидкодії

BASE_URL = r'https://www.olx.pl/nieruchomosci/mieszkania/wynajem/krakow/'
TABLE_HEADINGS = {"regularPrice":"value", "title":None, "url":None}
TABLE = {"regularPrice": "value",
         "title": None,
         "url": None,
         "params": None,
         #"description": None,
         #"map": None,
         "lastRefreshTime": None,
         "status": None,
         #"photos": None,
         "location": None,
         "id": None,
}

URL_PATTERN = r'.*\.html'
KEYWORD = 'oferta'
PARAMS = {
            # 'search%5Bcity_id%5D': 8959,
            # 'search%5Bregion_id%5D': 0,
            'search[district_id]': lambda:localization,
            # 'search%5Bdist%5D': 0,
            'search[filter_float_price:from]': lambda:minprice,
            'search[filter_float_price:to]': lambda:maxprice,
            'search[private_business]': 'private',
            # 'search%5Bcategory_id%5D': 1307,
        }
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "cache-control": "no-cache",
    "accept-encoding": "gzip, deflate, br",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}
OLX_SELECTORS = {
    'offer_selectors': '//table[@data-id]',
    'total_pages': '//input[@value="OK"]/@class',
    'offer_id': '//table[@data-id]/@data-id',
    'offer_url': '//a[@class]/@href',
    'offer_price': '//p[@class="price"]/strong/text()',
    'heading': '//img[@class="fleft"]/@alt',
    'otodom_offer_json': '//script[@id="__NEXT_DATA__"]/text()',
    'olx_offer_json': '//*[@id="root"]/div[1]/div[3]/div[2]/div[1]/div[2]/div[8]/div',
    #'olx_offer_data': """substring-before(substring-after(//*[@id='olx-init-config']/text(), 'STATE__='), ';\n')""",
    'olx_offer_data': '''substring-before(substring-after(//*[@id='olx-init-config']/text(), 'STATE__='), ',"categories":')''',
    'otodom_offer_data': '//*[@id="__NEXT_DATA__"]/text()'
}


class App:

    def __init__(self, root_instance: tk.Tk, session: req.Session):
        self.s = session
        self.w = Window(root_instance)
        self._set_binding(self.w)
        self.scraper = WebScraper(BASE_URL, HEADERS)
        print('size cache: ', sys.getsizeof(self.scraper.cache), 'Bytes')

    def _set_binding(self, window_instance: Window) -> None:
        w = window_instance
        w.b_run.config(command=self._click_run)
        w.table.bind('<<TreeviewSelect>>', self._click_table)
        w.panel.bind("<MouseWheel>", self._click_img)

    def _set_url_params(self, params: Dict[str,str]) -> None:
        minprice = self.w.min_price.get(0.0, tk.END).strip()
        maxprice = self.w.max_price.get(0.0, tk.END).strip()
        localization = self.w.text_place.get(0.0, tk.END).strip()
        if int(minprice) > int(maxprice):  # доробити
            minprice, maxprice = maxprice, minprice
        params['search[filter_float_price:from]'] = minprice
        params['search[filter_float_price:to]'] = maxprice
        params['search[district_id]'] = localization

    def _click_run(self) -> None:
        self.w.clear_table(self.w.table)
        self._set_url_params(PARAMS)
        urls = self.scraper.get_urls(s, keyword=KEYWORD, params=PARAMS)

        valid_urls = self.scraper.validate_url(urls, URL_PATTERN)
        print('valid urls: ', len(valid_urls))
        keywords = self.w.text_keywords.get(0.0, tk.END).strip().split(', ')
        print('keywords:', keywords)
        for i, valid_url in enumerate(valid_urls):
            if 'otodom' in valid_url:
                selector = OLX_SELECTORS['otodom_offer_data']
                ending = ''
                print(i, 'load otodom')
            else:
                selector = OLX_SELECTORS['olx_offer_data']
                ending = '}'
            data, source = self.scraper.get_pages_json_data(valid_url, self.s, selector, ending=ending)
            #print(self.scraper.cache[url])
            if keywords:
                offer_data = self.scraper.cache[valid_url]
                if not self.scraper.check_data_for_keywords(offer_data, keywords, ["url", "description"]):
                    continue
            table_data = self.get_data_for_table(TABLE_HEADINGS, data)
            #print(table_data)
            tags = "green" if source == 'web' else "default"
            self.w.fill_table(self.w.table, [table_data], tags=tags)
        print('size cache: ', sys.getsizeof(self.scraper.cache), 'Bytes')


    def get_data_for_table(self, list_headings: Dict, data: Dict[str,str]) -> List:
        """Gets heading values from 'data' for table. Return list of values."""
        headings = []
        for heading, nested in list_headings.items():
            headings.append(self.scraper.get_data_for_key(data, heading, nested=nested))
        return headings


    def _click_table(self, _) -> None:
        focus = self.w.table.focus()
        values = self.w.table.item(focus, 'values')
        selurl = values[2]
        description = self.scraper.get_data_for_key(self.scraper.cache[selurl], "description")
        self.photos_urls = self.scraper.get_data_for_key(self.scraper.cache[selurl], "photos")
        self.current_img = 0
        self.w.text.delete(0.0, tk.END)
        self.w.text.insert(tk.END, description)
        self.set_image(self.current_img)

    def set_image(self, img_count: int) -> None:
        """Delegates a setting the image in Entry-widget"""
        img_url = self.photos_urls[img_count]
        raw_img = self.scraper.get_image(img_url, self.s)
        self.w.set_image_to_entry(raw_img)



    def add_to_cache(self, key, data):
        # print(key, 'added to cache')
        self.cache[key] = data




    def get_offer_data_for_key(self, url, key):
        #offer_id = self.offers[self.offers['url'] == url]['offer_id'].item()
        data_in_cache = self.scraper.check_in_cache(url)
        if data_in_cache:
            return get_data_for_key(data_in_cache, key)
        else:
            html = get_html(url, self.s)
            if 'olx.pl' in url:
                raw_offer_data = get_selector_data(html, OLX_SELECTORS['olx_offer_data'])
            elif 'otodom' in url:
                raw_offer_data = self.get_otodom_offers_data(url, key)
            else:
                print('url not valid')
            self.add_to_cache(offer_id, raw_offer_data)
            # print('get new data',type(raw_offer_data), raw_offer_data[:23])
            return get_data_from_json(raw_offer_data, key)

    def get_otodom_offers_data(self, url, key):
        return '{"description": "proba", "offer_id": "43562774"}'

    def _click_img(self, event: tk.Event) -> None:
        c = self.current_img
        if c == len(self.photos_urls) - 1:
            c = 0
        else:
            c += 1
        self.current_img = c
        self.set_image(self.current_img)

    def get_offer_selectors(self, url, number_pages):
        all_selectors = []
        for page in range(number_pages + 1):
            if page <= 1:
                page = None
            html = self.get_main_html(url, page)
            offer_selectors = get_selectors(html, OLX_SELECTORS['offer_selectors'])
            all_selectors.extend(offer_selectors)
            self.log.insert(tk.END, f'page: {page}\n')
            self.log.see(tk.END)
            root.update()
        return all_selectors

    def get_offer_data(self, offer_selector):
        self.log.insert(tk.END, 'initial data start\n')
        offers = set()
        for sel in offer_selectors:
            offer_id = get_selector_data(sel.get(), OLX_SELECTORS['offer_id'])  # for otodom other function
            url = get_selector_data(sel.get(), OLX_SELECTORS['offer_url'])
            price = get_selector_data(sel.get(), OLX_SELECTORS['offer_price'])
            heading = get_selector_data(sel.get(), OLX_SELECTORS['heading'])
            offers.add((price, heading, url, offer_id))

        offers_df = pd.DataFrame(offers, columns=(['price', 'heading', 'url', 'offer_id']))
        offers_df.drop_duplicates()
        offers_df.sort_values('price', inplace=True, kind='mergesort')
        self.log.insert(tk.END, 'initial data end\n')
        root.update()
        return offers_df

    def filter_offers(self, df, keywords):
        self.log.insert(tk.END, 'start filter\n')
        indexes = []
        urls = df['url']
        print('urls to filter:', len(urls))
        for i, url in enumerate(urls):
            if i / 50 in [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]:
                self.log.insert(tk.END, f'url pass: {i}\n')
                root.update()
            if 'otodom' in url:  # видалити і переробити
                continue
            # print('url to filter:', url)
            offer_descr = self.get_offer_data_for_key(url, "description")
            # print('descr:', offer_descr[:25])
            for key in keywords:
                if key in offer_descr:
                    indexes.append(df['url'][df['url'] == url].index[0])
                    break
            # if key not in offer_descr:
        #print(indexes)  # df.drop(index=ind, inplace=True)
        return df.iloc()[indexes]


with req.Session() as s:
    root = tk.Tk()

    app = App(root, s)
    root.mainloop()
app.scraper.write_to_cachefile()
app.scraper.write_imgs_paths_cache()

if __name__ == '__main__':
    pass
