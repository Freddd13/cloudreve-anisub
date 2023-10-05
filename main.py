from cloudreve_anisub.cloudreve import Cloudreve
from cloudreve_anisub.email import EmailHandler
from cloudreve_anisub.deploy_stragegies import *

from cloudreve_anisub.utils.singleton import GetInstance
from cloudreve_anisub.utils.logger import LoggerManager
from cloudreve_anisub.rss_sources.acgrip import ACGripRSSParser

import hashlib
import os

log_manager = LoggerManager(f"log/{__name__}.log")
logger = log_manager.logger


def parse_last_download(lines):
    last_download = {}
    for line in lines:
        md5, timestamp = line.strip().split(' ')
        last_download[md5] = float(timestamp)
    return last_download


if __name__ == "__main__":
    ## 0. get config
    env = os.environ.get('CLOUDREVE_ANISUB_ENV')
    assert env

    if env == "LOCAL":
        strategy = LocalStrategy()
    elif env == "DOCKER":
        strategy = DockerStrategy()
    elif env == "GITHUB_ACTION":
        strategy = GithubActionStrategy()
    else:
        logger.error(f"env error, not support env: {env}")
        os._exit(-1)

    ## 1. Init
    ### instances
    cloudreve = Cloudreve(strategy.email, strategy.password, strategy.url)
    email_handler = EmailHandler(strategy.email, strategy.smtp_host, strategy.smtp_port, strategy.mail_license, strategy.receivers)
    acgrip = ACGripRSSParser(strategy.rss['acgrip'])

    ### messy params
    sub_filename = "./subscriptions"
    last_download_filename = "./_last_download_signal"
    cloudreve_download_dir = strategy.download_dir


    ## 2. load subscriptions and last downloading times
    assert(os.path.exists(sub_filename))
    with open(sub_filename, 'r', encoding='utf-8') as file:
        subscriptions =  file.readlines()
    if (os.path.exists(last_download_filename)):
        with open(last_download_filename, 'r') as file:
            last_download_lines =  file.readlines()
        last_downloads = parse_last_download(last_download_lines) if last_download_lines else {}
    else:
        last_download_lines = {}


    ## 3. for each sub, try to find new links in rss data and call cloudreve offline download
    all_tasks_success = True
    num_newly_downloads = 0
    latest_downloads = {}
    for sub in subscriptions:
        parts = sub.strip().split('|')
        assert(len(parts) >= 3)
        source_name = parts[0]
        save_folder = parts[1]
        keywords = parts[2:]

        full_description = ''.join(parts)
        md5 = hashlib.md5(full_description.encode('utf-8')).hexdigest()
        last_timestamp = last_downloads.get(md5)
        latest_timestamp = last_timestamp
        parser = GetInstance(source_name)
        if parser and parser.is_available:
            folder_to_root_dir = os.path.join(cloudreve_download_dir, save_folder).replace('\\','/')
            if cloudreve.create_directory(folder_to_root_dir): # also ok when folder exists
                links, max_timestamp = parser.get_download_data(keywords, last_timestamp)
                if len(links) > 0:  # only call downloading when having something new
                    is_download_success = cloudreve.add_offline_download_task(links, folder_to_root_dir)
                    if is_download_success:
                        latest_timestamp = max_timestamp
                        num_newly_downloads += len(links)
                        logger.info(f"Successfully download {len(links)} links into {save_folder}.")
                    else:
                        all_tasks_success = False
                        logger.error(f"Failed when downloading {keywords} in RSS source {source_name}.")
                else:
                    logger.warning("No new link found")
            else:
                logger.error(f"Failed when create_directory {save_folder} in cloudreve.")

        else:
            all_tasks_success = False
            logger.error(f"RSS source {source_name} is not available.")

        latest_downloads[md5] = latest_timestamp

    ###  update download data
    with open(last_download_filename, 'w') as file:
        for md5, timestamp in latest_downloads.items():
            if latest_timestamp:
                file.write(f'{md5} {timestamp}\n')

    ## 4. check result and prepare mail data
    if all_tasks_success:
        if num_newly_downloads > 0:
            subject = "Successfully downloading animes."
            content = "Success!"
            logger.info("All animes start to download successfully.")

        else:   # nothing new
            subject = "There's no new anime updated."
            content = "There's no new anime!"
            logger.info("There's no new anime")

    else:   # download error
        subject = "Failed to download all animes."
        content = "Failed..."
        logger.error("Failed to download all animes.")


    ## 5. send email
    if strategy.enable_email_notify:
        email_handler = EmailHandler(strategy.sender, strategy.smtp_host, strategy.smtp_port, strategy.mail_license, strategy.receivers)
        email_handler.perform_sending(subject, content, files=logger.get_all_log_filenames())



