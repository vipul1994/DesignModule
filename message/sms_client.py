# Author Vipul Jain
from random import randint

from config import LOGIN_API, MESSAGE_API, USERNAME, PASSWORD, \
    MILIO_MESSAGE_API, REGISTERED_PHONE
from custom_exceptions import BadInputError, \
    InvalidMessageError, \
    InvalidPhoneNumberError, \
    SmsException
import datetime
import requests
import time
from requests import ConnectTimeout


class WatertelSmsClient(object):

    def __init__(self, login_url, message_url, username, password):
        self.login_url = login_url
        self.message_url = message_url
        self.username = username
        self.password = password
        self.access_token = None
        self.expires_at = 0
        self.priority = 1

    @staticmethod
    def _validate_phone_number(phone_number):
        if not phone_number:
            raise InvalidPhoneNumberError("Empty phone number")
        phone_number = phone_number.strip()
        if len(phone_number) > 10:
            # TODO add more such checks
            raise InvalidPhoneNumberError("Phone number too long")

    @staticmethod
    def _validate_message(message):
        if not message:
            raise InvalidMessageError("Empty message")
        if len(message) > 140:
            raise InvalidMessageError("Message too long")

    @staticmethod
    def _make_login_request(username, password):
        try:
            data = {"username": username, "password": password}
            url = LOGIN_API
            r = requests.post(url, json=data)
            return r.status_code, r.json()
        except Exception as e:
            raise Exception("could not connect to login server on watertel")

    def _make_message_request(self, access_token, phone_number, message):
        try:
            data = {"message": message, "phone": phone_number, "priority": self.priority}
            url = MESSAGE_API.format(access_token=access_token)
            r = requests.post(url, json=data)
            return r.status_code, r.json()
        except ConnectTimeout as e:
            raise SmsException("connection timeout trying to send sms")

    def _login(self):
        # TODO - Make http request for login
        # TODO - error handling per status codes
        status_code, response = self._make_login_request(self.username,
                                                         self.password)
        self.access_token = response["accessToken"]
        self.expires_at = datetime.datetime.now() + response["expiry"]

    def _get_access_token(self):
        if datetime.datetime.now() > self.expires_at:
            self._login()
        return self.access_token

    # code for sending out sms to users
    def send_sms(self, phone_number, message):
        self._validate_phone_number(phone_number)
        self._validate_message(message)
        access_token = self._get_access_token()
        status_code, response = self._make_message_request(access_token,
                                                           phone_number,
                                                           message)
        if status_code == 400:
            # This is Watertel telling us the input is incorrect
            #  If it is possible, we should read the error message
            #  and try to convert it to a proper error
            # We will just raise the generic BadInputError
            raise BadInputError(response.error_message)
        elif status_code in (300, 301, 302, 401, 403):
            # These status codes indicate something is wrong
            # with our module's logic. Retrying won't help,
            # we will keep getting the same status code
            # 3xx is a redirect, indicate a wrong url
            # 401, 403 have got to do with the access_token being wrong
            # We don't want our clients to retry, so we raise RuntimeError
            raise RuntimeError(response.error_message)
        elif status_code > 500:
            # This is a problem with Watertel
            # This is beyond our control, and perhaps retrying would
            # We indicate this by raising SmsException
            raise SmsException(response.error_message)


class SmsClientWithRetry(object):

    def __init__(self, sms_client):
        self.delegate = sms_client

    def send_sms(self, phone_number, message):
        # TODO - add retry logic
        attempts = 1
        retries = self.num_attempts
        delay = self.backoff
        while retries > 1:
            try:
                return self.delegate.send_sms(phone_number, message)
            except SmsException as e:
                time.sleep(delay)
                attempts += 1
                retries -= 1
                delay *= self.backoff
        return self.delegate.send_sms(phone_number, message)


class MilioSmsClient(object):

    def __init__(self, url, registered_phone, access_token):
        self.url = url
        self.registered_phone = registered_phone
        self.access_token = access_token

    def send_sms(self, phone_number, message):
        pass


class SmsRouter:

    def __init__(self, split_ratio, first, second):
        self.split_ratio = split_ratio
        self. watertel = first
        self.milio = second

    def send_sms(self, phone_number, message):
        number = randint(1, 100)
        if number <= self.split_ratio:
            self.first.send_sms(phone_number, message)
        elif number <= 100:
            self.second.send_sms(phone_number, message)
        else:
            raise SmsException("Unreachable code path!")

_watertel_client = WatertelSmsClient(LOGIN_API, MESSAGE_API, USERNAME, PASSWORD)
_milio_client = MilioSmsClient(MILIO_MESSAGE_API, REGISTERED_PHONE, PASSWORD)
_router = SmsRouter(80, _watertel_client, _milio_client)
sms_client = SmsClientWithRetry(_router)