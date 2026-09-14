# Global-Earthquake-Analysis
This project builds an end-to-end pipeline that pulls five years of global earthquake records from the USGS Earthquake API, cleans and enriches the data, and loads it into a MySQL database. A set of SQL-driven analyses and an interactive Streamlit dashboard are then used to explore seismic patterns.


Pipeline & Tooling Summary
Stage	Tool / Technology	Purpose
Extract	>> USGS FDSN Event API + requests	>>>Pull raw GeoJSON earthquake records, 2021–2026
Transform >>	pandas, numpy, re	>>> Clean text/numeric fields, impute missing values, derive features
Load >>	mysql-connector-python >>>	Bulk insert into the earthquake_data MySQL table
Analyze	>> SQL (aggregation, window functions)  >>>	20+ business questions on frequency, magnitude, depth, geography
Present >>	Streamlit + pandas  >>>	Interactive dashboard with query picker, SQL viewer, and charts

