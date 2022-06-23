from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class LoadDimensionOperator(BaseOperator):
    ui_color = "#80BD9E"

    @apply_defaults
    def __init__(
        self,
        redshift_conn_id="",
        sql_query="",
        table="",
        truncate_table="",
        *args,
        **kwargs,
    ):
        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.sql_query = sql_query
        self.table = table
        self.truncate_table = truncate_table

    def execute(self, context):
        redshift_hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        if self.truncate_table == True:
            self.log.info("Truncating table.")
            redshift_hook.run(f"TRUNCATE TABLE {self.table}")
            self.log.info("Truncating table successful.")

        self.log.info("Loading dimension table {} via query:".format(self.table))
        self.log.info(self.sql_query)
        redshift_hook.run(self.sql_query)
        self.log.info("Dimension table {} loaded.".format(self.table))
