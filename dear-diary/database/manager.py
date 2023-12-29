import os 
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import pandas as pd 
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

        self.ADD_COLUMN = """ALTER TABLE {table} ADD COLUMN  {col_name} {col_type} DEFAULT {default}; """
        
        self.UPDATE_TABLE = """UPDATE {table} SET {col_name}={value} where page_name='{page_name}';"""
        
        self.INSERT_INTO_TABLE = """INSERT INTO {table}{cols} VALUES{values} """
        
        self.GET_MESSAGES = """SELECT messages FROM pages where page_name='{page_name}'"""
        
        
        
        self.CREATE_TABLE_PAGES= """
                    CREATE TABLE IF NOT EXISTS pages(
                        page_id VARCHAR(100) PRIMARY KEY,
                        page_name VARCHAR(100),
                        time VARCHAR(100),
                        messages VARCHAR(10000000000)
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
                   
        table_name : str, default=`runs_meta`
                     The name of the table for logging purpose only.
        
        Returns
        -------
        None
        
        Raises
        ------
        
        RuntimeError
            There is some problem with the table creation and the error is
        
        Examples
        --------
        
        >>> table_schema = 'CREATE TABLE IF NOT EXISTS runs_meta (
                        run_uuid VARCHAR(100) PRIMARY KEY,
                        running INT,
                        nested INT,
                        upstream VARCHAR(100)
                    );'
        >>> table_name = runs_meta
        >>> exp_manager = ExperimentMananger()
        >>> exp_manager.create_table(table_schema=table_schema,
        >>>                          table_name=table_name)
        'The table runs_meta is already present or it is successfully created!' 
        
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
        
        
    
 
        
        
        
    def create_column(self,table:str, col_name:str, col_type:str, default:any="NULL")->None:
        
        """
        This method adds a new column to an existing table. It makes use of the SQL's ``ALTER`` keyword to add another column to the table. By default it is designed to make columns nullable by providing 
        a default value. If the column is designed to have non null entries, then please mention it at the time of creating the tables.
        
        Paramaters
        ----------
        
        table : str
                Name of the table, in which the new column is to be added 
                   
        col_name : str
                   Name of the column to be added to the table 
                  
        col_type : str 
                   A valid type for the column. Choose according to the database.
                   
        default : any, optional, defult='NULL'
                  the default value for the column.
                   
        
        
        Returns
        -------
        None
        
        """
        
        self.connect_db()
        
        payload = {
            "table":table,
            "col_name":col_name,
            "col_type":col_type,
            "default": default
        }
        
        sql_query = self.ADD_COLUMN.format(**payload)
        logger.info(sql_query)
        self.session.execute(text(sql_query))
        self.session.commit()
        
        self.close_connection()
        
        
        
    def get_messages(self, page_name:str):
        """
        
        
        Paramaters
        ----------
        
        experiment_id : int
                        The id of the experiment, returned by mlflow.set_experiment method.
                   
        run_name : str
                   The name of the mlflow run whose run id is asked.
        
        Returns
        -------
        run_id : str or None 
        
        
        Examples
        --------
        
        >>> experiment_id = mlflow.set_experiment('some_experiment')
        >>> run_name = 'some_run'
        >>> exp_manager = ExperimentMananger()
        >>> print(exp_manager.get_run_id(experiment_id=experiment_id,
        >>>                              run_name=run_name))
        'fnjegnjdnjn1343njwnj'
        
        
        
        
        """
        try:            
            #Get run id from the runs table  
            run_payload = {}
            run_payload["page_name"] = page_name
            res = self._get_df(self.GET_MESSAGES.format(**run_payload))
            return res
        except Exception as e:
            return None
        
        
    def insert_into_pages(self, page_name:str, values:dict)->None:
        
        """
        This method adds data to runs_meta table and ensures that the table is created before hand. It is primarly used to to add rows to the runs_meta table when a run is created either a nested run or 
        normal mlflow run.
        
        Paramaters
        ----------
        
        run_id : str
                 It is the run id of the mlflow run against which the data is going to be inserted in the table.
                   
        values : list
                 It is a list of values for the columns ['running', 'nested', 'upstream'], strictly in that order. `running` is a integer varaible, whose values are 0 if the run has ended and
                 1 if the run is still running. Similary, if the run is a mlflow nested run, then `nested` is set to 1 else 0. The `upstream` is the run_id of the run that finished just before the 
                 current run. This preserves the information of the previous process such that a user can refer to a dag with this information.
                
        
        Returns
        -------
        None
        
        Examples
        --------
        
        >>> run_id = 'afne29u82udsskndks'
        >>> running = 1
        >>> nested = 0
        >>> upstream = 'fhirgnirg8990efhg'
        >>> values = [running, nested, upstream]
        >>> exp_manager = ExperimentMananger()
        >>> exp_manager.insert_into_runs_meta(run_id=run_id,
        >>>                                   values=values) 
        
        """
        
        payload = {}
        payload["page_name"] = page_name
        payload["page_id"] = values["page_id"]
        payload["time"] =  values["time"]
        payload["messages"] = values["messages"]
        
    
        
        formatter = {
            "cols": tuple(payload.keys()),
            "values": tuple(payload.values()),
            "table": "pages"
        }
        
        
        sql_query = self.INSERT_INTO_TABLE.format(**formatter)
        
        try:
            self.connect_db()
            
            self.create_table(self.CREATE_TABLE_RUNS_META)
            
            self.session.commit()
            
            self.session.execute(text(sql_query))
            
            self.session.commit()
            
            self.close_connection()
            
        except Exception as e:
            logger.error(f"Cannot add data to mlflow database because {e}")
            self.close_connection()
            
    def _get_df(self, statement)->DataFrame:
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
        df = pd.DataFrame(self.session.execute(text(statement)), columns=cols)
        self.close_connection()
        return df
    
    def get_latest_run(self, experiment_id:int):
        
        """
        This method fetches the latest run from the mlflow database using the runs and the runs_meta table. A latest run is a run which is not a nested run and has a status ``FINISHED``
        in the ``status`` column of the runs table.
        
        Paramaters
        ----------
        
        experiment_id : int
                        It is i of the experiment whose latest is to fetched. 
                   
                
        
        Returns
        -------
        data : dict or None
        
        Examples
        --------
        
        >>> experiment_id = mlflow.set_experiment('some_experiment')
        >>> exp_manager = ExperimentManager()
        >>> exp_manager.get_latest_run(experiment_id=experiment_id) 
        
        """
        
        try:
            df = self._get_df(self.GET_LATEST_RUN.format(**{"id":experiment_id}))
            data = df.iloc[0].to_dict()
            return data
        except Exception as e:
            logger.error(e)
            return None
        
    
    def get_experiment_id(self, experiment_name:str)->DataFrame:
        
        """
        This method fetches the experiment_id from a the database corresponding to an experiment_name. This information is fetched from experiments table present in the mlflow database.
        
        Paramaters
        ----------
        
        experiment_name : str
                          It is the name of the experiment.
                          
                   
                
        
        Returns
        -------
        df : DataFrame
        
        Examples
        --------
        
        >>> experiment_name = "some_experiment"
        >>> exp_manager = ExperimentManager()
        >>> exp_manager.get_experiment_id(experiment_name=experiment_name) 
        
        """
        
        
        payload = {}
        payload["name"] = f'Experiment: {experiment_name}'
        df = self._get_df(self.GET_EXP_ID_FROM_NAME.format(**payload))
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
        
        Examples
        --------
        
        >>> table = "runs_meta"
        >>> col_name = "nested"
        >>> value = 1 
        >>> run_id = 'fjdsnfjsdnfjb9993jfnj'
        >>> exp_manager = ExperimentManager()
        >>> exp_manager.update_table(table=table,
        >>>                          col_name=col_name, 
        >>>                          value=value, 
        >>>                          run_id=run_id)
        
        """
        
        self.connect_db()
        
        payload = {}
        payload["table"] = table
        payload["col_name"] = col_name
        payload["value"] = value
        payload["page_name"] = page_name
        
        sql_query = self.UPDATE_TABLE.format(**payload)
        
        try:
            self.session.execute(text(sql_query))
            self.session.commit()
            logger.info(f"successfully updated table {table}, {sql_query}")
            self.close_connection()
            
        except Exception as e:
            logger.error(f"Unable to update table {table} because of the following error, {e}")
            self.close_connection()
        
        
    
    
            
    
  
        
        
        
        
    