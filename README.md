# Automatic Anime Subscription for Cloudreve
Periodically subscribe RSS from Anime Torrent sites and call cloudreve offline downloading to get you latest animes.

## Usage

### Use Github Action
1. Fork the repo
2. Use your own information to set the needed secrets in your repo(Repo Settings -- Secrets and variables -- Actions -- Secrets). You may need an email with SMTP host, port, account and app password. Check out [User config](#User-config) for the full config we need.
![](docs/add_secrets.png)
3. Write your subscriptions into `subscriptions`. One sub occupies one line. In single line, the first three element represents rss source (acgrip, mikann, dmhy or ...) `folder name` of the anime to be saved in your cloudreve and `direct rss url(optional)`. Note that this dir is relative to the `download_dir` in the user config. The remaining things are your keywords to match in the RSS title. For any keyword, you can simply use the content in url such as `能干的猫今天也忧郁+桜都字幕组` for acgrip, which `+, -, *` is supported. The keyword number is not limited. Lastly, every element should be separated by `|` with no space (But space is allowed inside keyword).
4. Enable Workflow r/w permissions
Settings -- Actions -- General
![](docs/enable_rw.png)
5. Allow the actions to run on your forked repos:
a. Actions-->click "I understand my workflows, go ahead and enable them"
![](docs/allow_action.png)
b. Enable the auto download workflow: auto download-->Enable workflow
![](docs/enable_schedule.png)

Then the action will be triggered when pushing to repo or reaching a certain time everyday. The latter can be set in the auto_download.yml. 
To test whether your config is correct, you can run a test immediately following the steps below:
![](docs/try_workflow.png)
If you enable the email sending and set your mail data properly, you should receive an email with run data. You can also check the history running results from the actions tab.

### Use Docker
1. Download the config file:
```
wget https://github.com/Freddd13/cloudreve-anisub/blob/main/localconfig.yaml?raw=true -O .localconfig.yaml
```
2. Replace your own data in the yaml above. Check out [User config](#(User-config)) for the full config we need. (The varaible name is for env, but it should be easily understood for yaml.)
3. Download image and run:
```
# 1. pull the image
docker pull fredyu13/cloudreve-anisub
# 2. (optional) set your trigger time in crontab, see docker/crontab.
# 3. run a container from the image
docker run -d --name cloudreve-anisub -v $(pwd)/.localconfig.yaml:/app/.localconfig.yaml fredyu13/cloudreve-anisub
```

### User config
| Variable                  | Description                                         | Example Value          |
|---------------------------|-----------------------------------------------------|------------------------|
| `Cloudreve_email`               | Email associated with Cloudreve website.                | `user@example.com`     |
| `Cloudreve_password`            | Password for the Cloudreve.                        | `passwordiiyokoiyo`          |
| `Cloudreve_url`     | Cloudreve_url.                   | yourcloudreve.com      |
| `download_dir`     | Cloudreve download base dir. (The first `/` means that the path is relative to cloudreve root thus it's necessary.)                   |   /anime_download/cloudreve_anisub    |
| `acgrip_url(example，there're other sources)`                 | URL of the RSS feed.                               | `https://acg.rip`|
| `acgrip_enable(example)` | Whether to enable this rss source  | `1`  (currently not used)                    |
| `enable_email_notify`      | Whether to notify downloading result via email  (1 enable, 0 disable)  | `1` |
| `Email_sender`            | Email address used to send emails.                 | `sender@example.com`   |
| `Email_receivers`         | Email addresses designated to receive emails.      | `receiver@example.com` |
| `Email_smtp_host`         | SMTP server address used to send emails.           | `smtp.example.com`     |
| `Email_smtp_port`         | SMTP server port used to send emails.              | `11451`                  |
| `Email_mail_license`      | SMTP password or authorization used for sending emails.  | `1145141919810`  |
| `Email_send_logs`       | Whether to send email with logs (1 enable, 0 disable)       | `1`                     |
| `use_oauth2_outlook`       | Whether to use outlook oauth2 email (1 enable, 0 disable)       | `1`                     |
| `outlook_client_id`       | outlook azure app client ID      | `114514`                     |
| `outlook_client_secret`       | outlook azure app client secret value      | `114514`                     |
| `outlook_redirect_uri`       | outlook azure app redirect URI       | `http://localhost:9001`                     |

## Develop
### Run locally
1. Clone this repo
2. Create a .localconfig.yaml from localconfig.yaml and fill in your data. Check out [User config](#(User-config)) for the full config we need. (The varaible name is for env, but it should be easily understood for yaml.)
3. Enable Workflow r/w permissions
3. `pip install -r requirements.txt`
4. Set env `CLOUDREVE_ANISUB_ENV` to `LOCAL`
4. `python main.py`

### Build Docker
1. Clone this repo
2. Create a .localconfig.yaml from localconfig.yaml and fill in your data. 
3. `docker build -t cloudreve-anisub -f docker/Dockerfile .`
4. `docker run -d --name cloudreve-anisub cloudreve-anisub:latest`
The schedule task can be adjusted by modifing the ./docker/crontab.

## Note
### About RSS
- current only part of websites are supported, but you can implement yours by completing method according to the base_rss.py. Remember the source name in the `subscription` should be consistent with the `_name` in your class.

## TODO
- [x] Email notification
- [ ] Bot notification
- [x] Docker support
- [ ] More websites support
    - [x] acgrip
    - [ ] dmhy
    - [ ] bgmoe
    - [ ] mikan(under development)
    - [ ] nyaa


# Disclaimer:
The scripts provided in this repo is intended for personal use and convenience. It is the user's responsibility to use this tool in accordance with the terms of service and policies of anime.

The author of this repo shall not be held responsible for any misuse or improper use of this tool, including but not limited to any violations of related terms of service, copyright infringement, or any other legal or ethical concerns.

Users are advised to exercise discretion and adhere to all applicable laws and regulations when using this tool. The author of this tool disclaim all liability for any consequences resulting from the use of this tool.

By using this tool, you agree to accept all responsibility and legal consequences that may arise from its use.
Please use this tool responsibly and in compliance with terms and conditions in your country.
