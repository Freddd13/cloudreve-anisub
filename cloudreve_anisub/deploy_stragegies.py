'''
Date: 2023-10-05 12:48:37
LastEditors: Kumo
LastEditTime: 2023-10-05 18:24:22
Description: 
'''
from .utils.logger import LoggerManager

import os

log_manager = LoggerManager(f"log/{__name__}.log")
logger = log_manager.logger

class RSSSourceConfig:
    def __init__(self, enable, url) -> None:
        self.enable = enable
        self.url = url


@log_manager.apply_log_method_to_all_methods
class BaseStrategy:
    def __init__(self):
        self.last_success_video_time = None
        self.rss = {}

    def run(self):
        return NotImplementedError

    def load_config(self):
        return NotImplementedError

    def get_last_success_time(self):
        # 从.last_success_time文件中读取时间
        if os.path.exists('_last_success_time'):
            with open('_last_success_time', 'r') as f:
                self.last_success_video_time =  f.readline()
                logger.info(f"_last_success {self.last_success_video_time}")

    def update_last_success_time(self, latest_time_str):
        # 将时间写入当前目前.last_success_time文件
        with open('_last_success_time', 'w') as f:
            f.write(latest_time_str)


@log_manager.apply_log_method_to_all_methods
class GithubActionStrategy(BaseStrategy):
    def __init__(self):
        logger.info("Using Github Action Strategy")
        super().__init__()
        self.load_config()
        self.get_last_success_time()

    def load_config(self):
        self.email = os.environ.get('Cloudreve_email')
        self.password = os.environ.get('Cloudreve_password')
        self.url = os.environ.get('Cloudreve_url')
        self.download_dir = os.environ.get('Cloudreve_download_dir')

        self.rss["acgrip"] = RSSSourceConfig(os.environ.get('acgrip_enable'), os.environ.get('acgrip_url'))
        self.rss["bangumi_moe"] = RSSSourceConfig(os.environ.get('bangumi_moe_enable'), os.environ.get('bangumi_moe_url'))
        self.rss["mikan"] = RSSSourceConfig(os.environ.get('mikan_enable'), os.environ.get('mikan_url'))
        self.rss["nyaa"] = RSSSourceConfig(os.environ.get('nyaa_enable'), os.environ.get('nyaa_url'))

        self.enable_email_notify = bool(os.environ.get('enable_email_notify'))
        self.sender = os.environ.get('Email_sender')
        self.receivers = [os.environ.get('Email_receivers')] # TODO
        self.smtp_host = os.environ.get('Email_smtp_host')
        self.smtp_port = os.environ.get('Email_smtp_port')
        self.mail_license = os.environ.get('Email_mail_license') 

        # private
        # self._github_repo_token = os.environ.get('GITHUB_REPO_TOKEN')
        # self._github_owner_repo = os.environ.get('GITHUB_OWNER_REPO')


@log_manager.apply_log_method_to_all_methods
class DockerStrategy(BaseStrategy):
    def __init__(self):
        logger.info("Using DockerStrategy")
        super().__init__()
        self.load_config()
        self.get_last_success_time()

    def load_config(self):
        import yaml
        with open('config/.localconfig.yaml', 'r') as file:
            yaml_data = yaml.load(file, Loader=yaml.FullLoader)
        self.email = yaml_data['Cloudreve']['email']
        self.password = yaml_data['Cloudreve']['password']
        self.url = yaml_data['Cloudreve']['url']
        self.download_dir = yaml_data['Cloudreve']['download_dir']

        rss_config = yaml_data['RSS']
        self.rss["acgrip"] = RSSSourceConfig(rss_config['acgrip']['enable'], rss_config['acgrip']['url'])
        self.rss["bangumi_moe"] = RSSSourceConfig(rss_config['bangumi_moe']['enable'], rss_config['bangumi_moe']['url'])
        self.rss["mikan"] = RSSSourceConfig(rss_config['mikan']['enable'], rss_config['mikan']['url'])
        self.rss["nyaa"] = RSSSourceConfig(rss_config['nyaa']['enable'], rss_config['nyaa']['url'])

        self.enable_email_notify = bool(yaml_data['Email']['enable_email_notify'])
        self.sender = yaml_data['Email']['sender']
        self.receivers = yaml_data['Email']['receivers']
        self.smtp_host = yaml_data['Email']['smtp_host']
        self.smtp_port = yaml_data['Email']['smtp_port']
        self.mail_license = yaml_data['Email']['mail_license']


@log_manager.apply_log_method_to_all_methods
class LocalStrategy(BaseStrategy):
    def __init__(self):
        logger.info('Using LocalStrategy')
        super().__init__()
        self.load_config()
        self.get_last_success_time()

    def load_config(self):
        import yaml
        with open('config/.localconfig.yaml', 'r') as file:
            yaml_data = yaml.load(file, Loader=yaml.FullLoader)
        self.email = yaml_data['Cloudreve']['email']
        self.password = yaml_data['Cloudreve']['password']
        self.url = yaml_data['Cloudreve']['url']
        self.download_dir = yaml_data['Cloudreve']['download_dir']

        rss_config = yaml_data['RSS']
        self.rss["acgrip"] = RSSSourceConfig(rss_config['acgrip']['enable'], rss_config['acgrip']['url'])
        self.rss["bangumi_moe"] = RSSSourceConfig(rss_config['bangumi_moe']['enable'], rss_config['bangumi_moe']['url'])
        self.rss["mikan"] = RSSSourceConfig(rss_config['mikan']['enable'], rss_config['mikan']['url'])
        self.rss["nyaa"] = RSSSourceConfig(rss_config['nyaa']['enable'], rss_config['nyaa']['url'])

        self.enable_email_notify = bool(yaml_data['Email']['enable_email_notify'])
        self.sender = yaml_data['Email']['sender']
        self.receivers = yaml_data['Email']['receivers']
        self.smtp_host = yaml_data['Email']['smtp_host']
        self.smtp_port = yaml_data['Email']['smtp_port']
        self.mail_license = yaml_data['Email']['mail_license']
       