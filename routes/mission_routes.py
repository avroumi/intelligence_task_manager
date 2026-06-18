from fastapi import APIRouter, HTTPException,Request
from pydantic import BaseModel, Field
from typing import Literal

from logs.logger_param import logger
from database.agent_db import AgentDB
from database.db_connection import DataBaseConnection
from database.mission_db import MissionDB

db = DataBaseConnection()
agent_db = AgentDB(db)
mission_db = MissionDB(db , agent_db)


class CreateMission(BaseModel):

    title : str = Field(min_length=1 , max_length=100)
    description : str
    location : str = Field(min_length=1 , max_length=100)
    difficulty : int = Field(ge=1, le=10)
    importance : int = Field(ge=1, le=10)

class UpdateStatus(BaseModel): 
    status : Literal["NEW", "ASSIGNED", "IN_PROGRESS",
                      "COMPLETED", "FAILED", "CANCELLED"]

router_mission = APIRouter(prefix="/missions", tags=["Missions"])

@router_mission.post("",status_code=201)
def create_missions(data_test : CreateMission):
    data = data_test.model_dump()

    risk = int(data["difficulty"]) * 2 + int(data["importance"])

    if risk > 0 and risk <= 9 : 
        data["risk_level"] = "LOW"
    elif risk >= 10 and  risk <= 17:
        data["risk_level"] = "MEDIUM"
    elif risk >= 18 and  risk <= 24:
        data["risk_level"] = "HIGH"
    else: 
        data["risk_level"] = "CRITICAL"

    result = mission_db.create_mission(data)

    return result

@router_mission.get("")
def get_all_missions():
    return mission_db.get_all_missions()

@router_mission.get("/{mission_id}")
def get_mission_by_id(mission_id : int ):
    mission = mission_db.get_missions_by_id(mission_id)
    if not mission:
        raise HTTPException(404, "Mission not found")
    return mission

@router_mission.put("/{mission_id}/assign/{agent_id}")
def assign_mission(mission_id : int , agent_id : int ): 

    exists_mission = mission_db.get_missions_by_id(mission_id)
    exists_agent = agent_db.get_agent_by_id(agent_id)

    if not exists_agent:
           raise HTTPException(404, "Agent not found")
    if not exists_mission:
            raise HTTPException(404, "Mission not exists")
    
    if exists_mission["status"] != "NEW" : 
            raise HTTPException(400, "Mission not available")

    if exists_agent["is_active"] == False : 
            raise HTTPException(400, "Agent is not active")
        
    if exists_mission["risk_level"] == "CRITICAL" : 
        if exists_agent["agent_rank"] != "Commander": 
           raise HTTPException(400 , "Only commander can handle critical missions")
            
    assigned_mission = mission_db.get_open_missions_by_agent(agent_id) 
    if len(assigned_mission) >= 3 : 
        raise HTTPException(400, "Agents has reached maximum missions")
    
    success = mission_db.assign_mission(mission_id, agent_id)
    if not success: 
         raise HTTPException(500, "Servor error")
    
    return {"message" : f"Mission {mission_id} assigned succesfuly for agent {agent_id}"}


@router_mission.put("/{mission_id}/start")
def start_mission(mission_id : int ):
    status = "IN_PROGRESS"
    result = mission_db.update_mission_status(mission_id, status)
    if result == "mission not found": 
        raise HTTPException(404, result)
    if result != "Status updated successfully" : 
        raise HTTPException(400, result )
    
    return {"message": result}


@router_mission.put("/{mission_id}/complete")
def start_mission(mission_id : int ):
    status = "COMPLETED"
    result = mission_db.update_mission_status(mission_id, status)

    if result == "mission not found": 
        raise HTTPException(404, result)
    
    if result != "Status updated successfully" : 
        raise HTTPException(400, result )
    else : 
        mission = mission_db.get_missions_by_id(mission_id)
        agent = mission["assigned_agent_id"]
        if not agent : 
            raise HTTPException(400 , "you can't completed mission if" \
            "you not assigned agent , choose cancel ")
        completed = agent_db.increment_completed(agent)
    
    return {"message": result, "completed": completed}

@router_mission.put("/{mission_id}/fail")
def start_mission(mission_id : int ):
    status = "FAILED"
    result = mission_db.update_mission_status(mission_id, status)
    if result == "mission not found": 
        raise HTTPException(404, result)
    
    if result != "Status updated successfully" : 
        raise HTTPException(400, result )
    else : 
        mission = mission_db.get_missions_by_id(mission_id)
        agent = mission["assigned_agent_id"]
        if not agent : 
            raise HTTPException(400, "you can't failed mission if" \
            "you not assigned agent , choose cancel ")
        failed = agent_db.increment_failed(agent)
    
    return {"message": result, "failed": failed}
    
   
@router_mission.put("/{mission_id}/cancel")
def cancelled_mission(mission_id : int):
    status = "CANCELLED"
    result = mission_db.update_mission_status(mission_id, status)
    if result == "mission not found": 
        raise HTTPException(404, result)
    if result != "Status updated successfully" : 
        raise HTTPException(400, result )
    
    return {"message": result}




