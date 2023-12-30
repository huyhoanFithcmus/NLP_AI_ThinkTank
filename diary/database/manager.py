import os 
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import pandas as pd 
import json
from pandas import DataFrame
from logging import Logger
logger = Logger(name="DB_LOGGER",
                level=4)


class DBManager:
    """
    It is responsible for managing saving the chats of the user and AI with respect to their pages.
    
    You can provide the path to the database by setting the `DATABASE_URI` in the environment variabes.
    """
    
    def __init__(self) -> None:
        
        self.db_path = os.environ["DATABASE_URI"].strip()
        
        logger.info(f'The database path receieved is {self.db_path}')
        
        self.UPDATE_TABLE = """UPDATE {table}  SET {column}='{value}' where page_name='{page_name}';"""
        
        self.INSERT_INTO_TABLE = """INSERT INTO {table}{col_names} VALUES{values}"""
        
        self.GET_PAGE_NAME = """SELECT page_name FROM pages where page_name='{page_name}'"""
        
        self.GET_MESSAGES = """SELECT messages FROM pages where page_name='{page_name}'"""
        
        self.GET_ALL_PAGE_NAMES = """SELECT page_name from pages"""
        
        
        
        self.CREATE_TABLE_PAGES= """
                    CREATE TABLE IF NOT EXISTS pages(
                        page_id VARCHAR(100) PRIMARY KEY,
                        page_name VARCHAR(100),
                        time VARCHAR(100),
                        messages TEXT
                    );
                    """

        
    def connect_db(self)->None:
        """
        This method is responsible for securing a connection to the databse. It updates two class variables; engine and session  
        which are essential to connect to the database using SQLAlchemy. All the commands will be executed using the session variable.
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
        """The method make sures that the connection from the database is closed. It is essential to close any loose connection such that 
        the user do not run into database lock situation as the users increase in some light weight sql implementations like ``sqlite``.
        """
        self.session.close()
        self.engine.dispose()
        
        
    def create_table(self, table_def:str, table_name:str='pages')->None:
        """
        This method creates a new table in the mlflow databse. Always remember to add the ``IF NOT EXISTS`` clause while creating tables. 
        
        Paramaters
        ----------
        
        table_def : str
                    It is the schema string used to create the table; it has information of the name of the table and as well as the columns.
                   
        table_name : str, default=`pages`
                     The name of the table for logging purpose only.
        
        Returns
        -------
        None
        
        Raises
        ------
        
        RuntimeError
            There is some problem with the table creation and the error is 
        
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
        try:            
            #Get run id from the runs table  
            run_payload = {}
            run_payload["page_name"] = page_name
            res = self._get_df(self.GET_PAGE_NAME.format(**run_payload))
            return res
        except Exception as e:
            raise Exception(e)
        
    def get_all_page_names(self):
        try:            
            res = self._get_df(self.GET_ALL_PAGE_NAMES)
            return res
        except Exception as e:
            return None
        
        
        
    def get_messages(self, page_name:str, is_json=True):
    
        try:            
            #Get run id from the runs table  
            run_payload = {}
            run_payload["page_name"] = page_name
            res = self._get_df(self.GET_MESSAGES.format(**run_payload), json_format=is_json)
            return res
        except Exception as e:
            print(e)
            return None
        
        
    def insert_into_pages(self, page_name:str, values:dict)->None:
        
        payload = {}
        payload["page_name"] = page_name
        payload["page_id"] = values["page_id"]
        payload["time"] =  values["time"]
        payload["messages"] = values["messages"]
        
    
        
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
        This method returns a pandas DataFrame of the result of the statment and it is a private method of the class.
        
        Paramaters
        ----------
        
        statement : str
                    The sql query to be executed against the database
                   
                
        
        Returns
        -------
        df : DataFrame
        
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
        This method updates a column of a table. It uses ``UPDATE`` keyword to update the values of a colum on the basis of the ``run_id``.
        
        Paramaters
        ----------
        
        table : str
                Name of the table, whose  column is going to be altrerd.
        
        col_name : str
                   Name of the column that is to be updated.
                   
        value : any
                The value for that column.
               
        run_id : str
                 The run_id corresponding to which the update is to be made in the table.
                          
                   
                
        
        Returns
        -------
        None
        
        """
        
        self.connect_db()
        
        payload = {}
        payload["table"] = table
        payload["column"] = col_name
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
        
        
    
    
            
    
  
        
        
        
        
    