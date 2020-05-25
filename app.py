# Import dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Setup database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create Flask app
app= Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        """
        Welcome to this API! </br>
        Below you can see the available routes. </br>
        ---------------------------------------</br>
        </br>
        """
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    # Set up the connection
    session = Session(engine)

    response = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    prcpList = []

    for date, prcp in response:
        prcpDict = {}
        prcpDict["Date"]=date
        prcpDict["Prcp"]=prcp
        prcpList.append(prcpDict)

    return jsonify(prcpList)


@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    response = session.query(Station.station).all()
    session.close()

    stationList = list(np.ravel(response))

    return jsonify(stationList)


@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    response = session.query(Measurement.tobs, Measurement.date)\
    .filter(Measurement.station == "USC00519281")\
    .filter(Measurement.date >= '2016-08-23')
    session.close()

    tobsList = []
    for tobs, date in response:
        tobsDict = {}
        tobsDict["Date"] = date
        tobsDict["TOBS"] = tobs
        tobsList.append(tobsDict)

    return jsonify(tobsList)


@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    
    def temp(function, start):
        response = session.query(Measurement, function(Measurement.tobs))\
        .filter(Measurement.date == start)
        return response[0][1]

    tmin = temp(func.min, start)
    tmax = temp(func.max, start)
    tavg = round(temp(func.avg, start),2)

    startDict = {}
    startDict["TMIN"] = tmin
    startDict["TMAX"] = tmax
    startDict["TAVG"] = tavg

    return jsonify(startDict)


@app.route("/api/v1.0/<start>/<end>")
def range(start, end):
    session = Session(engine)
    
    def temp(function, start, end):
        response = session.query(Measurement, function(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date <= end)
        return response[0][1]

    tmin = temp(func.min, start, end)
    tmax = temp(func.max, start, end)
    tavg = round(temp(func.avg, start, end),2)

    rangeDict = {}
    rangeDict["TMIN"] = tmin
    rangeDict["TMAX"] = tmax
    rangeDict["TAVG"] = tavg

    return jsonify(rangeDict)


if __name__ == "__main__":
    app.run(debug=True)