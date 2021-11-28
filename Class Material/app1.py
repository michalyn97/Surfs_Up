import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#set up database
engine = create_engine("sqlite:///hawaii.sqlite")

#reflect the database
Base = automap_base()

Base.prepare(engine, reflect=True)

#save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#create a session link from Python to the database
session = Session(engine)

#set up flask
app = Flask(__name__)

#root route or index.html
@app.route("/")

#What will display on the page
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
    
    
#add the percipitation route
@app.route("/api/v1.0/precipitation")

#Diplay on page; Json precipitation info
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
      filter(Measurement.date >= prev_year).all()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

#define the route and route name
@app.route("/api/v1.0/stations")

#create a new stations function
def stations():
    #query to get all the stations into the database
    results = session.query(Station.station).all()
    #unravel into an array and convert into a list
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

#define the route and the route name
@app.route("/api/v1.0/tobs")

#create the function
def temp_monthly():
    #calculate the date one year ago from the last date in the database.
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #query the primary station for all the temperature observations from the previous year.
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    #unravel the results into a one-dimensional array and convert that array into a list. Then jsonify the list and return our results
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

#define the route and route name
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

#create a function and add parameters
def stats(start=None, end=None):
#create a query to select the minimum, average, and maximum temperatures
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
        #Note: the asterisk is used to indicate there will be multiple results for our query: minimum, average, and maximum temperatures.
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == "__main__":
     app.run(debug=True)