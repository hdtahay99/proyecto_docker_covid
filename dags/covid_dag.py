import os
import pandas as pd
from datetime import datetime
from structlog import get_logger
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.contrib.hooks.fs_hook import FSHook
from airflow.hooks.mysql_hook import MySqlHook


logger = get_logger()

COLUMNS = {
    "Province/State" : "province_state", 
    "Country/Region" : "country_region", 
    "Lat"            : "lat", 
    "Long"           : "lon", 
    "Date"           : "date", 
    "Value"          : "value",
    "Status"         : "status",
    "Created_at"     : "created_at"
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


def data_preprocessing(df, file):
    """
    Convert date columns to rows with their values
    """
    
    columns = ['Province/State','Country/Region','Lat','Long']
    
    df['Province/State'].fillna('Unknown', inplace = True)
    df['Lat'].fillna(0.0000, inplace = True)
    df['Long'].fillna(0.0000, inplace = True)
    
    dates = df.drop(columns=columns)
    dates = dates.diff(axis=1)
    dates.fillna(0, inplace = True)
    
    df.drop(columns=df.columns.difference(columns), inplace = True)
    
    df_concat = pd.concat([df,dates], axis=1)
    
    df_concat = df_concat.melt(id_vars=columns, var_name="Date", value_name="Value")
    
    status = "Unkown"

    if("confirmed" in file):
        status = "Confirmed"
    elif("deaths" in file):
        status = "Deaths"
    elif("recovered" in file):
        status = "Recovered"
        
    df_concat["Status"] = status
    df_concat["Created_at"] = datetime.now()

    df_concat.rename(columns=COLUMNS, inplace=True)

    df_concat.date = pd.to_datetime(df_concat.date)

    return df_concat


def sensor_data(**kwargs):
    
    execution_date = kwargs["execution_date"]
    logger.info(execution_date)
    
    file_path = f"{FSHook('fs_covid').get_path()}/data/"
    connection = MySqlHook('mysql_default').get_sqlalchemy_engine()

    files = [file for file in os.listdir(file_path)]
    for file in files:
        df = pd.read_csv(file_path+file, encoding="ISO-8859-1")
        df = data_preprocessing(df, file)
        logger.info(df)

        status = ""

        if("confirmed" in file):
            status = "Confirmed"
        elif("deaths" in file):
            status = "Deaths"
        elif("recovered" in file):
            status = "Recovered"

        with connection.begin() as transaction:
            transaction.execute(f"DELETE FROM db_covid.covid_values WHERE db_covid.covid_values.status = '{status}'")
            df.to_sql('covid_values', con = transaction, schema='db_covid',  if_exists = 'append', index = False)

        logger.info(f'Records inserted {len(df.index)} --- {file}')
        os.remove(file_path+file)
        os.remove(file_path)



sensor = FileSensor(filepath = 'data/',
                    fs_conn_id = 'fs_covid',
                    task_id = 'check_for_file',
                    poke_interval = 5,
                    timeout = 60,
                    dag=dag)

operador = PythonOperator(task_id = 'process_file',
                          dag=dag,
                          python_callable=sensor_data,
                          provide_context=True)

sensor >> operador