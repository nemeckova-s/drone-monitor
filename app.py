# -*- coding: utf-8 -*-
"""

"""

import MySQLdb
try:
    from __main__ import _flask
except ImportError:
    from web import _flask


class App(object):
    """
    App class with methods and properties for database connection
    """

    MY_AUTH_PASSWD = "PwA_2016_17"

    def __init__(self):
        """
        constructor
        :return:
        """
        self.__connection = None

    @property
    def connection(self):
        if not self.__connection:
            dbparams = _flask.config["MYSQL_CONNECT"]
            self.__connection = MySQLdb.connect(**dbparams)
        return self.__connection

    def __enter__(self):
        """
        for using with ... as ...:
        :return: self
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        for using with ... as ...:
        what to do at the end
        :param exc_type: error type
        :param exc_val: error value
        :param exc_tb: error traceback
        :return:
        """
        try:
            if self.__connection:
                self.__connection.close()
        except:
            pass

    def read(self, sql, params=()):
        """
        SELECT query for db
        :param sql: sql SELECT query with %s instead of parameters
        :param params: parameters of the query
        :return: dict: fetched response from db
        """
        cursor = self.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql, params)
        return cursor.fetchall()

    def write(self, sql, params=(), commit=True):
        """
        INSERT, REPLACE or DELETE query for db
        :param sql: sql query with %s instead of parameters
        :param params: parameters of the query
        :return: int: number of affected rows
        """
        cursor = self.connection.cursor()
        cursor.execute(sql, params)
        if commit:
            self.connection.commit()
        return cursor.rowcount























