from cloudreve_anisub.cloudreve_v3 import CloudreveV3
from cloudreve_anisub.email import EmailHandler
from cloudreve_anisub.deploy_stragegies import *
from cloudreve_anisub.utils.proxy_decorator import IS_AUTHOR_ENV

from cloudreve_anisub.utils.singleton import GetInstance
from cloudreve_anisub.utils.logger import LoggerManager
from cloudreve_anisub.rss_sources.acgrip import ACGripRSSParser
from cloudreve_anisub.rss_sources.mikan import MikanRSSParser


import hashlib
import os

log_manager = LoggerManager(f"log/{__name__}.log")
logger = log_manager.logger

source_dict = {
    ACGripRSSParser._name : ACGripRSSParser,
    MikanRSSParser._name : MikanRSSParser
}

def parse_last_download(lines):
    last_download = {}
    for line in lines:
        md5, timestamp = line.strip().split(' ')
        last_download[md5] = float(timestamp)
    return last_download


if __name__ == "__main__":
    ## 0. get config
    env = os.environ.get('CLOUDREVE_ANISUB_ENV')
    if not env and IS_AUTHOR_ENV:
        env = "LOCAL"

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
    cloudreve = CloudreveV3(strategy.email, strategy.password, strategy.url)
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
    titles_newly_download = []
    latest_downloads = {}
    for sub in subscriptions:
        parts = sub.strip().split('|')
        assert(len(parts) >= 5)
        source_name = parts[0]
        save_folder = parts[1]
        direct_rss_url = parts[2]   #TODO
        max_day_interval = int(parts[3])   # older pub will not be downloaded
        keywords = parts[4:]
        assert(source_name in source_dict.keys())

        full_description = ''.join(parts)
        md5 = hashlib.md5(full_description.encode('utf-8')).hexdigest()
        last_timestamp = last_downloads.get(md5, -1)
        latest_downloads[md5] = last_timestamp  #TODO if has direct url, do not calc md5

        # parser = GetInstance(source_name)
        parser = source_dict[source_name](strategy.rss[source_name])
        if parser and parser.is_available:
            links, max_timestamp, titles, folder_to_root_dir = parser.get_download_data(keywords, last_timestamp, max_day_interval)
            if not folder_to_root_dir:
                folder_to_root_dir = os.path.join(cloudreve_download_dir, save_folder).replace('\\','/')
            if len(links) > 0:  # only call downloading when having something new
                if cloudreve.create_directory(folder_to_root_dir): # also ok when folder exists
                    is_download_success = cloudreve.add_offline_download_task(links, folder_to_root_dir)
                    if is_download_success:
                        num_newly_downloads += len(links)
                        latest_downloads[md5] = max_timestamp
                        titles_newly_download.extend(titles)
                        logger.info(f"Successfully download {len(links)} links into {save_folder}.")
                    else:   # failed when downloading
                        all_tasks_success = False
                        logger.error(f"Failed when downloading {keywords} in RSS source {source_name}.")
                else:       # failed when create folder
                    all_tasks_success = False
                    logger.error(f"Failed when create_directory {save_folder} in cloudreve.")
            else:   # nothing new
                logger.warning("No new link found")

        else:   # failed when getting parser
            all_tasks_success = False
            logger.error(f"RSS source {source_name} is not available.")


    ###  update download data
    with open(last_download_filename, 'w') as file:
        for md5, timestamp in latest_downloads.items():
            if timestamp:
                file.write(f'{md5} {timestamp}\n')

    ## 4. check result and prepare mail data
    logger.info("=" * 50)
    logger.info("summary: ")
    repo_prefix = "AniSub: "
    if all_tasks_success:
        if num_newly_downloads > 0:
            subject = f"{repo_prefix}Successfully download animes."
            content = "Successfully download the following anime(s):\n{}".format('\n'.join([str(title) for title in titles_newly_download]))
            logger.info("All animes start to download successfully.")

        else:   # nothing new
            subject = f"{repo_prefix}There's no new anime updated."
            content = "There's no new anime!"
            logger.info("There's no new anime")

    else:   # download error
        subject = f"{repo_prefix}Failed to download all animes."
        content = "Failed..."
        logger.error("Failed to download all animes.")
    logger.info("=" * 50)


    ## 5. send email
    if strategy.enable_email_notify:
        email_handler = EmailHandler(strategy.sender, strategy.smtp_host, strategy.smtp_port, strategy.mail_license, strategy.receivers)
        email_handler.perform_sending(subject, content, files=LoggerManager.get_all_log_filenames())



