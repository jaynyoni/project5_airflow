from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class DataQualityOperator(BaseOperator):
    ui_color = "#89DA59"

    @apply_defaults
    def __init__(
        self, redshift_conn_id="", aws_credentials_id="", tables="", *args, **kwargs
    ):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.aws_credentials_id = (aws_credentials_id,)
        self.tables = tables

    def execute(self, context):

        redshift_hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        for table in self.tables:

            query = "SELECT COUNT(*) FROM {}".format(table)

            self.log.info(query)

            connection = redshift_hook.get_conn()

            cursor = connection.cursor()

            cursor.execute(query)

            records = cursor.fetchall()

            self.log.info(records[0][0])

            if len(records) < 1 or len(records[0]) < 1 or records[0][0] < 1:

                error_message = "Data quality check failed on table {}.".format(table)

                self.log.error(error_message)

                raise ValueError(error_message)

            else:

                self.log.info(
                    f"Data quality on table {table} check passed with {records[0][0]} records"
                )
