# -*- coding: utf-8 -*-
"""
unit tests for web app
"""

from unittest import TestCase
import requests
from datetime import datetime
from hashlib import sha1
import json
import time
try:
    from __main__ import _flask
except ImportError:
    from web import _flask


class TestDroneRequests(TestCase):

    URL = "https://drone.fm.tul.cz"
    # URL =  "http://77.104.234.105:14859"
    DRONE = 1
    FLIGHT = 48
    HEIGHT = 423.03
    LATITUDE = 50.768252
    LONGITUDE = 15.084928

    def test_dronestart_succ(self):
        data = {"start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "drone": self.DRONE}
        data = json.dumps(data, ensure_ascii=False)
        hash = sha1("%s|%s" % (data, _flask.config["DRONE_PASSWORD"])).hexdigest()
        ret = requests.post(self.URL + "/dronestart", data={"data": data, "hash": hash})
        self.assertTrue(ret.content.isdigit())

    def test_dronestart_missing_params(self):
        data = {"start": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        data = json.dumps(data, ensure_ascii=False)
        hash = sha1("%s|%s" % (data, _flask.config["DRONE_PASSWORD"])).hexdigest()
        ret = requests.post(self.URL + "/dronestart", data={"data": data, "hash": hash})
        self.assertEqual(ret.status_code, 403)

        data = {"start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "drone": self.DRONE}
        ret = requests.post(self.URL + "/dronestart", data={"data": data})
        self.assertEqual(ret.status_code, 405)

    def test_dronestart_invalid_hash(self):
        data = {"start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "drone": self.DRONE}
        data = json.dumps(data, ensure_ascii=False)
        hash = sha1("%s|%s" % (data, _flask.config["DRONE_PASSWORD"])).hexdigest()[3:]
        ret = requests.post(self.URL + "/dronestart", data={"data": data, "hash": hash})
        self.assertEqual(ret.status_code, 403)

    def test_dronestart_invalid_param_vals(self):
        data = {"start": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "drone": self.DRONE}
        data = json.dumps(data, ensure_ascii=False)
        hash = sha1("%s|%s" % (data, _flask.config["DRONE_PASSWORD"])).hexdigest()
        ret = requests.post(self.URL + "/dronestart", data={"data": data, "hash": hash})
        self.assertEqual(ret.status_code, 403)

        data = {"start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "drone": "1a"}
        data = json.dumps(data, ensure_ascii=False)
        hash = sha1("%s|%s" % (data, _flask.config["DRONE_PASSWORD"])).hexdigest()
        ret = requests.post(self.URL + "/dronestart", data={"data": data, "hash": hash})
        self.assertEqual(ret.status_code, 403)

    def test_dronestart_integrity_err(self):
        data = {"start": "2017-04-07 18:35:47",
                "drone": 1}
        data = json.dumps(data, ensure_ascii=False)
        hash = sha1("%s|%s" % (data, _flask.config["DRONE_PASSWORD"])).hexdigest()
        ret = requests.post(self.URL + "/dronestart", data={"data": data, "hash": hash})
        self.assertEqual(ret.status_code, 403)

        data = {"start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "drone": 17829}
        data = json.dumps(data, ensure_ascii=False)
        hash = sha1("%s|%s" % (data, _flask.config["DRONE_PASSWORD"])).hexdigest()
        ret = requests.post(self.URL + "/dronestart", data={"data": data, "hash": hash})
        self.assertEqual(ret.status_code, 403)

    def test_dronestart_json_err(self):
        data = {"start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "drone": self.DRONE}
        data = json.dumps(data, ensure_ascii=False)
        data = data[1:]
        hash = sha1("%s|%s" % (data, _flask.config["DRONE_PASSWORD"])).hexdigest()
        ret = requests.post(self.URL + "/dronestart", data={"data": data, "hash": hash})
        self.assertEqual(ret.status_code, 403)

    # ------------------------------------------------------------------------------------------------------------------

    def test_dronelocation_succ(self):
        data = {"flight": self.FLIGHT,
                "stamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "height": self.HEIGHT,
                "latitude": self.LATITUDE,
                "longitude": self.LONGITUDE}
        data = json.dumps(data, ensure_ascii=False)
        hash = sha1("%s|%s" % (data, _flask.config["DRONE_PASSWORD"])).hexdigest()
        ret = requests.post(self.URL + "/dronelocation", data={"data": data, "hash": hash})
        self.assertTrue(ret.content.isdigit())

    def test_dronelocation_succ_photo(self):
        time.sleep(1.1)
        import base64
        with open("test_photo.jpg", "rb") as f:
            photo = base64.b64encode(f.read())
        data = {"flight": self.FLIGHT,
                "stamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "height": self.HEIGHT,
                "latitude": self.LATITUDE,
                "longitude": self.LONGITUDE,
                "photo": photo}
        data = json.dumps(data, ensure_ascii=False)
        hash = sha1("%s|%s" % (data, _flask.config["DRONE_PASSWORD"])).hexdigest()
        ret = requests.post(self.URL + "/dronelocation", data={"data": data, "hash": hash})
        self.assertTrue(ret.content.isdigit())

    def test_dronelocation_missing_params(self):
        data = {"flight": self.FLIGHT,
                "stamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "height": self.HEIGHT}
        data = json.dumps(data, ensure_ascii=False)
        hash = sha1("%s|%s" % (data, _flask.config["DRONE_PASSWORD"])).hexdigest()
        ret = requests.post(self.URL + "/dronelocation", data={"data": data, "hash": hash})
        self.assertEqual(ret.status_code, 403)

        data = {"flight": self.FLIGHT,
                "stamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "height": self.HEIGHT,
                "latitude": self.LATITUDE,
                "longitude": self.LONGITUDE}
        data = json.dumps(data, ensure_ascii=False)
        ret = requests.post(self.URL + "/dronelocation", data={"data": data})
        self.assertEqual(ret.status_code, 405)

    def test_dronelocation_invalid_hash(self):
        data = {"flight": self.FLIGHT,
                "stamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "height": self.HEIGHT,
                "latitude": self.LATITUDE,
                "longitude": self.LONGITUDE}
        data = json.dumps(data, ensure_ascii=False)
        hash = sha1("%s|%s" % (data, _flask.config["DRONE_PASSWORD"])).hexdigest()[1:10]
        ret = requests.post(self.URL + "/dronelocation", data={"data": data, "hash": hash})
        self.assertEqual(ret.status_code, 403)

    def test_dronelocation_invalid_param_vals(self):
        data = {"flight": self.FLIGHT,
                "stamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "height": "adsk",
                "latitude": self.LATITUDE,
                "longitude": self.LONGITUDE}
        data = json.dumps(data, ensure_ascii=False)
        hash = sha1("%s|%s" % (data, _flask.config["DRONE_PASSWORD"])).hexdigest()
        ret = requests.post(self.URL + "/dronelocation", data={"data": data, "hash": hash})
        self.assertEqual(ret.status_code, 403)

    def test_dronelocation_integrity_err(self):
        data = {"flight": self.FLIGHT,
                "stamp": "2017-04-07 19:43:03",
                "height": self.HEIGHT,
                "latitude": self.LATITUDE,
                "longitude": self.LONGITUDE}
        data = json.dumps(data, ensure_ascii=False)
        hash = sha1("%s|%s" % (data, _flask.config["DRONE_PASSWORD"])).hexdigest()
        ret = requests.post(self.URL + "/dronelocation", data={"data": data, "hash": hash})
        self.assertEqual(ret.status_code, 403)

    def test_dronelocation_json_err(self):
        data = {"flight": self.FLIGHT,
                "stamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "height": self.HEIGHT,
                "latitude": self.LATITUDE,
                "longitude": self.LONGITUDE}
        data = json.dumps(data, ensure_ascii=False)[1:]
        hash = sha1("%s|%s" % (data, _flask.config["DRONE_PASSWORD"])).hexdigest()
        ret = requests.post(self.URL + "/dronelocation", data={"data": data, "hash": hash})
        self.assertEqual(ret.status_code, 403)






















