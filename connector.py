import re
import parsel
import json
from typing import *
import requests as req
import glob


CACHE_PATH = 'cache/cache.json'
IMG_CACHE_PATH = 'cache/images/'
IMG_PATHS_CACHE_PATH = 'cache/images/images_paths.json'


class WebScraper:

    def __init__(self, base_url: str, headers: Dict[str, str], log_instance=None, **kwds) -> None:
        self.log = log_instance
        self.headers = headers
        self.base_url = base_url
        self.cache = {}
        self.img_paths_cache = {}
        self.cache_count = 1

        self._read_cache(CACHE_PATH)
        self._read_img_paths_cache(IMG_PATHS_CACHE_PATH)
        self.img_names_count = len(self.img_paths_cache) + 1

    def _read_cache(self, cache_path: str) -> Dict or None:
        """Read data from cache file into the memory."""
        try:
            #for path in glob.glob(cache_path):
            with open(cache_path, encoding='Latin-1') as f:  # переробити: змінити на латін
                #print('read cache path:', path)
                self.cache.update(json.load(f))
                #self.cache_count += 1
        except FileNotFoundError:
            return {"key": "value"}

    def _read_img_paths_cache(self, img_paths_cache_path: str) -> None or Dict:
        """Read data from image cache files into memory."""
        try:
            with open(img_paths_cache_path, encoding='utf-8') as f:
                print('read imgs paths file :', img_paths_cache_path)
                self.img_paths_cache.update(json.load(f))
        except FileNotFoundError:
            return {"url": "path"}

    def check_in_cache(self, key: str) -> str or Dict[str, str] or False:
        """Checks whether 'key' is in memory."""
        if self.cache.get(key, False):
            # print('data from cache')
            return self.cache[key]
        elif self.img_paths_cache.get(key, False):
            return self.img_paths_cache[key]
        else:
            return False

##    def add_to_cache(self, key: str, data: Dict[str, str]) -> None:
##        """Add data into cache, into many files"""
##        print('added to cache')
##        #del data["categories"]
##        filename = f'cache/cache_{self.cache_count}.json'
##        with open(filename, 'w', encoding='utf-8') as f:
##            json.dump({key: data}, f, indent=4)
##        self.cache_count += 1
##        self.cache[key] = data

    def add_to_cache(self, key: str, data: Dict[str, str]) -> None:
        """Add {key: data} to the cache variable."""
        print('added to cache')
        #del data["categories"]
        #filename = f'cache/cache_{self.cache_count}.json'
        #with open(CACHE_PATH, 'w', encoding='Latin-1') as f:
            #json.dump({key: data}, f, indent=4)
        #self.cache_count += 1
        self.cache[key] = data

    def write_to_cachefile(self) -> None:
        """Write data from the cache variable to the cache file."""
        print('write to cachefile')
        #del data["categories"]
        #filename = f'cache/cache_{self.cache_count}.json'
        with open(CACHE_PATH, 'w', encoding='Latin-1') as f:
            json.dump(self.cache, f, indent=4)

    def write_imgs_paths_cache(self):
        with open(IMG_PATHS_CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.img_paths_cache, f, indent=1)

    def get_selectors(html, xpath):
        sel = parsel.Selector(text=html)
        return sel.xpath(xpath)

    def get_selector_data(self, html: str, xpath: str) -> List[str]:
        """Gets all data from 'html' for given 'xpath'."""
        sel = parsel.Selector(text=html)
        # print(sel.getall())
        return sel.xpath(xpath).getall()

    def get_urls(self, session: req.Session, **kwds) -> List[str]:
        """gets all url-links from main_url page and following pages with number from 1 to 'n'.
		If 'keyword' is not None, it filter links. Returns list with url-links."""
        keyword = kwds.get('keyword', None)
        pagenumber = kwds.get('n', 30) 
        params = kwds.get('params', None)
        xpath = '//@href'
        urls = set()
        page_url = ''
        i = 0
        for page in range(1, pagenumber + 1):
            i += 1
            page = None if page <= 1 else page
            params['page'] = page
            r = session.get(self.base_url, params=params)
            if r.url == page_url or len(page_url) - len(r.url) > 5:
                break
            else:
                page_url = r.url
            # with open(f'{i}.html', 'w', encoding='utf-8') as f:
            # f.write(r.text)
            new_urls = self.get_selector_data(r.text, xpath)
            print('base url:', r.url)
            urls.update(new_urls)
        if keyword:
            urls = [item for item in urls if keyword in item]
        print('count urls:', len(urls))
        return urls

    def validate_url(self, urls: Union[List, set], pattern: str) -> set:
        """Extracts valid part of each 'url' for 'pattern'. Return set of valid urls."""
        valid_urls = set()
        for url in urls:
            valid = re.match(pattern, url)[0]
            valid_urls.add(valid)
        return valid_urls

    def get_pages_json_data(self, url: str, session: req.Session, xpath: str, **kwds) -> Dict[str, str] and str:
        """Gets data from html page or cache for given 'url' and 'xpath'."""
        starting = kwds.get('starting', '')
        ending = kwds.get('ending', '')
        if not self.check_in_cache(url):
            print('loading offer...')

            html = self.get_html(url, session, headers=self.headers) 
            json_data = starting + self.get_selector_data(html, xpath)[0] + ending
            datadict = json.loads(json_data)
            self.add_to_cache(url, datadict)
            source = 'web'
        else:
            datadict = self.cache[url]
            source = 'cache'
        return datadict, source

    
            

    def check_data_for_keywords(self, datadict: Dict, keywords: List[str], keys: List[str] = None) -> bool:
        """Checks 'textdata' for 'keywords'. Return True or False. """
        #with open('dict.txt', 'w', encoding='utf-8') as f:
                  #f.write(str(datadict))
        input_data = datadict
        for word in keywords:
            for key in keys:
                data = self.get_data_for_key(input_data, key)
                if data and word in data: return True
        return False

    def get_html(self, url: str, session: req.Session, params: Dict = None, headers: Dict[str, str] = None) -> str:
        """Gets html text for 'url'. """
        r = session.get(url, params=params, headers=headers)
        return r.text

    def get_image(self, url: str, session: req.Session) -> bytes:
        """Gets bytes image content for 'url' from web or from image cache."""
        print('image url: ', url)
        if self.check_in_cache(url):
            path = self.img_paths_cache[url]
            with open(path, 'rb') as image:
                return image.read()
        r = session.get(url)
        if r.status_code == 200:
            path = IMG_CACHE_PATH + f'{self.img_names_count}.png'
            with open(path, 'wb') as image:
                image.write(r.content)
            self.img_names_count += 1
            self.img_paths_cache[r.url] = path
            # print('image:', type(r.content), r.content)
            return r.content

    def get_keys_from_json(self, keys: Union[List, Dict, set], json_text: str) -> List:
        """"""
        json_dict = json.loads(json_text)
        values = []
        for key, nested in keys.items():
            value = self.get_data_for_key(json_dict, key, nested)
            values.append(value)
        return values

    def get_data_for_keys(self, json_text: str, keys: List) -> List[str]:
        """"""
        jsondict = json.loads(json_text)
        data = []
        for key in keys:
            value = self.get_data_for_key(jsondict, key)
            data.append(value)
        return data

    def get_data_for_key(self, json_dict: Dict, key: str, nested: str = None):
        """Search recursively target 'key' in 'json' object and return value for it.
        Also the function search 'nested' мфдшkey which is nested in value of target 'key'. Otherwise return None."""
        if isinstance(json_dict, dict):
            if key in json_dict:
                if nested:
                    return self.get_data_for_key(json_dict[key], nested)
                return json_dict[key]
            for k in json_dict:
                val = self.get_data_for_key(json_dict[k], key, nested)
                if val is not None: return val
        elif isinstance(json, list):
            for i in json_dict:
                val = self.get_data_for_key(i, key, nested)
                if val is not None:
                    return val
        return None

##    def del_get_data_for_key(self, json_object: Dict, target_key: str, nested: str = None) -> Union[
##        List, str, Dict, None]:
##        """Search recursively 'target_key' in 'json_object' and return value for it. Otherwise return None."""
##        if target_key in json_object:
##            value = json_object[target_key]
##            if nested: value = value[nested]
##            return value
##        for d in json_object.values():
##            if isinstance(d, dict):
##                val = self.get_data_for_key(d, target_key)
##                if val is not None:
##                    if nested: val = val[nested]
##                    return val
##        return None

if __name__ == '__main__':
    
    url = 'https://www.olx.pl/nieruchomosci/mieszkania/wynajem/krakow'
    params = {
        # 'search[filter_float_price:from]': 1,
        # 'search[filter_float_price:to]': maxprice,
        'search[private_business]': 'private',
    }
    app = WebScraper(url)
    with req.Session() as s:
        list_urls = app.get_urls(url, s, params=params)
        print(len(list_urls))
