# -*- coding: utf-8 -*-
"""
module for getting data from the database
"""

from decimal import Decimal
from app import App


class DBData(object):
    """
    class for getting various data from the database
    """

    @staticmethod
    def image(id):
        """
        get photo from the database
        :param id: int: id of the photo
        :return: str: binary data of the photo
        """
        assert type(id) == type(1) or id.isdigit(), "The photo id must be an integer!"
        sql = "SELECT Photo FROM photo WHERE Id_location=%s"
        with App() as app:
            photo = app.read(sql, (int(id),))
            assert photo, "This photo does not exist!"
            return photo[0]["Photo"]

    @staticmethod
    def lastFlight(drone):
        """
        get data about the last flight of the drone
        returns the last flight that has at least one location record
        :param drone: int: id of the drone
        :return: list of dicts: Id_flight, Start, Id_location, Stamp, Height, Longitude, Latitude
        """
        assert type(drone) == type(1) or drone.isdigit(), "The drone id must be an integer!"
        sql = "SELECT flight.Id_flight, Start, Id_location, Stamp, Height, Longitude, Latitude " \
              "FROM flight JOIN location ON flight.Id_flight=location.Id_flight " \
              "WHERE flight.Id_flight=(SELECT Id_flight FROM flight WHERE Id_drone=%s ORDER BY Start DESC LIMIT 1) " \
              "ORDER BY Stamp "
        with App() as app:
            lastflight = app.read(sql, (int(drone),))
            for l in lastflight:
                for key, val in l.iteritems():
                    if type(val) == type(Decimal("1.0")):
                        l[key] = float(val)
            return lastflight

    @staticmethod
    def getDrones():
        """
        get data about all drones/cars
        :return: list of dicts: Id_drone, Name
        """
        sql = "SELECT * FROM drone ORDER BY Name"
        with App() as app:
            return app.read(sql)

    @staticmethod
    def getPhotosData(count, drone):
        """
        get data about the last few photos of selected drone (except the photos themselfs)
        :param count: int: how many photos we want
        :param drone: int: id of the drone
        :return: list of dicts: Id_location, Stamp, Id_flight, Latitude, Longitude, Height
        """
        assert type(drone) == type(1) or drone.isdigit(), "The drone id must be an integer!"
        assert type(count) == type(1) or count.isdigit(), "The number of photos must be an integer!"
        sql = "SELECT location.Id_location, Stamp, flight.Id_flight, Latitude, Longitude, Height " \
              "FROM photo JOIN location ON photo.Id_location=location.Id_location " \
              "JOIN flight ON flight.Id_flight=location.Id_flight " \
              "WHERE Id_drone=%s ORDER BY Stamp DESC LIMIT %s "
        with App() as app:
            return app.read(sql, (int(drone), int(count)))

    @staticmethod
    def getFlightData(flight):
        """
        get data about he flight (no photos)
        :param flight: int: id of the desired flight
        :return: list of dicts: Id_location, Stamp, Id_flight, Latitude, Longitude, Height
        """
        assert type(flight) == type(1) or flight.isdigit(), "The flight id must be an integer!"
        sql = "SELECT Id_location, Stamp, Id_flight, Latitude, Longitude, Height " \
              "FROM location WHERE Id_flight=%s ORDER BY Stamp DESC "
        with App() as app:
            return app.read(sql, (int(flight),))
