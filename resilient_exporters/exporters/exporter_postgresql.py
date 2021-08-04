import urllib
import logging
from typing import Text, Union
from ..exporters import Exporter, ExportResult
from ..utils import _validate_data_for_sql_table, \
                    _transform_data_for_sql_query, \
                    _describe_postgres_column
from ..exceptions import MissingConfigError, \
                                           InvalidConfigError, \
                                           MissingModuleError, \
                                           ExportError

logger = logging.getLogger(__name__)

try:
    import psycopg2
except ModuleNotFoundError:
    logger.error("""Module psycopg2 not available. Install using:
                    pip install resilient-exporters[postgres]""")
    raise

class PostgreSQLExporter(Exporter):
    """Exporter for PostgreSQL.

    Args:
        target_host (str):
        target_port (int):
        username (str):
        password (str):
        database (str):
        default_table (str):
        create_table_if_inexistent (bool): Default to False
        **kwargs : the keyword arguments to pass down to parent's class Exporter
    Raises:
        InvalidConfigError: if it cannot retrieve the server information, which
            is likely due an invalid configuration of the target.

    .. admonition:: Example

        .. code-block:: python

            from resilient_exporters.exporters import PostgreSQLExporter

            exporter = PostgreSQLExporter(target_host="myserver.domain.net",
                                          username="username",
                                          password="my-password",
                                          database="profiles",
                                          default_table="scientists")

            data = {"name": "Richard Feynman",
                    "age": 69}
            exporter.send(data)
    """
    def __init__(self,
                 conn_string: Text = None,
                 target_host: Text = None,
                 database: Text = None,
                 target_port: int = 5432,
                 username: Text = None,
                 password: Text = None,
                 default_table: Text = None,
                 **kwargs):
        assert conn_string or (target_host and target_port), "Either a connection string or target host is needed."
        super(PostgreSQLExporter, self).__init__(**kwargs)

        if conn_string:
            self.__conn = psycopg2.connect(conn_string)
        else:
            self.__conn = psycopg2.connect(host=target_host,
                                           port=port,
                                           user=username,
                                           password=password,
                                           dbname=database)
        self.__cur = self.__conn.cursor()
        self.__default_table = default_table

        # List tables in the database
        try:
            #self.__cur.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES;")
            self.__cur.execute("SELECT * FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' \
                                AND schemaname != 'information_schema';")
            self.__all_tables = {}
            for row in self.__cur.fetchall():
                self.__all_tables[row[1]] = {}
        except Exception as e:
            logging.error(e)
            raise InvalidConfigError(self, "Cannot retrieve database info. Is \
                                            the configuration valid? Does the user have read rights?")
        
        # Get information on columns for each table
        for table_name in self.__all_tables.keys():
            self.__cur.execute(f"SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, ORDINAL_POSITION, IS_NULLABLE, \
                                 CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, DATETIME_PRECISION \
                                 FROM information_schema.columns WHERE table_name='{table_name}';")
            for col in self.__cur.fetchall():
                print(col)
                self.__all_tables[table_name][col[1]] = _describe_postgres_column(col)

    def send(self,
             data: Union[dict, tuple],
             table: Text = None) -> ExportResult:
        """Inserts data into a table. Reuses default database and
        tables names, if provided at initialisation.

        Args:
            data (Union[dict, tuple]): a dict or tuple representing the document to insert into the
                collection. If a dict, the keys must be the column names. If a tuple, there must be
                as many elements as there are columns in the table.
            table (str): name of the target table. If `None`, will use
                the default value set at initialisation. Default is `None`.

        Returns:
            ExportResult: the result in the form (ObjectId, True) if successful,
                (None, False) otherwise.

        Raises:
            MissingConfigError: if it cannot find a database and/or collection
                in the arguments and default values.
        """
        if table is None:
            if self.__default_table is None:
                    raise MissingConfigError(self, "No table given by argument nor default table configured.")
            table = self.__default_table

        if table in self.__all_tables.keys():
            # Validates the data, raises errors in case something is wrong
            _validate_data_for_sql_table(data, self.__all_tables[table])
            columns, values = _transform_data_for_sql_query(data)

            if isinstance(data, dict):
                print(f"INSERT INTO {table}({columns}) VALUES({values});")
                self.__cur.execute(f"INSERT INTO {table}({columns}) VALUES({values});", table)
            else:
                self.__cur.execute(f"INSERT INTO {table} VALUES({values});", table)
            success = bool(self.__cur.rowcount)
            self.__conn.commit()
            return ExportResult(None, success)
        else:
            raise InvalidConfigError(self, f"""Table {table} does not exist in
                                                database. Provide the name of 
                                                an existing table""")
