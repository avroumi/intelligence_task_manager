import mysql.connector
from contextlib import contextmanager


class DataBaseConnection: 
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = "1234"
        self.port = "3306"
        self.database = "Intelligence_db"

    def get_connection_for_database(self): 
        return mysql.connector.connect(
            host=self.host, 
            user= self.user,
            password= self.password,
            port= self.port
        )
    
    def get_connection(self): 
        return mysql.connector.connect(
            host=self.host, 
            user= self.user,
            password= self.password,
            port= self.port,
            database= self.database 
        )

    def create_datbase(self): 

        conn = self.get_connection_for_database() 
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS Intelligence_db")
        cursor.execute("USE Intelligence_db")

        cursor.close()
        conn.close()
    
    def create_tables(self):

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents(
        id INT PRIMARY KEY AUTO_INCREMENT , 
        name VARCHAR(50) NOT NULL , 
        specialty VARCHAR(100) NOT NULL , 
        is_active BOOLEAN DEFAULT TRUE , 
        completed_missions INT NOT NULL  DEFAULT 0  , 
        failed_missions INT NOT NULL DEFAULT 0 ,
        agent_rank ENUM("Junior, Senior, Commander" ) )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS missions(
        id INT PRIMARY  KEY AUTO_INCREMENT , 
        title VARCHAR(100) NOT NULL , 
        description TEXT NOT NULL , 
        location VARCHAR(100) NOT NULL , 
        difficulty INT NOT NULL , 
        importance INT NOT NULL , 
        status ENUM("NEW", "ASSIGNED", "IN_PROGRESS", "COMPLETED", "FAILED", "CANCELLED") DEFAULT "NEW", 
        risk_level VARCHAR(50) NOT NULL , 
        assigned_agent_id INT   
                       )
            """)
        
    @contextmanager
    def get_cursor(self, dictionnary= True):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=dictionnary, buffered=True)

        try : 
            yield cursor 
            conn.commit()
        except Exception: 
            conn.rollback()
            raise 
        finally: 
            cursor.close()
            conn.close() 


    def setup(self): 
        self.create_datbase()
        self.create_tables()


db = DataBaseConnection()
db.setup()
