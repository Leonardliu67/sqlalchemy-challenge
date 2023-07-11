import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Set up database engine for Flask app
# Create function allows access to SQLite database file
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Reflect database into classes
Base = automap_base()
# Reflect tables
Base.prepare(engine, reflect=True)
# Set class variables
Measurements = Base.classes.measurement
Stations = Base.classes.station
# Creates session link from Python to SQLite database
session = Session(engine)
# Create Flask app, all routes go after this code
app = Flask(__name__)

# Define welcome route
@app.route("/")

def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!<br>
    Available Routes:<br>
    ######################################<br>
    /api/v1.0/precipitation<br>
    /api/v1.0/stations<br>
    /api/v1.0/tobs<br>
    /api/v1.0/start/end<br>
    ''') 
@app.route("/api/v1.0/precipitation")

def precipitation():
# convert the query results from your precipitation
# analysis (i.e. retrieve only the last 12 months of data) to 
# a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
    session = Session(engine)
    last_yr = dt.date(2017,8,23) - dt.timedelta(days=365)
    last_yr_prcp = session.query(Measurements.date,Measurements.prcp).\
        filter(Measurements.date >= last_yr).all()
    session.close()
    last_yr_prcp_dict = dict(last_yr_prcp)
    return jsonify(last_yr_prcp_dict)
########################################################################

@app.route("/api/v1.0/stations")

def stations():
# Return a JSON list of stations from the dataset.
    session = Session(engine)
    station = session.query(Stations.station,Stations.name).all()
    session.close()
    station_dict = dict(station)
    return jsonify(station_dict)
########################################################################

@app.route("/api/v1.0/tobs")

def tobs():
# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
    last_yr = dt.date(2017,8,23) - dt.timedelta(days=365)
    session = Session(engine)
    station_data = session.query(Measurements.station,func.count(Measurements.station)).\
                            group_by(Measurements.station).all()
    station_data.sort(key=lambda a:a[1],reverse=True)
    most_active_station = station_data[0][0]
    t_data = session.query(Measurements.date,Measurements.tobs).\
                    filter(Measurements.station == most_active_station).\
                    filter(Measurements.date >= last_yr)
    session.close()
    t_data_dict = dict(t_data)
    return jsonify(t_data_dict)
 ########################################################################   

@app.route("/api/v1.0/<start>")

def data(start):
    start_day = dt.datetime.strptime(start,"%Y-%m-%d")
    session = Session(engine)
    min_max_avg = session.query(func.min(Measurements.tobs),func.max(Measurements.tobs),func.avg(Measurements.tobs)).\
                        filter(Measurements.date >= start_day).all()
    session.close()
    mma = list(np.ravel(min_max_avg))
    return jsonify(mma)

@app.route("/api/v1.0/<start>/<end>")

def data1(start,end):
    start_day = dt.datetime.strptime(start,"%Y-%m-%d")
    end_day = dt.datetime.strptime(end,"%Y-%m-%d")
    session = Session(engine)
    min_max_avg = session.query(func.min(Measurements.tobs),func.max(Measurements.tobs),func.avg(Measurements.tobs)).\
                        filter(Measurements.date >= start_day).\
                        filter(Measurements.date <= end_day).all()
    session.close()
    mma1 = list(np.ravel(min_max_avg))
    return jsonify(mma1)


if __name__ == "__main__":
    app.run(debug=True)