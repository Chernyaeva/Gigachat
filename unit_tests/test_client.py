
import unittest
import time
from datetime import datetime
import json
import sys
import os

sys.path.append(os.path.join(os.getcwd(), '..'))
from server import make_response

class TestServer(unittest.TestCase):

    good_message = {
        "action": "presence",
        "time": 123456789.0,
        "type": "status",
        "user": {
            "account_name": "GigaChad",
            "status": "I'm still alive!"
        }
    }

    bad_message = {
        "action": "presence!",
        "time": 123456789.0,
        "type": "status",
        "user": {
            "account_name": "GigaChad",
            "status": "I'm still alive!"
        }
    }

    good_response = json.dumps({
        'response' : 202,
        'time' : time.mktime(datetime.now().timetuple())
    }).encode('utf-8')

    bad_response = {
        'response' : 500,
        'time' : time.mktime(datetime.now().timetuple()),
        'alert' : "server could not find good response"
    }

    def test_is_dict(self):
        self.assertEqual(type(json.loads(make_response(self.good_message))), dict)

    def test_good_response(self):
        self.assertEqual(make_response(self.good_message), self.good_response)

    def test_bad_response(self):
        self.assertDictEqual(json.loads(make_response(self.bad_message).decode('utf-8')), self.bad_response)

if __name__ == "__main__":
    unittest.main()