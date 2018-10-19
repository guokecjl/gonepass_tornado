# coding: utf-8

import json
import time
import base64

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from hashlib import md5
from urllib.parse import urlencode
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado.gen import coroutine, Return

VERSION = "1.0.1"

RSA_KEY = b"""-----BEGIN RSA PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDB45NNFhRGWzMFPn9I7k7IexS5
XviJR3E9Je7L/350x5d9AtwdlFH3ndXRwQwprLaptNb7fQoCebZxnhdyVl8Jr2J3
FZGSIa75GJnK4IwNaG10iyCjYDviMYymvCtZcGWSqSGdC/Bcn2UCOiHSMwgHJSrg
Bm1Zzu+l8nSOqAurgQIDAQAB
-----END RSA PUBLIC KEY-----\n"""


class GMessageLib(object):

    API_URL = "http://onepass.geetest.com"
    GATEWAY_HANDLER = "/check_gateway.php"
    MESSAGE_HANDLER = "/check_message.php"
    JSON_FORMAT = False

    def __init__(self, custom_id, private_key):
        self.private_key = private_key
        self.custom_id = custom_id
        self.sdk_version = VERSION

    @coroutine
    def _check_method(self, method, **kwargs):
        """
        method for gateway check
        """
        if method == "gateway":
            process_id = kwargs["process_id"]
            access_code = kwargs["accesscode"]
            phone = kwargs["phone"]
            user_id = kwargs.get("user_id", "")
            _callback = kwargs.get("_callback", "")

            if not (process_id and access_code and phone):
                raise Return(0)

            send_url = "{api_url}{handler}".format(
                api_url=self.API_URL, handler=self.GATEWAY_HANDLER)
            sign_data = "&&".join([self.custom_id,
                                   self._md5_encode(self.private_key),
                                   str(time.time()*1000)])
            sign = self.rsa_encrypt(sign_data)
            query = {
                "process_id": process_id,
                "sdk": ''.join(["python_", self.sdk_version]),
                "user_id": user_id,
                "timestamp": time.time(),
                "accesscode": access_code,
                "callback": _callback,
                "custom": self.custom_id,
                "phone": phone,
                "sign": sign,
            }
        elif method == "message":
            process_id = kwargs["process_id"]
            message_id = kwargs["message_id"]
            message_number = kwargs["message_number"]
            phone = kwargs["phone"]
            user_id = kwargs.get("user_id", "")
            _callback = kwargs.get("_callback", "")

            if not (phone and process_id and message_id and message_number):
                raise Return(0)

            send_url = "{api_url}{handler}".format(
                api_url=self.API_URL, handler=self.MESSAGE_HANDLER)
            query = {
                "process_id": process_id,
                "sdk": ''.join(["python_", self.sdk_version]),
                "user_id": user_id,
                "timestamp": time.time(),
                "message_id": message_id,
                "message_number": message_number,
                "callback": _callback,
                "custom": self.custom_id,
            }
        else:
            send_url, query, process_id = "", "", ""  # avoid warning
        response_data = yield self._post_values(send_url, query)
        response_data = json.loads(response_data)
        if str(response_data["result"]) == "0":
            if self._check_result(process_id, response_data.get("content")):
                raise Return(1)
            else:
                raise Return(0)
        else:
            raise Return(0)

    @coroutine
    def check_gateway(self, process_id, accesscode, phone, user_id=None,
                      _callback=None):
        """
        method for gateway check
        """
        result = yield self._check_method("gateway", process_id=process_id,
                                          accesscode=accesscode, phone=phone,
                                          user_id=user_id, _callback=_callback)
        raise Return(result)

    @coroutine
    def check_message(self, process_id, message_id, message_number, phone,
                      user_id=None, _callback=None):
        """
        method for message check
        """
        result = yield self._check_method("message", process_id=process_id,
                                          message_id=message_id,
                                          message_number=message_number,
                                          phone=phone, user_id=user_id,
                                          _callback=_callback)
        raise Return(result)

    @coroutine
    def _post_values(self, url, data):
        client = AsyncHTTPClient()
        request = HTTPRequest(url, method='POST', body=urlencode(data))
        response = client.fetch(request, raise_error=False)
        raise Return(response.text())

    def _check_result(self, origin, validate):
        encode_str = self._md5_encode(self.private_key + "gtmessage" + origin)
        if validate == encode_str:
            return True
        else:
            return False

    @staticmethod
    def _md5_encode(values):
        if isinstance(values, str):
            values = values.encode()
        m = md5(values)
        return m.hexdigest()

    @staticmethod
    def rsa_encrypt(text):
        rsa_key = RSA.importKey(RSA_KEY)
        cipher = PKCS1_v1_5.new(rsa_key)
        result = base64.encodebytes(cipher.encrypt(text.encode())).decode()
        return result
