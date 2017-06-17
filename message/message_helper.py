# Author Vipul Jain

from config import LOGIN_API, MESSAGE_API
import logging
import requests

logger = logging.getLogger(__name__)


def get_token(user, password):
    try:
        data = {"username": user, "password": password}
        r = requests.post(LOGIN_API, data=data)
        return r.accessToken
    except Exception as e:
        logger.info("message server is down!!! try again after some time.")
        return 500


def send_message(access_token, phone_number, message, priority):
    try:
        data = {"phone": phone_number,  "message" : message, "priority": priority}
        url = MESSAGE_API.format(access_token=access_token)
        r = requests.post(url, data=data)

        if r.status_code==200:
            logger.info("sms delivered successfully")
            return 200
        if r.status_code==400:
            logger.info("invalid arguments. check phone no or message length")
            return 400
        if r.status_code==401:
            logger.info("invalid access token")
            return 401
        if r.status_code==500:
            logger.info("gateway problem. try again!!")
            return 500
    except Exception as e:
        logger.info("message server is down!!! try again after some time.")
        return 500

