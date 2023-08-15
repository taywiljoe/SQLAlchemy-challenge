#################################################
# Import the dependencies.
#################################################
import numpy as np

import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
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
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )
    
###precipitation route###
##returns json with the date as the key and the value as the precipitation###
###only returns the jsonified precipitation data for the last year in the database###

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #year ago
    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query for the date and precipitation for a year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
        
    session.close()
    
    # Dictionary with date as the key and the value as the precipitation
    precip = {date: prcp for date, prcp in precipitation}
    
    # Return results
    return jsonify(precip)
    

###station route###
###returns jsonified data of all of the stations in the database
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # All stations data
    station = session.query(Station.name).all()
    session.close()
    
    # Return results
    return jsonify(list(np.ravel(station)))

###tobs route###
###returns jsonified data for the most activate station (USC00519281)###
###only returns the jsonified data for the last year of data###
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Calculate one year of data
    year = dt.datetime(strptime(recent_date,"%Y-%m-%d") - dt.timedelta(days=365))
    year_str = year.strftime("%Y-%m-%d")
    
    # Data for most active station
    most_active = session.query(Measurement.station, func.count()).group_by(Measurement.station).order_by(func.count().desc()).all()[0][0]
    tobs_year = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_str, Measurement.station == most_active).all()
    session.close()
    
    # Return results
    return jsonify(list(np.ravel(tobs_year)))


###start route###
###accepts the start date as a parameters from the URL###
###returns the min, max, and average temperatures calculated from the given start date to the end of the dataset###
@app.route("/api/v1.0/<sdate>")
def start(sdate):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #min, max, avg
    tobs_year = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= sdate).group_by(Measurement.date).all()
    
    data = []
    for result in tobs_year:
        row = {}
        row['Start Date'] = result[0]
        row['Lowest Temperature'] = float(result[1])
        row['Highest Temperature'] = float(result[2])
        row['Average Temperature'] = float(result[3])
        list.append(row)
        
        session.close()
        
    # Return results    
    return jsonify(list)

###start/end route###
###accpets the start and end dates as parameters for the URL###
###returns the min, max, and average temperatures calculated from the given start date to the given end date###
@app.route("/api/v1.0/start/end")
def stat(start=None, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    tobs_year = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start, Measurement.date <= end).group_by(Measurement.date).all()
    list = []
    for result in tobs_year:
        row = {}
        row['Start Date'] = result[0]
        row['Lowest Temperature'] = float(result[1])
        row['Highest Temperature'] = float(result[2])
        row['Average Temperature'] = float(result[3])
        list.append(row)

        session.close()
        
    # Return results    
    return jsonify(list)

if __name__ == '__main__':
    app.run(debug=True)
