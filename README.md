# Introduction

This project creates a high grade data pipeline that automatically loads new data for Sparkify a music streaming company
using Apache Airflow. 

### Prerequities 

1. Amazon Web Services account that has as Redshift Cluster, Amazon S3 buckets and with IAM roles and user privileges.
2. Apache Airflow

### What is Happening?

The Sparkify streaming app dumps json log files into S3 buckets. These source datasets tell us about user activity in 
the application and JSON metadata about the songs the users listen to. We use Amazon Redshift Copy function to extract 
the .json files from S3 to Redshift staging. Once the data is staged in Redshift we then transform it in Redshift to 
create facts and dimensions for reporting.

## ETL Process
### Setup
To get going, you will need to create two new connections within Airflow:

### Amazon S3
First, you will need to create an IAM Role that allows Redshift to access S3 for you. Once you have created the role, 
get the Access key ID and the Secret access key and add them to Airflow under Admin > Connections > Create.

>- Conn ID: aws_credentials
>- Login: your AWS profile Access key ID 
>- Password: Secret access key for this Access key ID

This is the connection that allows Airflow to access S3 and copy the .json files from the Sparkify S3 bucket, so 
unless you have configured this correctly, the ***sparkify_etl.py*** DAG will not be able to execute 
the StageToRedshiftOperator correctly and it will fail.

### Amazon Redshift
Next, you will need to add your Amazon Redshift connection details to a new Airflow connection. Note that for Airflow 
to access your Redshift cluster, you will need to Authorize access to the cluster.

>- Conn ID: redshift
>- Host: _your Amazon Redshift cluster's endpoint (usually something like: your_cluster_name.abcdefgh.us-west-2.redshift.amazonaws.com)
>- Schema: the name of the Redshift db
>- Login: your Redshift username
>- Password: your Redshift password
>- Port: the port you have opened to allow connections on (5439 by default)

Once your Redshift Cluster is ready open the Amazon Redshift Query Editor. Copy and paste the ***create_tables.sql*** code 
and run it to create the tables that will be needed. This is only needed once during set-up. 

## Run Sparkify ETL
Toggle on the ***sparkify_etl.py*** DAG via the Airflow UI. 
Before doing so, you may want to configure its start_date and end_date values in the default_args dict, as the DAG is 
scheduled to run once an hour.

Here are some other options that can be configured in this DAG.

>- In all the load_songplays_table and load_*_dimension_table tasks, the truncate_table attribute can be set to either True or False. 
> If set to True, the LoadFactOperator / LoadDimensionOperator will TRUNCATE the tables before running the new queries on them. 
   > This allows you to switch between append-only and insert-delete functionality for these tasks.

The tables are created with primary key index so duplicates will be handled automattically by redshift in the event it is
doing append only for existing records.

You can also play around with the default_args dict if you want to change run time, start and end time etc. The framework 
is very flexible and easy to make changes.
   
### Files
- dags/sparkify_etl.py - The main ETL tag that extracts the `.json` data from s3, copies it to Redshift and transforms it
- plugins/operators/stage_redshift.py - The StageToRedshiftOperator that we use to copy the `.json` data from s3 to Redshift
- plugins/operators/load_fact.py - The LoadFactOperator, used to generate the `songplays` fact table
- plugins/operators/load_dimension.py - The LoadDimensionOperator, used to generate the `songs`, `users`, `artists`, and `time` dimension tables
- plugins/operators/data_quality.py - The DataQualityOperator, currently used to check if any of the tables are empty after ETL. 
- plugins/helpers/sql_queries.py - Contains all the SQL queries used by all the other operators.
- plugins/helpers/create_tables.py - Contains all the SQL schemas for all the tables used in the ELT process.
