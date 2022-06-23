from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class LoadFactOperator(BaseOperator):
    ui_color = "#F98866"

    @apply_defaults
    def __init__(
        self,
        redshift_conn_id="",
        table="",
        truncate_table="",
        sql_query="",
        *args,
        **kwargs,
    ):
        super(LoadFactOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.table = table
        self.truncate_table = truncate_table
        self.sql_query = sql_query

    def execute(self, context):
        redshift_hook = PostgresHook(self.redshift_conn_id)

        if self.truncate_table == True:
            self.log.info("Truncating table {}." .format(self.table))
            redshift_hook.run(f"TRUNCATE TABLE {self.table}")
            self.log.info("Truncating table {} successful.".format(self.table))

        self.log.info("Loading fact table {} via query:".format(self.table))
        self.log.info(self.sql_query)
        redshift_hook.run(self.sql_query)
        self.log.info("Fact table {} loaded.".format(self.table))
