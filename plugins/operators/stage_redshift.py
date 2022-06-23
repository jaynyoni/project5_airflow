import datetime

from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class StageToRedshiftOperator(BaseOperator):
    ui_color = "#358140"

    @apply_defaults
    def __init__(
        self,
        redshift_conn_id="",
        aws_credentials_id="",
        table="",
        s3_bucket="",
        s3_folder="",
        region="",
        json_format="",
        execution_date="",
        *args,
        **kwargs
    ):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.aws_credentials_id = aws_credentials_id
        self.table = table
        self.s3_bucket = s3_bucket
        self.s3_folder = s3_folder
        self.region = region
        self.json_format = json_format
        self.execution_date = execution_date

    def execute(self, context):

        self.log.info("Starting COPY to Redshift.")

        aws_hook = AwsHook(self.aws_credentials_id)
        aws_credentials = aws_hook.get_credentials()
        redshift_hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        execution_date = self.execution_date.format(**context)

        self.log.info(execution_date)

        s3_path = "s3://{}/{}".format(self.s3_bucket, self.s3_folder)

        self.log.info(s3_path)

        self.log.info("Emptying table {}.".format(self.table))

        empty_table = ("""truncate {}""").format(self.table)

        redshift_hook.run(empty_table)

        self.log.info("Copying table {}.".format(self.table))

        staging_table_copy = (
            """
        copy {} from '{}'
        access_key_id '{}'
        secret_access_key '{}'
        region '{}'
        json '{}'
        timeformat as 'epochmillisecs'
        truncatecolumns
        blanksasnull
        emptyasnull;
        """
        ).format(
            self.table,
            s3_path,
            aws_credentials.access_key,
            aws_credentials.secret_key,
            self.region,
            self.json_format,
        )

        self.log.info(staging_table_copy)

        redshift_hook.run(staging_table_copy)

        self.log.info("COPY complete!")
