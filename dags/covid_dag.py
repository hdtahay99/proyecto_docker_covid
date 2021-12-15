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
    "Confirmed"      : "confirmed",
    "Deaths"         : "deaths",
    "Recovered"      : "recovered",
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


def sensor_data(**kwargs):
    
    execution_date = kwargs["execution_date"]
    logger.info(execution_date)
    
    file_path = f"{FSHook('fs_covid').get_path()}/data/"
    connection = MySqlHook('mysql_default').get_sqlalchemy_engine()

    files = [file for file in os.listdir(file_path)]
    
    df1 = pd.read_csv(file_path+files[0], encoding="ISO-8859-1")
    df2 = pd.read_csv(file_path+files[1], encoding="ISO-8859-1")
    df3 = pd.read_csv(file_path+files[2], encoding="ISO-8859-1")

    columns = ['Province/State','Country/Region','Lat','Long']

    ## Melt de los 3 datasets
    confirmed = df1.melt(id_vars=columns, var_name="Date", value_name="Confirmed")
    deaths = df2.melt(id_vars=columns, var_name="Date", value_name="Deaths")
    recovered = df3.melt(id_vars=columns, var_name="Date", value_name="Recovered")

    ## Union en un solo dataset
    full_data = confirmed.merge(right=deaths, how='left', on=['Province/State', 'Country/Region', 'Date', 'Lat', 'Long'])
    full_data = full_data.merge(right=recovered, how='left', on=['Province/State', 'Country/Region', 'Date', 'Lat', 'Long'])
    
    ## DateTime
    full_data['Date'] = pd.to_datetime(full_data['Date'])

    ## NaN values
    full_data['Recovered'].fillna(0, inplace = True)
    full_data['Lat'].fillna(0.0000, inplace = True)
    full_data['Long'].fillna(0.0000, inplace = True)
    full_data['Province/State'].fillna('Unknown', inplace = True)
    
    ## Reversion de sumarizado
    group_data = full_data.groupby(['Province/State', 'Country/Region', 'Lat', 'Long', 'Date'])['Confirmed', 'Deaths', 'Recovered'].sum().reset_index()
    temp = group_data.groupby(['Province/State', 'Country/Region', 'Lat', 'Long', 'Date']) ['Confirmed', 'Deaths', 'Recovered'] 
    temp =temp.sum().diff().reset_index()
    
    ## NaN values
    temp.fillna(0, inplace = True)
    
    ## Finalizando
    temp["Created_at"] = datetime.now()
    temp.rename(columns=COLUMNS, inplace=True)
    temp[['confirmed', 'deaths', 'recovered']] = temp[['confirmed', 'deaths', 'recovered']].applymap(lambda x: 0 if x < 0 else x)

    with connection.begin() as transaction:
        transaction.execute(f"TRUNCATE TABLE db_covid.covid_values")
        temp.to_sql('covid_values', con = transaction, schema='db_covid',  if_exists = 'append', index = False)

    logger.info(f'Records inserted {len(temp.index)}')

    os.remove(file_path+files[0])
    os.remove(file_path+files[1])
    os.remove(file_path+files[2])



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