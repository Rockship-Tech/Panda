# How to run 

## Airflow

``` bash install airflow
pip install 'apache-airflow[postgres,google,amazon,snowflake,databricks,dbt]==2.6.2' \
 --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.6.2/constraints-3.8.txt"
```
```
pip install -r requrements.txt
```

``` bash
airflow db init
```

```
docker start postgresDB
```

Connect to postgres in docker
``` bash
psql -h localhost -p 5432 -U postgres -d postgres
```

Config airflow to use postgres, username postgres:
Default airflow home is ~/airflow, change in airflow.cfg
```
sed -i 's#sqlite:////home/ubuntu/airflow/airflow.db#postgresql+psycopg2://postgres:postgres@localhost/airflow#g' airflow.cfg
```

change from sequential to local executor
```
sed -i 's#SequentialExecutor#LocalExecutor#g' airflow.cfg
```

Create airflow username:
```
airflow users create -u airflow -f airflow -l airflow -r Admin -e airflow@gmail.com
```

And input password\
Run airflow:

```
airflow scheduler
```
To run webserver
```
airflow webserver
```


---
## API Server:

in panda
```
source venv/bin/activate
```

```
export FLASK_APP=server/main.py
```

```
flask run
```


