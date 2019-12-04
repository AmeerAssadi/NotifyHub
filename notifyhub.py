import requests
import datetime
from json import dumps
import config


def main():
    # headers = {
    #     'Accept': 'application/vnd.github.v3+json'
    # }

    notifications = requests.get('https://api.github.com/notifications?access_token=' + config.github_apiKey + '&since=' + (datetime.datetime.utcnow() - datetime.timedelta(1)).strftime('%a, %d %b %Y %H:%M:%S GMT'))

    if notifications.status_code == 200:
        if len(notifications.json()) == 0:
            print('No new notification')
            exit()
        for notification in notifications.json():
            author = ''
            url = ''
            detailsReq = requests.get(notification["subject"]["url"] + '?access_token=' + config.github_apiKey)
            if detailsReq.status_code == 200:
                try:
                    author = detailsReq.json()["user"]["login"]
                    url = detailsReq.json()["html_url"]
                except:
                    pass
            # Check if repository is private
            if len(url) == 0:
                url = 'Private Repository'
            if len(author) == 0:
                author = 'Hidden Name'

            slackPayload = {
                "icon_url": config.icon_url,
                'text': ':robot_face: Notification about new ' + notification["subject"][
                    "type"] + ' request opened by ' + '`' + author + '`'
                        + "\n" + 'Repository name: ' + '`' + notification["repository"]["full_name"] + '`'
                        + "\n" + 'Subject: ' + '`' + notification["subject"]["title"] + '`'
                        + '\n' + 'URL: ' + url
            }
            requests.post(config.posting_webhook, dumps(slackPayload), headers={'content-type': 'application/json'})

    else:
        errorPayload = {
            'text': 'Error ' + dumps(notifications.json()["message"])
        }
        requests.post(config.error_logging, dumps(errorPayload), headers={'content-type': 'application/json'})


if __name__ == '__main__':
    main()
