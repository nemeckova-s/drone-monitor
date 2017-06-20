# -*- coding: utf-8 -*-
"""

"""

import json
from _mysql import IntegrityError
from hashlib import sha1
from datetime import datetime
from app import App

try:
    from __main__ import _flask
except ImportError:
    from web import _flask


class DroneAPI(object):
    """
    methods for requests from drone
    """

    START_PARAMS = (("start", True),
                    ("drone", True))
    LOCATION_PARAMS = (("flight", True),
                       ("stamp", True),
                       ("height", True),
                       ("longitude", True),
                       ("latitude", True),
                       ("photo", False))
    PARSERS = {"start": (lambda e: datetime.strptime(e, "%Y-%m-%d %H:%M:%S"),
                         "Value Error: start value is not ISO datetime!"),
               "drone": (lambda e: int(e),
                         "Value Error: drone value is not an integer!"),
               "flight": (lambda e: int(e),
                          "Value Error: flight value is not an integer!"),
               "stamp": (lambda e: datetime.strptime(e, '%Y-%m-%d %H:%M:%S'),
                         "Value Error: stamp value is not ISO datetime!"),
               "height": (lambda e: float(e),
                          "Value Error: height is not a float!"),
               "longitude": (lambda e: float(e),
                             "Value Error: longitude is not a float!"),
               "latitude": (lambda e: float(e),
                            "Value Error: latitude is not a float!"),
               "photo": (lambda e: e.decode("base64"),
                         "Base64 Decode Error: Photo cannot be decoded from Base64!")
               }

    def __init__(self, rawdata, hash):
        """
        encode raw data to utf8, check hash and decode to json, set decoded data to self.data
        :param rawdata: raw data from the request
        :param hash: hash imprint of the raw data combined with "|" and drone password from config
        :return: DroneAPI object
        """
        data = rawdata.encode("utf8")
        assert sha1("%s|%s" % (data, _flask.config["DRONE_PASSWORD"])).hexdigest() == hash, \
            "Security Error: Hash does not match!"
        try:
            data = json.loads(data)
        except Exception:
            raise AssertionError("JSON Decode Error")
        self.data = data

    def parse(self, params):
        """
        parse self.data using the params
        :param params: sequence: first value is method to use for parsing, second value is string saying what weng wrong
        :return: dict: parsed values of self.data
        """
        ret = {}
        for (key, compulsary) in params:
            if compulsary:
                assert key in self.data, "Data Error: Missing %s value!" % key
            if key in self.data:
                try:
                    ret[key] = self.PARSERS[key][0](self.data[key])
                except Exception:
                    raise AssertionError(self.PARSERS[key][1])
        return ret

    def start(self):
        """
        parse self.data and save start data to database
        :return: int: id of the flight record in database
        """
        vals = self.parse(self.START_PARAMS)
        with App() as app:
            sql = "INSERT INTO flight (Id_drone, Start) VALUES (%s, %s)"
            try:
                app.write(sql, (vals["drone"], vals["start"]))
            except IntegrityError:
                raise AssertionError("Integrity Error: This flight already exists!")
            id = app.read("SELECT LAST_INSERT_ID() AS Id")[0]["Id"]
            return id

    def location(self):
        """
        parse self.data and save location data to database
        :return: int: id of the location record in database
        """
        vals = self.parse(self.LOCATION_PARAMS)
        with App() as app:
            sql = "INSERT INTO location (Id_flight, Height, Latitude, Longitude, Stamp) " \
                  "VALUES (%s, %s, %s, %s, %s)"
            try:
                app.write(sql,
                          (vals["flight"], vals["height"], vals["latitude"], vals["longitude"], vals["stamp"]),
                          commit="photo" not in vals)
                id = app.read("SELECT LAST_INSERT_ID() AS Id")[0]["Id"]
                if "photo" in vals:
                    sql = "INSERT INTO photo (Id_location, Photo) VALUES (%s, %s)"
                    app.write(sql, (id, vals["photo"]))
                return id
            except IntegrityError, e:
                print "%s" % (e.message or e)
                raise AssertionError("Integrity Error: This flight does not exist!")
