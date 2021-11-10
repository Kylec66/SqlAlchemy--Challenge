import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt
from flask import Flask, jsonify

# Database Setup

engine = create_engine("sqlite:///RESOURCES/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

last_12_months = dt.date(2017, 8, 23) - dt.timedelta(days=365)

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():

    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start date<br/>"
        f"/api/v1.0/start date/end date"
    )


#Precipitation
@app.route("/api/v1.0/precipitation")
# Return a list of precipitation from last year.
def precipitation():
    session = Session(engine)
    results = session.query(measurement.date, measurement.prcp).all()
    session.close()

    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        all_precipitation.append(precipitation_dict)
    return jsonify(all_precipitation)

# Stations
@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    results = session.query(station.station).all()
    
    session.close()

    every_station = list(np.ravel(results))
    
    return jsonify(every_station)

# TOBS
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results = session.query(measurement.date, measurement.tobs).filter((measurement.station) == 'USC00519281', (measurement.date)>=last_12_months).all()
    session.close()
    
    every_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict['tobs'] = tobs
        every_tobs.append(tobs_dict)
    return jsonify(every_tobs)

# Start Date

@app.route("/api/v1.0/<start_date>")
def date_temps(start_date):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start_date).all()
    session.close()

    all_date_temps = []
    for result in results:
        date_temps_dict = {}
        date_temps_dict["TMIN"] = result[0]
        date_temps_dict["TAVG"] = result[1]
        date_temps_dict["TMAX"] = result[2]
        
        all_date_temps.append(date_temps_dict)
    return jsonify(all_date_temps)

# Start and End Date
   
@app.route("/api/v1.0/<start_date>/<end_date>")
def range_temps(start_date, end_date):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    session.close()

    all_range_temps = []
    for result in results:
        range_temps_dict = {}
        range_temps_dict["TMIN"] = result[0]
        range_temps_dict["TAVG"] = result[1]
        range_temps_dict["TMAX"] = result[2]
        
        all_range_temps.append(range_temps_dict)
    return jsonify(all_range_temps)


if __name__ == '__main__':
    app.run(debug=True)