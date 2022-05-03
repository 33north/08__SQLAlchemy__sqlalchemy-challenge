import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct, desc

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
        f"<br/>"
        f"Available Routes via date range between 2010-01-01 to 2018-08-23:<br/>"
        f"/api/v1.0/start<br/>"
        f"^---(replace <em>start</em> with a start date)<br/>"
        f"/api/v1.0/start/end<br/>"
        f"^---(replace <em>start</em> and <em>end</em> with start and end date, respectively)<br/>"
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

    # Creates list of station names
    station_list = list(np.ravel(station_names))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Session query of Measurement table for date and tobs of most active station of the most recent year
    tobs_date = session.query(Measurement.date, Measurement.tobs).all()

    # Found unique station names, counted them, and sort them
    distinct_station_ct = session.query(Measurement.station, func.count(Measurement.station).label("Station Activity")).group_by(Measurement.station)
    sorted_station_list = distinct_station_ct.order_by(desc("Station Activity")).all()
    
    most_active_station = sorted_station_list[0][0]

    # Find most recent date
    recent_date_query = session.query(func.max(Measurement.date)).all()
    max_date = recent_date_query[0][0]

    max_date_list = max_date.split("-")
    starting_date = dt.date(int(max_date_list[0]), int(max_date_list[1]), int(max_date_list[2]))

    one_year = dt.timedelta(days = 366)

    one_year_prior = starting_date - one_year
    
    # Query the most active station name date and tobs
    active_station_query = session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date > one_year_prior)

    # active_station_query_list = [data for data in active_station_query]

    state_date_tobs_list = []
    for station, date, tobs in active_station_query:
        tobs_dates_station_dict = {}
        tobs_dates_station_dict["station"] = station
        tobs_dates_station_dict["date"] = date
        tobs_dates_station_dict["temperature observed"] = tobs
        state_date_tobs_list.append(tobs_dates_station_dict)
    
    return jsonify(state_date_tobs_list)

@app.route("/api/v1.0/<string:start>")
def start(start=None):
    # Session query of Measurement table for tobs starting at a given date
    if start:
        temp_calc_min = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).scalar()
        temp_calc_max = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).scalar()
        temp_calc_avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).scalar()
        response = jsonify(
            {
                "tmin: ": temp_calc_min,
                "tmax: ": temp_calc_max,
                "tavg: ": temp_calc_avg 
            }
        )
        return response
    else:
        return f"Gotcha"

    return jsonify({"error": "Character not found."}), 404

@app.route("/api/v1.0/<string:start>/<string:end>")
def start_end(start=None, end=None):
    # Session query of Measurement table for tobs between a given start and end date
    if end:
        temp_calc_min = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).scalar()
        temp_calc_max = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).scalar()
        temp_calc_avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).scalar()
        response = jsonify(
            {
                "tmin: ": temp_calc_min,
                "tmax: ": temp_calc_max,
                "tavg: ": temp_calc_avg 
            }
        )
        return response
    # elif start:
    #     temp_calc_min = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).scalar()
    #     temp_calc_max = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).scalar()
    #     temp_calc_avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).scalar()
    #     response = jsonify(
    #         {
    #             "tmin: ": temp_calc_min,
    #             "tmax: ": temp_calc_max,
    #             "tavg: ": temp_calc_avg 
    #         }
    #     )
    else:
        return f"Gotcha"

    return jsonify({"error": "Character not found."}), 404

if __name__ == '__main__':
    app.run(debug = True)
