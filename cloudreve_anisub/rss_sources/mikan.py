'''
Date: 2023-10-05 10:52:28
LastEditors: Kumo
LastEditTime: 2023-10-05 18:24:42
Description: 
'''


from .base_rss import BaseRSSParser
from ..utils.singleton import SingletonMeta, InstanceRegistry
from ..utils.logger import LoggerManager

import feedparser
from datetime import datetime, timezone, timedelta
import time
import requests

log_manager = LoggerManager(f"log/{__name__}.log")
logger = log_manager.logger

@log_manager.apply_log_method_to_all_methods
class MikanRSSParser(BaseRSSParser, metaclass=SingletonMeta):
    _name = "mikan"
    def __init__(self, rss_config):
        super().__init__()
        InstanceRegistry.register_instance(self)
        
        self._url = rss_config.url
        self._is_available = False
        self._feed = None

        self.get_latest_entries()


    @property
    def is_available(self):
        return self._is_available


    def get_latest_entries(self):   # TODO 重试
        response = self._http.get(self._url,proxies=self._proxy_dict)
        if response.status_code == 200:
            self._feed = feedparser.parse(response.text)
            logger.info("Feed Title: " + self._feed.feed.title)
            self._is_available = True


    def get_download_data(self, keywords, last_timestamp):
        entry_links, entry_timestamps = [], []
        if not last_timestamp:
           last_timestamp = -1
        for entry in self._feed.entries:
            # match Keywords
            if not all(keyword in entry.title for keyword in keywords):
                continue
            # time_string = "Wed, 04 Oct 2023 08:31:55 -0700"
            dt = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
            this_timestamp = dt.timestamp()

            if this_timestamp <= last_timestamp:
                logger.warn("Nothing new")
                break

            logger.info("标题:"+entry.title)

            entry_links.append(entry.link)
            entry_timestamps.append(this_timestamp)
        
        return zip(entry_links, entry_timestamps)
