# coding: utf-8

import json
import tornado.ioloop
import tornado.web
from tornado.gen import coroutine
from tornado.web import RequestHandler
from gonepass import GMessageLib

onepass_id = "7591d0f44d4c265c8441e99c748d936b"
onepass_key = "52ad901f58cb2466a587d8a702f20b23"

product = "embed"


class CheckGatewayHandler(RequestHandler):
    @coroutine
    def post(self):
        gm = GMessageLib(onepass_id, onepass_key)
        process_id = self.get_argument("process_id", "")
        accesscode = self.get_argument("accesscode", "")
        phone = self.get_argument("phone", "")
        user_id = "test"
        result = gm.check_gateway(process_id, accesscode, phone, user_id=user_id, testbutton=False)
        result = 0 if result else 1
        output = {"result":result,"content":"demo"}
        self.write(json.dumps(output))
        return


class CheckMessageHandler(RequestHandler):
    @coroutine
    def post(self):
        gm = GMessageLib(onepass_id, onepass_key)
        process_id = self.get_argument("process_id", "")
        message_id = self.get_argument("message_id", "")
        message_number = self.get_argument("message_number", "")
        phone = self.get_argument("phone", "")
        user_id = "test"
        result = gm.check_message(process_id, message_id,message_number, phone, user_id=user_id)
        result = 0 if result else 1
        output = {"result": result,"content": "demo"}
        self.write(json.dumps(output))
        return


if __name__ == "__main__":
    app = tornado.web.Application([
                                      (r"/gmessage/check_gateway", CheckGatewayHandler),
                                      (r"/gmessage/check_message", CheckMessageHandler),
                                  ], debug=True)

    app.listen(8122)
    tornado.ioloop.IOLoop.instance().start()
