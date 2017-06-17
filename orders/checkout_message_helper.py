# Author Vipul Jain

import logging
from config import USERNAME, PASSWORD
from message.message_helper import get_token, send_message

logger = logging.getLogger(__name__)
TOKEN = ""
MAX_RETRY = 10


def checkout_message(checkout_status, phone_number, priority):
    """
    utility for sending message on checkout.
    :param checkout_status: 0 for success, 1 for failure
    :param phone_number: phone number of the user
    :param message: text of the message to be sent 
    :param priority: priority of the message
    :return: 200 - ok 400 - user details error 500 - server error
    """
    global MAX_RETRY

    if checkout_status == 0:
        message = "checkout was successful. items will be delivered soon."
    elif checkout_status == 1:
        message = "checkout failed!! retry."

    retry = MAX_RETRY
    while retry > 0:
        try:
            code = send_message(access_token=TOKEN,
                                phone_number=phone_number,
                                message=message,
                                priority=priority)
            if code == 200 or code == 400:
                return code
            if code==401:
                TOKEN = get_token(user=USERNAME, password=PASSWORD)
        except Exception as e:
            logger.error("Message server is down. Retrying!!!")
        retry -= 1
    return 200 if retry != 0 else 500
