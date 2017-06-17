# Author Vipul Jain

import logging
from config import USERNAME, PASSWORD
from message.sms_client import get_token, send_message

logger = logging.getLogger(__name__)
TOKEN = ""
MAX_RETRY = 10


def delivery_message(status, phone_number, priority):
    """
    
    :param status: 0 for success, 1 for failure 
    :param phone_number: user phone number
    :param priority: priority of the message
    :return: 200 - ok 400 - user details error 500 - server error
    """
    global MAX_RETRY

    message = ""
    if status == 0:
        message = "item was delivered successfully"

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