'''
Date: 2023-10-05 10:52:28
LastEditors: Kumo
LastEditTime: 2024-04-14 20:15:01
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
class MikanRSSParser(BaseRSSParser, metaclass=SingletonMeta):
    _name = "mikan"
    def __init__(self, rss_config):
        super().__init__()
        InstanceRegistry.register_instance(self)
        
        self._url = rss_config.url
        self._is_available = True
        self._feed = None


    @property
    def is_available(self):
        return self._is_available


    def _get_latest_entries(self):
        logger.info("requesting and merging rss data...")
        response = self._http.get(self._url, proxies=self._proxy_dict)
        if response.status_code == 200:
            return feedparser.parse(response.content)  
        else:
            return None


    def get_download_data(self, keywords, last_timestamp, max_day_interval):
        entry_links, entry_timestamps, entry_titles = [], [], []
        if not last_timestamp:
           last_timestamp = -1

        for entry in self._get_latest_entries().entries:
            # time_string = "2024-04-11T02:55:01.989"
            dt = datetime.fromisoformat(entry.published)
            this_timestamp = dt.timestamp()

            # season old part check, TODO
            days_difference = (datetime.now().timestamp() - this_timestamp) / (60 * 60 * 24)
            logger.debug(f"days_difference: {days_difference}")
            if days_difference > max_day_interval:
                logger.warn("ignore old part resources.")
                break

            if this_timestamp <= last_timestamp:
                logger.warn("Nothing new")
                break
            
            logger.debug(f"this_timestamp: {this_timestamp}, last_timestamp: {last_timestamp}")
            logger.info(f"标题: {entry.title}")

            entry_links.append(entry.enclosures[0].href)
            entry_timestamps.append(this_timestamp)
            entry_titles.append(entry.title)

            # TODO:try to parse anime name by AI as the folder name, if failed-->None-->use tmp folder in `./subscription`

        return entry_links, max(entry_timestamps) if entry_timestamps else 0, entry_titles, None
