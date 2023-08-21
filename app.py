# Import the dependencies.
import numpy as np

import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        "<br/>"
        f"For API routes listed below, start and start/end date format: YYYY-MM-DD<br/>"
        f"Choose dates between 01-01-2010 and 08-23-2017<br/>"
        "<br/>"
        f"More Specific API Routes by Start Date:<br/>"
        f"/api/v1.0/start<br/>"
        "<br/>"
        f"More Specific API Routes by Start Date and End Date:<br/>"
        f"/api/v1.0/start/end<br/>"
        "<br/>"
        f"Example API Routes:<br/>"
        f"/api/v1.0/2010-01-01<br/>"
        f"/api/v1.0/2014-08-15<br/>"
        f"/api/v1.0/2016-05-01<br/>"
        f"/api/v1.0/2012-01-01/2017-08-01<br/>"
        f"/api/v1.0/2017-05-01/2017-05-31<br/>"
        f"/api/v1.0/2016-02-04/2017-02-20<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list"""
    # Find the most recent date in the data set.
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # Calculate the date one year from the last date in data set.
    one_year_recent_date = dt.date(2017,8,23) - dt.timedelta(days = 365)

    # Query precipitation data for the last year and return the jsonified data.
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= '2016-08-23').order_by(Measurement.date).all()
    
    session.close()
    
    # Convert list of tuples into normal list
    all_precipitation = list(np.ravel(results))
    return jsonify(all_precipitation)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all stations and return the jsonified data.
    results = session.query(Station.station).distinct().all()
  
    session.close()
    
    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query most active year id and the most recent date in the data set.
    most_active_station_id = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    
    most_active_station_date = session.query(Measurement.station, Measurement.date).\
    filter(Measurement.station == most_active_station_id[0]).order_by(Measurement.date.desc()).first()
    
    # Calculate the date one year from the last date in data set.
    last_active_station_date = dt.date(2017,8,18) - dt.timedelta(days = 365)
    
    # Query temperature(tobs) data for the last year and return the jsonified data.
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
    filter(Measurement.station == most_active_station_id[0]).filter(Measurement.date >= '2016-08-18').all()
    
    session.close()

    # Convert list of tuples into normal list
    most_active_recent_year_tobs = list(np.ravel(results))
    return jsonify(most_active_recent_year_tobs)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all min temperature, avg temperature, and max temperature for a specified start date """
    # Query data for specific start date and return the jsonified data.
    start_date_results = session.query(func.min(Measurement.tobs),\
    func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
  
    session.close()
    
    # Convert list of tuples into normal list
    start_date_temp_stats = list(np.ravel(start_date_results))
    return jsonify(start_date_temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all min temperature, avg temperature, and max temperature for a specified start date and          end date"""
    # Query data for specific start date and end date, then return the jsonified data.
    start_end_date_results = session.query(func.min(Measurement.tobs),\
    func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start).\
    filter(Measurement.date <= end).all()
  
    session.close()
    
    # Convert list of tuples into normal list
    start_end_date_temp_stats = list(np.ravel(start_end_date_results))
    return jsonify(start_end_date_temp_stats)

if __name__ == '__main__':
    app.run(debug=True)
