import os
import pandas as pd
from airflow import DAG


logger = get_logger()

COLUMNS = {
    "Province/State" : "province_state", 
    "Country/Region" : "country_region", 
    "Lat"            : "lat", 
    "Long"           : "long", 
    "Date"           : "date", 
    "Value"          : "value"
}


dag = DAG('covid_dag', description='Covid 19 data insert and preprocess flow',
          default_args={
              'owner': 'tomas.ramon.edi.heansell',
              'depends_on_past': False,
              'max_active_runs': 1,
              'start_date': days_ago(1)
          },
          schedule_interval='0 1 * * *',
          catchup=False)
