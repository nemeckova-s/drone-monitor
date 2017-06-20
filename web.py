# -*- coding: utf-8 -*-

import os
from flask import Flask, abort, render_template, request
from io import BytesIO

os.chdir(os.path.dirname(os.path.abspath(__file__)))

_flask = Flask(__name__)
if __name__ == '__main__':
    _flask.config.from_object('config.ConfigDevelopment')
else:
    _flask.config.from_object('config.Config')

#-----------------------------------------------------------------------------------------------------------------------

@_flask.before_request
def before_request():
    pass

@_flask.after_request
def after_request(response):
    return response

@_flask.teardown_request
def teardown_request(exception):
    pass

#-----------------------------------------------------------------------------------------------------------------------

@_flask.errorhandler(404)
def pg404(e):
    return render_template("error.html", error=ValueError(u"Tato stránka neexistuje.")), 404

def bad_request(statuscode, message):
    """
    create an error response
    :param statuscode: int: statuscode of the error
    :param message: message of the error
    :return: response object
    """
    from flask import jsonify
    response = jsonify({"message": message})
    response.status_code = statuscode
    return response

#-----------------------------------------------------------------------------------------------------------------------

from droneapi import DroneAPI
from dbdata import DBData

@_flask.route('/', methods=['GET', 'POST'])
def index():
    """
    index page
    :return: response object
    """
    drones = DBData.getDrones()
    return render_template('index.html', drones=drones)

@_flask.route('/dronestart', methods=['POST',])
def dronestart():
    """
    start of the drone
    expects data and hash in the request
    :return: str/response object: number of the new flight / response object in the case of an error
    """
    try:
        data = request.form["data"]
        hash = request.form["hash"]
    except KeyError:
        return bad_request(405, "Missing compulsory parameters data or hash!")
    try:
        droneapi = DroneAPI(data, hash)
        return str(droneapi.start())
    except AssertionError, e:
        return bad_request(403, e.message)

@_flask.route('/dronelocation', methods=['POST',])
def dronelocation():
    """
    location of the drone
    expects data and hash in the request
    :return: str/response object: number of the new location record / response object in the case of an error
    """
    try:
        data = request.form["data"]
        hash = request.form["hash"]
    except KeyError:
        return bad_request(405, "Missing compulsory parameters data or hash!")
    try:
        droneapi = DroneAPI(data, hash)
        return str(droneapi.location())
    except AssertionError, e:
        return bad_request(403, e.message)

@_flask.route('/image/<int:id>.%s' % _flask.config["PHOTO_FORMAT"], methods=['GET',])
def image(id):
    """
    get image file
    :param id: int: number of the image
    :return: image file
    """
    from flask import send_file
    try:
        img = DBData.image(id)
    except AssertionError:
        abort(404)
        return
    img = BytesIO(img)
    return send_file(img, mimetype='image/%s' % _flask.config["PHOTO_FORMAT"])

@_flask.route('/lastflight/<int:drone>', methods=['GET',])
def lastflight(drone):
    """
    get data about the last flight of given drone
    :param drone: int: number of the drone
    :return: json: flight data
    """
    from flask import jsonify
    try:
        lastflight = DBData.lastFlight(drone)
    except AssertionError, e:
        return bad_request(405, e.message)
    return jsonify(results=lastflight)

@_flask.route('/dronephotos/<int:drone>', methods=['GET',])
def dronephotos(drone):
    """
    get html of drone photos template
    :param drone: int: number of the drone
    :return: response object: rendered template
    """
    try:
        photos = DBData.getPhotosData(_flask.config["PHOTO_CHOICES_COUNT"], drone)
    except AssertionError, e:
        return bad_request(405, e.message)
    return render_template("photochoices.html", photos=photos, format=_flask.config["PHOTO_FORMAT"])

@_flask.route('/dronepath/<int:flight>', methods=['GET',])
def dronepath(flight):
    """
    get html of a flight template
    :param flight: number of the flight
    :return: response object: rendered template
    """
    try:
        path = DBData.getFlightData(flight)
    except AssertionError, e:
        return bad_request(405, e.message)
    return render_template("dronepath.html", path=path, format=_flask.config["PHOTO_FORMAT"])

@_flask.route('/gpstosjtsk', methods=['POST',])
def gpsToSjtsk():
    """
    convert wgs-84 to s-jtsk
    :return: json / error response: results
    """
    import requests
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()
    from flask import jsonify
    try:
        jsn = request.json
    except Exception, e:
        return bad_request(405, u"Missing JSON data.")
    r = requests.post(_flask.config["REST_API_URL"] + "multipleGpsToSJTSK", json=jsn)
    if r.status_code != 200:
        return bad_request(r.status_code, u"REST API request wasn't successful.")
    return jsonify(results=r.content)

@_flask.route('/getmap/<float:x>/<float:y>', methods=['GET',])
def getMap(x, y):
    """
    get map data around given point
    :param x: float: x coord
    :param y: y coord
    :return: json / error response: results
    """
    import requests
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()
    from flask import jsonify
    r = requests.get(_flask.config["REST_API_URL"] + "getTilesAroundMap/%f/%f/1" % (x, y))
    if r.status_code != 200:
        return bad_request(r.status_code, u"REST API request wasn't successful.")
    return jsonify(results=r.content)


#-----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    _flask.run(host='0.0.0.0', port=14859, debug=True)
