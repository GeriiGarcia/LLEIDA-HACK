from qgis.core import QgsProject, QgsFeatureRequest, QgsMapLayer, QgsWkbTypes, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPoint, QgsField
from PyQt5.QtCore import QVariant 
import psycopg2
import math

import psycopg2
import json

# PostgreSQL connection settings
db_params = {
    "host": "localhost",
    "port": "5432",
    "dbname": "BD",
    "user": "user",
    "password": "password"
}

# Function to connect to PostgreSQL
def connect_to_db(params):
    conn = psycopg2.connect(**params)
    return conn

# Function to get the shortest path using pgrouting
def create_table_and_run_dijkstra(conn, start_id, end_id):
   return "Hola"

# Example usage: Find the shortest path between node 1 and node 10

print("Iniciant programa")
conn = connect_to_db(db_params)
print("connected to DB")
create_table_and_run_dijkstra(conn)
conn.close()
print("end of program")


