import os
import pandas as pd 
import json

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from pandas import DataFrame
from logging import Logger

logger = Logger(name="DB_LOGGER", level=4)

class DBManager:
    """
    This class is responsible for managing the storage of user and debates associated with their respective pages. 
    The path to the database can be specified by setting the "DATABASE_URI" environment variable.
    """
    
    def __init__(self) -> None:
        """
        Initializes the DBManager class. Retrieves the database path from the environment variable `DATABASE_URI` 
        and strips any leading/trailing whitespace. Logs the received database path using the logger.
        """
        # Get the database path from the environment variable
        self.db_path = os.environ["DATABASE_URI"].strip()
        logger.info(f'The database path receieved is {self.db_path}')
        
        # SQL queries:
        self.UPDATE_TABLE = """UPDATE {table}  SET {column}='{value}' where page_name='{page_name}';"""
        self.INSERT_INTO_TABLE = """INSERT INTO {table}{col_names} VALUES{values}"""
        self.GET_PAGE_NAME = """SELECT page_name FROM pages where page_name='{page_name}'"""
        self.GET_MESSAGES = """SELECT messages FROM pages where page_name='{page_name}'"""
        self.GET_TOPIC_PAGE = """SELECT page_topic FROM pages where page_name='{page_name}'"""
        self.GET_ALL_PAGE_NAMES = """SELECT page_name from pages"""
        self.DELETE_PAGE = """DELETE FROM pages WHERE page_name='{page_name}'"""
        self.GET_EXPERT_INS = """SELECT expert_instructions FROM pages where page_name='{page_name}'"""
        self.CREATE_TABLE_PAGES= """CREATE TABLE IF NOT EXISTS pages(page_id VARCHAR(100) PRIMARY KEY,
                                                                    page_name VARCHAR(100), 
                                                                    time VARCHAR(100),
                                                                    messages TEXT,
                                                                    page_topic VARCHAR(100),
                                                                    page_image VARCHAR(100),
                                                                    expert_instructions TEXT);"""
        
    def connect_db(self)->None:
        """
        Establishes a connection to the database.
    
        This method creates an SQLAlchemy engine using the provided database path (`db_path`).
        It then initializes a session to interact with the database.
        All database commands will be executed using this session variable.

        Raises:
            Exception: If unable to connect to the database, an error is logged and an exception is raised.
        """
        try:
            # Create a SQLAlchemy engine to connect to the database
            self.engine = create_engine(self.db_path)
            
            # Create a session to interact with the database
            self.session = Session(self.engine)
        except Exception as e:
            logger.error(f'Unable to connect to Database')
            raise Exception(e)
        
        
    def close_connection(self)->None:
        """
        Closes the connection to the database.
        
        This method ensures that the connection to the database is properly closed.
        It is important to close any loose connections to prevent potential database lock situations,
        especially as the number of users increases in lightweight SQL implementations like SQLite.
        """
        self.session.close()
        self.engine.dispose()
        
        
    def create_table(self, table_def:str, table_name:str='pages')->None:
        """
        Creates a new table in the database.

        Parameters
            table_def (str):
                The schema string used to create the table, containing information about the table name and columns.
            table_name (str, optional):
                The name of the table, used for logging purposes. Defaults to 'pages'.

        Raises
            RuntimeError: If there is an issue with table creation, this error is raised.
        """
        self.connect_db()
        
        try:         
            self.session.execute(text(table_def))
            self.session.commit()
            self.close_connection()
            logger.info(f'The table {table_name} is already present or it is successfully created!')
            
        except RuntimeError as e:
            logger.error(f'Cannot create table')
            self.close_connection()
            raise Exception(e)
        
        
    def get_page_name(self, page_name:str):
        """
        Retrieves the page name from the database.

        Parameters
            page_name (str): The name of the page to retrieve.

        Returns
            res (DataFrame): The result containing the page name.

        Raises
            Exception: If an error occurs during retrieval, an exception is raised.
        """

        try:            
            # Get run id from the runs table  
            run_payload = {}
            run_payload["page_name"] = page_name
            res = self._get_df(self.GET_PAGE_NAME.format(**run_payload))
            return res
        except Exception as e:
            raise Exception(e)
        
    def get_all_page_names(self):
        """
        Retrieves all page names from the database.

        Returns
            res (DataFrame): The result containing all page names.

        """
        try:            
            res = self._get_df(self.GET_ALL_PAGE_NAMES)
            return res
        except Exception as e:
            return None
        
    def get_debates(self, page_name:str, is_json=True):
        """
        Retrieves the debates from the database.

        Parameters
            page_name (str): 
                The name of the page to retrieve debates for.
            is_json (bool):
                A flag to indicate whether the output should be in JSON format or not.

        Returns
            res (DataFrame):
                The result containing the debates.
        """
        try:            
            # Get run id from the runs table  
            run_payload = {}
            run_payload["page_name"] = page_name
            res = self._get_df(self.GET_MESSAGES.format(**run_payload), json_format=is_json)
            return res
        except Exception as e:
            print(e)
            return None
        
        
    def insert_into_pages(self, page_name:str, values:dict)->None:
        """
        Inserts a new page into the database.

        Parameters
            page_name (str):
                The name of the page to insert.
            values (dict):
                The values to insert into the page.

        Returns
            None

        """
        payload = {}
        payload["page_name"] = page_name
        payload["page_id"] = values["page_id"]
        payload["time"] =  values["time"]
        payload["messages"] = values["messages"]
        payload["page_topic"] = values["page_topic"]
        payload["page_image"] = values["page_image"]
        payload["expert_instructions"] = values["expert_instructions"]
        
        formatter = {
            "table": "pages",
            "col_names": tuple(payload.keys()),
            "values": tuple(payload.values()),
        }
        
        
        sql_query = self.INSERT_INTO_TABLE.format(**formatter)
    
        
        try:
            self.connect_db()
            self.create_table(self.CREATE_TABLE_PAGES)
            self.session.commit()
            self.session.execute(text(sql_query))
            self.session.commit()
            self.close_connection()
            
        except Exception as e:
            logger.error(f"Cannot add data to mlflow database because {e}")
            self.close_connection()
            
    def _get_df(self, statement, json_format=False)->DataFrame:
        """
        Executes the provided SQL statement and returns the result as a DataFrame.

        Parameters
            statement (str):
                The SQL statement to execute.
            json_format (bool, optional):
                A flag to indicate whether the output should be in JSON format or not, by default False.

        Returns
            DataFrame
                The result of the SQL statement as a DataFrame.
        """
        self.connect_db()
        
        data = self.session.execute(text(statement))
        cols = list(data.keys())
        res = self.session.execute(text(statement))
        if json_format:
            return {"output":json.loads(res.fetchone()[0])} 
        df = pd.DataFrame(res, columns=cols)
        self.close_connection()
        return df
    
    def update_table(self, table:str, col_name:str, value:any, page_name:str)->None:
        
        """
        Updates a table in the database.

        Parameters
            table (str):
                The name of the table to update.
            col_name (str):
                The name of the column to update.
            value (any):
                The value to update the column with.
            page_name (str):
                The name of the page to update.
        
        Returns
            None
        
        """
        
        self.connect_db()
        
        payload = {}
        payload["table"] = table
        payload["column"] = col_name
        
        if col_name in ["messages"]:
            value = json.dumps(value, ensure_ascii=False).replace("'", "''")
        if col_name in ["expert_instructions"]:
            value = json.dumps(value, ensure_ascii=False)

        payload["value"] = value
        payload["page_name"] = page_name
        
        sql_query = self.UPDATE_TABLE
        
        try:
            self.session.execute(text(sql_query.format(**payload)))
            self.session.commit()
            logger.info(f"successfully updated table {table}, {sql_query}")
            self.close_connection()
        except Exception as e:
            logger.error(f"Unable to update table {table} because of the following error, {e}")
            self.close_connection()

    def delete_page(self, page_name:str)->None:
        """
        Deletes a page from the database.

        Parameters
            page_name (str):
                The name of the page to delete.

        Returns
            None
        """
        self.connect_db()
        try:
            # Execute the SQL query to delete the page
            self.session.execute(text(self.DELETE_PAGE.format(page_name=page_name)))
            self.session.commit()
            logger.info(f"Page '{page_name}' deleted successfully.")
        except Exception as e:
            logger.error(f"Failed to delete page '{page_name}' due to: {e}")
        finally:
            self.close_connection()

    def get_topic_page_value(self, page_name:str):
        """
        Retrieves the topic page value from the database.

        Parameters
            page_name (str):
                The name of the page to retrieve the topic page value for.
        
        Returns
            res (DataFrame):
                The result containing the topic page value.
        """
        try:
            run_payload = {}
            run_payload["page_name"] = page_name
            res = self._get_df(self.GET_TOPIC_PAGE.format(**run_payload))
            return res
        except Exception as e:
            raise Exception(e)
        
    def get_expert_instructions(self, page_name:str, is_json=True):
        """
        Retrieves the expert instructions from the database.

        Parameters
            page_name (str):
                The name of the page to retrieve expert instructions for.
            is_json (bool):
                A flag to indicate whether the output should be in JSON format or not.
        
        Returns
            res (DataFrame):
                The result containing the expert instructions.
        """
        try:
            run_payload = {}
            run_payload["page_name"] = page_name
            res = self._get_df(self.GET_EXPERT_INS.format(**run_payload), json_format=is_json)
            return res
        except Exception as e:
            print(e)
            return None