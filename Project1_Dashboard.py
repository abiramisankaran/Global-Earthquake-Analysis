import os
import pandas as pd
import mysql.connector
import streamlit as st

st.set_page_config(page_title="Earthquake Project Dashboard", layout="wide")

# Queries drevied from earthquake_data.

QUERIES = [
    {
        "num": 1,
        "title": 'Top 10 strongest earthquakes',
        "sql": 'select id,country, mag from earthquake_data order by mag desc limit 10;',
        "headers": ['id', 'country', 'mag'],
    },
    {
        "num": 2,
        "title": 'Top 10 deepest earthquakes by depth in km.',
        "sql": 'select id,depth_km from earthquake_data order by depth_km desc limit 10;',
        "headers": ['id', 'depth_km'],
    },
    {
        "num": 3,
        "title": 'Shallow earthquakes < 50 km and mag > 7.5',
        "sql": 'select id, depth_km, mag from earthquake_data where depth_km < 50 and mag > 7.5\norder by mag desc;',
        "headers": ['id', 'depth_km', 'mag'],
    },
    {
        "num": 5,
        "title": 'Average magnitude per magnitude type',
        "sql": 'select magType,avg(mag) AS average_magnitude from earthquake_data \ngroup by magType order by average_magnitude desc;',
        "headers": ['Mag_type', 'Avg_mag'],
    },
    {
        "num": 6,
        "title": 'Year with most earthquakes',
        "sql": 'select year(time) as year, count(*) as earthquake_count from earthquake_data\ngroup by year(time)order by earthquake_count desc limit 1;',
        "headers": ['Year', 'Earthquake Count'],
    },
    {
        "num": 7,
        "title": 'Month with highest number of earthquakes',
        "sql": 'select month(time) as month_number,monthname(time) as month,count(*) AS earthquake_count\nfrom earthquake_data group by month(time),monthname(time)\norder by earthquake_count desc limit 1;',
        "headers": ['month_number', 'month', 'earthquake_count'],
    },
    {
        "num": 8,
        "title": 'Day of week with most earthquakes',
        "sql": 'select dayname(time) as dayofweek,count(*) as earthquake_count from earthquake_data\ngroup by dayofweek(time),dayname(time)\norder by earthquake_count desc limit 1;',
        "headers": ['day_of_week', 'earthquake_count'],
    },
    {
        "num": 9,
        "title": 'Count of earthquakes per hour of day',
        "sql": 'select hour(time) as hour_of_day,count(*) as earthquake_count from earthquake_data\ngroup by hour(time) order by hour_of_day;',
        "headers": ['hour_of_day', 'earthquake_count'],
    },
    {
        "num": 10,
        "title": 'Most active reporting network',
        "sql": 'select net,count(*) as earthquake_count from earthquake_data \ngroup by net order by earthquake_count desc limit 1;',
        "headers": ['network', 'earthquake_count'],
    },
    {
        "num": 11,
        "title": 'Top 5 places with highest casualties',
        "sql": 'select place, sum(felt) as total_casualties from earthquake_data \ngroup by place order by total_casualties desc limit 5;',
        "headers": ['places', 'Highest_casualities'],
    },
    {
        "num": 14,
        "title": 'Count of reviewed vs automatic earthquakes',
        "sql": 'select status, Count(*) as earthquake_count from earthquake_data \ngroup by status order by earthquake_count DESC;',
        "headers": ['status', 'earthquake_count'],
    },
    {
        "num": 15,
        "title": 'Count by earthquake type',
        "sql": 'select type,count(*) as earthquake_count from earthquake_data group by type \norder by earthquake_count desc;',
        "headers": ['earthquake_type', 'earthquake_count'],
    },
    {
        "num": 16,
        "title": 'Number of earthquakes by datatype',
        "sql": 'select types,count(*) as earthquake_count from earthquake_data group by types\norder by earthquake_count desc;',
        "headers": ['types', 'earthquake_count'],
    },
    {
        "num": 18,
        "title": 'Events with high station coverage',
        "sql": 'select id, place, nst from earthquake_data where nst >50 order by nst desc;',
        "headers": ['id', 'place', 'station_count'],
    },
    {
        "num": 19,
        "title": 'Number of tsunamis triggered per year.',
        "sql": 'select year(time) as year,count(*) as tsunami_count from earthquake_data where tsunami = 1\ngroup by year(time) order by year;',
        "headers": ['year', 'tsunami_count'],
    },
    {
        "num": 20,
        "title": 'Count earthquakes by alert levels',
        "sql": 'select alert,count(*) as earthquake_count from earthquake_data where alert is not null group by alert\norder by earthquake_count desc;',
        "headers": ['alert_level', 'earthquake_count'],
    },
    {
        "num": 21,
        "title": 'Top 5 Countries with the highest average magnitude of earthquakes in the past 5 years',
        "sql": 'select country,avg(mag) as average_magnitude from earthquake_data\nwhere country is not null and mag is not null and time >= date_sub(curdate(),interval 5 year)\ngroup by country order by average_magnitude desc limit 5;',
        "headers": ['country', 'average_magnitude'],
    },
    {
        "num": 22,
        "title": 'Countries that have experienced both shallow and deep earthquakes within the same month',
        "sql": 'select country,YEAR(time) as year,MONTH(time) as month from earthquake_data\nwhere country is not null and time is not null and depth_km is not null group by country, YEAR(time), MONTH(time)\nhaving MIN(depth_km) < 50 and MAX(depth_km) >= 50 order by country, year, month;',
        "headers": ['country', 'year', 'month'],
    },
    {
        "num": 23,
        "title": 'Year-over-Year growth rate in the total number of earthquakes globally.',
        "sql": 'select YEAR(time) as year, count(*) as earthquake_count,round((count(*) - lag(count(*)) \nover (order by YEAR(time))) / lag(count(*)) over (order by YEAR(time)) * 100,2) as yoy_growth_rate\nfrom earthquake_data where time is not null group by YEAR(time) order by year;',
        "headers": ['year', 'earthquake_count', 'yoy_growth_rate'],
    },
    {
        "num": 24,
        "title": '3 most seismically active regions by combining both frequency and average magnitude.',
        "sql": 'select country, count(*) as earthquake_count,round(avg(mag), 2) as avg_magnitude,\nround(count(*) * avg(mag), 2) as seismic_score from earthquake_data\nwhere country is not null group by country order by seismic_score desc limit 3;',
        "headers": ['country', 'earthquake_count', 'avg_magnitude', 'seismic_score'],
    },
    {
        "num": 25,
        "title": 'The average depth of earthquakes within ±5° latitude range of the equator by country',
        "sql": 'select country, round(avg(depth_km), 2) as average_depth_km from earthquake_data\nwhere country is not null and latitude between -5 and 5 and depth_km  group by country \norder by average_depth_km DESC;',
        "headers": ['country', 'avg_depth'],
    },
    {
        "num": 26,
        "title": 'Countries having the highest ratio of shallow to deep earthquakes',
        "sql": 'select country,sum(depth_km < 70) as shallow, sum(depth_km >= 70) as deep,\nround(sum(depth_km < 70) / sum(depth_km >= 70), 2) as ratio from earthquake_data\nwhere country is not null group by country having deep > 0 order by ratio desc limit 10;',
        "headers": ['country', 'shallow', 'deep', 'ratio'],
    },
    {
        "num": 27,
        "title": 'Average magnitude difference between earthquakes with tsunami alerts and those without',
        "sql": 'select round(avg(case when tsunami = 1 then mag end), 2) as tsunami_avg,\n            round(avg(case when tsunami = 0 then mag end), 2) as no_tsunami,\n            round(avg(case when tsunami = 1 then mag end) - avg(case when tsunami = 0 then mag end), 2 )\n            as mag_dif from earthquake_data;',
        "headers": ['tsunami_avg', 'no_tsunami', 'mag_dif'],
    },
    {
        "num": 28,
        "title": 'Events with the lowest data reliability',
        "sql": 'select id,round(gap, 2) as gap,round(rms, 2) as rms,round((gap + rms) / 2, 2) as err_score\nfrom earthquake_data where gap is not null and rms is not null order by err_score desc limit 10;',
        "headers": ['id', 'gap', 'rms', 'err_score'],
    },
    {
        "num": 30,
        "title": 'Regions with the highest frequency of deep-focus earthquakes (depth > 300 km).',
        "sql": 'select country,count(*) as deep_count from earthquake_data\nwhere depth_km > 300 and country is not null group by country order by deep_count desc limit 10;',
        "headers": ['country', 'deep_count'],
    },
]

# DB connection - cached

@st.cache_resource
def get_connection(host, user, password, database):
    return mysql.connector.connect(
          host=host, user=user, password=password, database=database
    )


def run_query(conn, sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cols = [c[0] for c in cursor.description]
    cursor.close()
    return pd.DataFrame(rows, columns=cols)

# Database connection - hardcoded

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "abiramisql121089"
DB_DATABASE = "earthquake_db"
 
st.title("🌍 Earthquake Analysis — Project Dashboard")
 
if "conn" not in st.session_state:
    try:
        st.session_state.conn = get_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE)
    except Exception as e:
        st.error(f"Connection failed: {e}")
        st.session_state.conn = None
 
conn = st.session_state.conn
 
if conn is None:
    st.stop()

# Query picker

options = [f"{q['num']}. {q['title']}" for q in QUERIES]
choice = st.selectbox("Choose a query", options)
selected = QUERIES[options.index(choice)]

with st.expander("Show SQL"):
    st.code(selected["sql"], language="sql")

try:
    df = run_query(conn, selected["sql"])
except Exception as e:
    st.error(f"Query failed: {e}")
    st.stop()

st.subheader(selected["title"])
st.dataframe(df, use_container_width=True)

# Charting

if df.shape[1] == 2 and df.shape[0] > 1:
    label_col, value_col = df.columns[0], df.columns[1]
    if pd.api.types.is_numeric_dtype(df[value_col]):
        st.bar_chart(df.set_index(label_col)[value_col])
elif selected["num"] == 23 and "yoy_growth_rate" in df.columns:
    st.line_chart(df.set_index("year")["yoy_growth_rate"])
elif selected["num"] == 9 and "hour_of_day" in df.columns:
    st.bar_chart(df.set_index("hour_of_day")["earthquake_count"])