# import dependencies
from flask import Flask
import datetime as dt
import numpy as np
import pandas as pd
#sql stuff
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
# flask needs to go RIGHT AFTER SQL stuff
from flask import Flask, jsonify


#import SQL lite data base
engine = create_engine("sqlite:///hawaii.sqlite")
# taking table in DB and turning it into a python object ---------------------------------------
# base is an instance of the automap_base() class
Base = automap_base()
# reflect the tables
# use auto_mapbase() to get the data into the table
# "prepare" creating objects to represent the tables.
Base.prepare(engine, reflect=True)

# save references of each table
# creating an object for the measurement / stations.
Measurement =  Base.classes.measurement
Station = Base.classes.station
#create a session link from Python to our DB
session = Session(engine)


# creating a New Flask App Instance named app
app = Flask(__name__)

# defining route default route
@app.route('/')
#creating welcome() function
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')
#perceptitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
      filter(Measurement.date >= prev_year).all()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)
#stations route
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)
# tobs route
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)
# stats route
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    #detmine the starting and ending date 
    if not end:
        results = session.query(*sel).\
        filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps=temps)
    # calc min avg and max
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)

