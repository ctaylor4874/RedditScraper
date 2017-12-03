"""
Scraper for reddit.
"""
import os
import time
import argparse
import logging
import contextlib
import json
import requests


def get_data():
    return requests.get("http://www.reddit.com/r/{}/{}.json?limit=100".format(args.subreddit, args.type_of_post)).json()


def read_data():
    with contextlib.closing(
            open("{}/data/response.txt".format(os.path.dirname(os.path.realpath(__file__))), "r")) as stream:
        read_in = stream.read()
        return json.loads(read_in)


def check_title(title):
    title = title.lower()
    if args.keyword.lower() in title:
        for word in args.additional_keywords:
            if word.lower() in title:
                return True
    return False


def parse_data(data):
    current_time = time.time()
    message_body = ""
    for child in data.get('data').get('children'):
        if int(child.get('data').get('created_utc')) > (current_time - 1800):
            has_item = check_title(child.get('data').get('title'))
            if has_item:
                message_body += "\n\n===\n\nTitle: {} > \n\nReddit Link: www.reddit.com{} \n\nLink: {}".format(
                    child.get('data').get('title'), child.get('data').get('permalink'), child.get('data').get('url'))
    return message_body


def send(user, to, pwd, body):
    import smtplib

    from_user = user
    to_user = to
    subject = "Reddit Posts from {}, {}".format(args.subreddit, args.type_of_post)
    email_text = body

    message = """From: {}\nTo: {}\nSubject: {}\n\n{}
        """.format(from_user, to_user, subject, email_text)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(from_user, to_user, message)
        server.close()
        logging.info('successfully sent the mail')
    except Exception as exc:
        logging.error(exc)


def send_email(body):
    user = os.getenv("EMAIL_ADDRESS")
    second_user = os.getenv("SECOND_EMAIL")
    pwd = os.getenv("EMAIL_PASSWORD")
    send(user, user, pwd, body)
    if second_user:
        send(user, second_user, pwd, body)


def run():
    data = get_data()
    if not data.get('error'):
        parsed = parse_data(data)
        if len(parsed):
            send_email(parsed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Subreddit and type args.')
    parser.add_argument('subreddit', help='Enter the subreddit to watch.')
    parser.add_argument('type_of_post', help='Enter the type (new, top, hot, etc...).')
    parser.add_argument('keyword', help='Enter the keywords (animals, people, etc...)')
    parser.add_argument('additional_keywords', help='Enter the additional keywords example=(animals people)', nargs='+')
    args = parser.parse_args()
    logging.basicConfig(level=20, format='%(asctime)s:{}'.format(logging.BASIC_FORMAT))
    try:
        run()
    except Exception as e:
        logging.exception(e)
        raise
