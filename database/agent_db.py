from database.db_connection import DataBaseConnection
from pydantic import BaseModel, Field
from typing import Literal 



class AgentDB:
    def __init__(self, db : DataBaseConnection):
        self.db = db 

    class CreateAgent(BaseModel): 
        name : str = Field(min_length=1 , max_length=50)
        specialty : str = Field(min_length=1 , max_length=100)
        is_active : bool | None = None 
        completed_missions : int | None = None 
        failed_missions : int | None = None 
        agent_rank : Literal["Junior", "Senior", "Commander"]

        

    def create_agent(self, data : dict) -> dict :
        
        columns = ", ".join(data.keys())
        placeholder = ", ".join(["%s"] * len(data))
        values = tuple(data.values())
        sql = f"INSERT INTO agents ({columns}) VALUES ({placeholder}) "


        with self.db.get_cursor() as cursor : 
            cursor.execute(sql , values)
            new_id = cursor.lastrowid

        return {"message": f"data {data} create succesfully",
                "agentId" : new_id}

    def get_all_agents(self) -> list[dict]: 
        with self.db.get_cursor() as cursor :
            cursor.execute("SELECT * FROM agents")
            return cursor.fetchall()
        
    def get_agent_by_id(self, agent_id) -> dict | None : 
        with self.db.get_cursor() as cursor :
            cursor.execute("SELECT * FROM agents WHERE id = %s LImit 1 ", (agent_id, ))
            return cursor.fetchone()
        
    def update_agent(self, agent_id , data : dict) -> dict :

         
        if data["id"] : 
            return {"message": "You can't change id"}
        
        set_close = ", ".join([f"{key} = %s " for key in data.keys()])
        values = list(data.values()) + [agent_id]
        sql = f"UPDATE agents SET {set_close} WHERE id = %s "

        with self.db.get_cursor() as cursor : 
            cursor.execute(sql, values)
            success = cursor.rowcount > 0 
            if success : 
                return {"message" : " Update succesfully"}
            
        return {"message" : "Update failed"}
    
    def deactivate_agent(self, agent_id): 
        with self.db.get_cursor() as cursor : 
            agent_exist = self.get_agent_by_id(agent_id) 
            if agent_exist:
                cursor.execute("UPDATE agents SET is_active = false WHERE id = %s ", (agent_id, ))
                return {"message": f"Deactivate agent {agent_id} successfuly"}
            return {"message" : "Failed to deactivate agent"}
        
    def increment_completed(self, agent_id) -> dict :
        with self.db.get_cursor() as cursor :
            agent_exist = self.get_agent_by_id(agent_id) 
            if agent_exist:
                cursor.execute("UPDATE agents SET completed_missions = completed_missions + 1 " \
                "WHERE id = %s", (agent_id, ))
                return {"message": "Increment succesfully"}
            return {"message": "Failed to increment"}
        
    def increment_failed(self, agent_id) -> dict :
        with self.db.get_cursor() as cursor :
            agent_exist = self.get_agent_by_id(agent_id) 
            if agent_exist:
                cursor.execute("UPDATE agents SET failed_missions = failed_missions + 1 " \
                "WHERE id = %s", (agent_id, ))
                return {"message": "Increment succesfully"}
            return {"message": "Failed to increment agent"}
        
    def get_agent_performance(self , agent_id): 
        agent = self.get_agent_by_id(agent_id)
        if agent: 
            failed = agent["failed_missions"]
            completed = agent["completed_missions"]
            total = int(failed) + int(completed)
            success_rate = round(completed / total * 100, 2) 
            return {"completed": completed,
                    "failed" : failed,
                    "total" : total, 
                    "success_rate" : success_rate
                    }
    
    def count_active_agents(self) -> dict :
        with self.db.get_cursor() as cursor :
            cursor.execute("SELECT  COUNT(is_active) FROM agents WHERE is_active= TRUE")
            active_agents = cursor.fetchone()
            return {"active_agent" : active_agents["COUNT(is_active)"]}

        
    









