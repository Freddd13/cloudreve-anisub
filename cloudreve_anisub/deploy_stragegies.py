'''
Date: 2023-10-05 12:48:37
LastEditors: Kumo
LastEditTime: 2023-10-05 19:12:08
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
        self.send_logs = os.environ.get('Email_send_logs') 

        ## outlook oauth app params
        self.use_oauth2_outlook = bool(os.environ.get('use_oauth2_outlook'))
        self.outlook_client_id = os.environ.get('outlook_client_id')
        self.outlook_client_secret = os.environ.get('outlook_client_secret')
        self.outlook_redirect_uri = os.environ.get('outlook_redirect_uri')

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

        # email
        ## basic
        self.enable_email_notify = bool(yaml_data.get('Email', {}).get('enable_email_notify', False))
        self.sender = yaml_data.get('Email', {}).get('sender', None)
        self.receivers = yaml_data.get('Email', {}).get('receivers', None)
        self.smtp_host = yaml_data.get('Email', {}).get('smtp_host', None)
        self.smtp_port = yaml_data.get('Email', {}).get('smtp_port', None)
        self.mail_license = yaml_data.get('Email', {}).get('mail_license', None)
        self.send_logs = yaml_data.get('Email', {}).get('send_logs', False)

        ## outlook oauth app params
        self.use_oauth2_outlook = bool(yaml_data.get('Email', {}).get('use_oauth2_outlook', False))
        self.outlook_client_id = yaml_data.get('Email', {}).get('outlook_client_id', None)
        self.outlook_client_secret = yaml_data.get('Email', {}).get('outlook_client_secret', None)
        self.outlook_redirect_uri = yaml_data.get('Email', {}).get('outlook_redirect_uri', None)


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

        # email
        ## basic
        self.enable_email_notify = bool(yaml_data.get('Email', {}).get('enable_email_notify', False))
        self.sender = yaml_data.get('Email', {}).get('sender', None)
        self.receivers = yaml_data.get('Email', {}).get('receivers', None)
        self.smtp_host = yaml_data.get('Email', {}).get('smtp_host', None)
        self.smtp_port = yaml_data.get('Email', {}).get('smtp_port', None)
        self.mail_license = yaml_data.get('Email', {}).get('mail_license', None)
        self.send_logs = yaml_data.get('Email', {}).get('send_logs', False)

        ## outlook oauth app params
        self.use_oauth2_outlook = bool(yaml_data.get('Email', {}).get('use_oauth2_outlook', False))
        self.outlook_client_id = yaml_data.get('Email', {}).get('outlook_client_id', None)
        self.outlook_client_secret = yaml_data.get('Email', {}).get('outlook_client_secret', None)
        self.outlook_redirect_uri = yaml_data.get('Email', {}).get('outlook_redirect_uri', None)

       