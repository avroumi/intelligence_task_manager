from database.db_connection import DataBaseConnection
from database.agent_db import AgentDB




class MissionDB : 
    def __init__(self, db : DataBaseConnection, agent_db : AgentDB):
        self.db = db 
        self.agent_db = agent_db

    def create_mission_(self, data : dict) -> dict :

        risk = int(data["difficulty"]) * 2 + int(data["importance"])
        print(risk)
        
        if risk > 0 and risk <= 9 : 
            data["risk_level"] = "LOW"
        elif risk >= 10 and  risk <= 17:
            data["risk_level"] = "MEDIUM"
        elif risk >= 18 and  risk <= 24:
            data["risk_level"] = "HIGH"
        else: 
            data["risk_level"] = "CRITICAL"
        
        
        columns = ", ".join(data.keys())
        placeholder = ", ".join(["%s"] * len(data))
        values = tuple(data.values())
        sql = f"INSERT INTO missions ({columns}) VALUES ({placeholder}) "


        with self.db.get_cursor() as cursor : 
            cursor.execute(sql , values)
            new_id = cursor.lastrowid

        return {"message": f"data {data} create succesfully",
                "MissionId" : new_id}
    
    def get_all_missions(self) -> list[dict]: 
        with self.db.get_cursor() as cursor :
            cursor.execute("SELECT * FROM missions")
            return cursor.fetchall()
        
    def get_missions_by_id(self, agent_id : int ) -> dict | None : 
        with self.db.get_cursor() as cursor :
            cursor.execute("SELECT * FROM missions WHERE id = %s LIMIT 1 ", (agent_id, ))
            return cursor.fetchone()
        
    def assign_mission(self, mission_id : int , agent_id : int ) -> str : 

        exists_mission = self.get_missions_by_id(mission_id)
        exists_agent = self.agent_db.get_agent_by_id(agent_id)

        if not exists_agent:
            return "Agent not exists"
        if not exists_mission:
            return "Mission not exists"

        if exists_mission["status"] != "NEW" : 
            return "This mission already assigned"

        if exists_agent["is_active"] == False : 
            return f"This soldat {agent_id} is inactive "
        
        if exists_mission["risk_level"] == "CRITICAL" : 
            if exists_agent["agent_rank"] != "Commander": 
                return " The mission is too much dangerous for this agent"
            
        assigned_mission = self.get_open_missions_by_agent(agent_id) 
        if len(assigned_mission) >= 3 : 
            return  "The agent have already three mission"
        
        if exists_mission and exists_agent : 
            with self.db.get_cursor() as cursor :
                cursor.execute("UPDATE  missions SET  status = 'ASSIGNED' , assigned_agent_id" \
                "  =  %s WHERE id = %s ",(agent_id,mission_id))
                
                return "assigned Succesfully"
        return "Failed to assign"
    
    def update_mission_status(self, mission_id : int , status : str) -> str: 
        mission = self.get_missions_by_id(mission_id)
        status = status.upper()
        

        
        
        if mission["status"] == "ASSIGNED" and status !=  "IN_PROGRESS": 
            return "Status is ASSIGNED you can just to choice IN_PROGRESS"
        
        if mission["status"] == "IN_PROGRESS" and status not in ["FAILED", "COMPLETED"]: 
            return "Status is IN_PROGRESS you can just to choice failed or completed"
       
        with self.db.get_cursor() as cursor :
            cursor.execute("UPDATE missions SET status = %s WHERE id = %s ", (status, mission_id))
            return "Status updated successfully"
        
    def get_open_missions_by_agent(self, agent_id) -> list[dict] | None:
        with self.db.get_cursor() as cursor :
            cursor.execute("SELECT * FROM missions " \
            " WHERE (status ='IN_PROGRESS' OR status ='ASSIGNED') AND id = %s  " ,(agent_id, ))
            return cursor.fetchall()
        

    def count_all_missions(self) -> dict: 
        with self.db.get_cursor() as cursor :
            cursor.execute("SELECT COUNT(*) FROM missions")
            mission = cursor.fetchone()
            return {"total_mission" : mission["COUNT(*)"]}
        
    def count_by_status(self, status): 
         with self.db.get_cursor() as cursor :
            cursor.execute("SELECT COUNT(*) FROM missions WHERE status = %s", (status, ))
            mission = cursor.fetchone()
            return {"total_mission" : mission["COUNT(*)"]}
         

    def count_critical_missions(self): 
         with self.db.get_cursor() as cursor :
            cursor.execute("SELECT COUNT(*) FROM missions WHERE risk_level = 'CRITICAL' ")
            mission = cursor.fetchone()
            return {"total_CRITICAL_mission" : mission["COUNT(*)"]}
         
    def get_top_agent(self):
        with self.db.get_cursor() as cursor :
            cursor.execute("SELECT * FROM agents ORDER BY completed_missions DESC")
            return cursor.fetchone()
        
    def count_open_missions(self):
        with self.db.get_cursor() as cursor :
            cursor.execute("SELECT status , COUNT(status) AS active FROM missions " \
            " WHERE status IN ('IN_PROGRESS','NEW','ASSIGNED')" \
            " GROUP BY status")
            return cursor.fetchall()

    def delete_mission(self, mission_id) -> str : 
        with self.db.get_cursor() as cursor :
            mission = self.get_missions_by_id(mission_id)
            if mission["status"] not in ["NEW","ASSIGNED"] :
                return 'You can delete this mission'
            
            cursor.execute("DELETE FROM  missions WHERE id = %s ", (mission_id, ))
            return "Mission delete succesfully"


        
    
    

