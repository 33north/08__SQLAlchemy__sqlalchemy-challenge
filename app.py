import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, render_template, jsonify

#################################################
# Database Setup
#################################################
# Create and connect engine to db
engine = create_engine("sqlite:///resources/hawaii.sqlite")
connection = engine.connect()

# Reflect db
Base = automap_base()
Base.prepare(engine, reflect = True)

# Saving tables from the reflected db
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session from engine
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Session query of Measurement table for date and prcp
    prcp_date = session.query(Measurement.date, Measurement.prcp).all()

    # Close session
    session.close()

    # Changing data to dictionary
    precipitation_list = []
    for date, prcp in prcp_date:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipitation"] = prcp
        precipitation_list.append(prcp_dict)

    return jsonify(precipitation_list)

@app.route("/api/v1.0/stations")
def stations():
    # Session query of Station table for station
    station_names = session.query(Station.station).all()

    # Close session
    session.close()

    station_list = list(np.ravel(station_names))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    
    return()

if __name__ == '__main__':
    app.run(debug = True)
