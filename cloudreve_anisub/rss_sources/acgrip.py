'''
Date: 2023-10-05 10:52:28
LastEditors: Kumo
LastEditTime: 2023-10-05 18:25:14
Description: 
'''

from .base_rss import BaseRSSParser
from ..utils.singleton import SingletonMeta, InstanceRegistry
from ..utils.logger import LoggerManager

import feedparser
from xml.etree import ElementTree as ET

from datetime import datetime, timezone, timedelta
import time
import requests

log_manager = LoggerManager(f"log/{__name__}.log")
logger = log_manager.logger

@log_manager.apply_log_method_to_all_methods
class ACGripRSSParser(BaseRSSParser, metaclass=SingletonMeta):
    _name = "acgrip"
    def __init__(self, rss_config):
        super().__init__()
        InstanceRegistry.register_instance(self)
        
        self._url = rss_config.url
        self._is_available = True
        self._feed = None

        self.test_source()


    @property
    def is_available(self):
        return self._is_available


    def test_source(self):
        num_pages_to_check = 1  # TODO
        all_items = []
        logger.info("requesting and merging rss data...")
        for i in range(num_pages_to_check):
            url = f"{self._url}/page/{i+1}.xml"
            response = self._http.get(url,proxies=self._proxy_dict)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                for item in root.findall(".//item"):
                    all_items.append(ET.tostring(item, encoding="unicode"))
            else:
                self._is_available = False            
                return
                
        # merge RSS XML
        merged_rss = f"""
        <rss version="2.0">
        <channel>
            {''.join(all_items)}
        </channel>
        </rss>
        """
        self._feed = feedparser.parse(merged_rss)        

        # response = self._http.get(self._url,proxies=self._proxy_dict)
        # if response.status_code == 200:
        #     self._feed = feedparser.parse(response.text)
        #     print(response.text)
        #     logger.info("Feed Title: " + self._feed.feed.title)
        #     self._is_available = True


    def get_latest_entries(self, keywords):
        num_pages_to_check = 5  # TODO
        all_items = []
        logger.info("requesting and merging rss data...")
        for i in range(num_pages_to_check):
            # https://acg.rip/.xml?term=ANi+%E9%AD%94%E6%B3%95%E4%BD%BF%E7%9A%84%E6%96%B0%E5%A8%98+%E7%AC%AC%E4%BA%8C%E5%AD%A3
            url = f"{self._url}/page/{i+1}.xml?term={'+'.join(keywords)}"
            response = self._http.get(url,proxies=self._proxy_dict)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                for item in root.findall(".//item"):
                    all_items.append(ET.tostring(item, encoding="unicode"))
            else:       
                return None
                
        # merge RSS XML
        merged_rss = f"""
        <rss version="2.0">
        <channel>
            {''.join(all_items)}
        </channel>
        </rss>
        """    
        return feedparser.parse(merged_rss)     

    # deprecate
    def get_download_data_old(self, keywords, last_timestamp):
        entry_links, entry_timestamps = [], []
        if not last_timestamp:
           last_timestamp = -1
        for entry in self._feed.entries:
            # match Keywords
            if not all(keyword in entry.title for keyword in keywords):
                # logger.debug(f"q keywords: {','.join(keywords)}")
                # logger.debug(f"this content: {entry.title}")
                continue
            # time_string = "Wed, 04 Oct 2023 08:31:55 -0700"
            dt = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
            this_timestamp = dt.timestamp()

            if this_timestamp <= last_timestamp:
                logger.warn("Nothing new")
                break
            
            logger.info("标题:"+entry.title)

            entry_links.append(entry.enclosures[0].href)
            entry_timestamps.append(this_timestamp)

        return entry_links, max(entry_timestamps) if entry_timestamps else 0


    def get_download_data(self, keywords, last_timestamp):
        # https://acg.rip/page/2?term=%E9%AD%94%E6%B3%95%E4%BD%BF%E7%9A%84%E6%96%B0%E5%A8%98

        entry_links, entry_timestamps = [], []
        if not last_timestamp:
           last_timestamp = -1

        for entry in self.get_latest_entries(keywords):
            # time_string = "Wed, 04 Oct 2023 08:31:55 -0700"
            dt = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
            this_timestamp = dt.timestamp()

            if this_timestamp <= last_timestamp:
                logger.warn("Nothing new")
                break
            
            logger.info("标题:"+entry.title)

            entry_links.append(entry.enclosures[0].href)
            entry_timestamps.append(this_timestamp)

        return entry_links, max(entry_timestamps) if entry_timestamps else 0
