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

    logger.info("Calculed risk_level from data")

    risk = int(data["difficulty"]) * 2 + int(data["importance"])

    if risk > 0 and risk <= 9 : 
        data["risk_level"] = "LOW"
    elif risk >= 10 and  risk <= 17:
        data["risk_level"] = "MEDIUM"
    elif risk >= 18 and  risk <= 24:
        data["risk_level"] = "HIGH"
    else: 
        data["risk_level"] = "CRITICAL"
    logger.info("risk is %s ",risk)
        
    logger.info("Create mission with risk , data : %s", data)
    result = mission_db.create_mission(data)
    logger.info("Mission create succesfully , %s", result)
    return result

@router_mission.get("")
def get_all_missions():
    return mission_db.get_all_missions()


@router_mission.put("/{mission_id}/assign/{agent_id}")
def assign_mission(mission_id : int , agent_id : int ): 

    logger.info("Try to assign mission , mission id %s | agent_id %s", mission_id,agent_id)

    exists_mission = mission_db.get_missions_by_id(mission_id)
    exists_agent = agent_db.get_agent_by_id(agent_id)

    if not exists_agent:
           logger.error("agent id %s not found", agent_id)
           raise HTTPException(404, "Agent not found")
    if not exists_mission:
            logger.error("mission id %s not found", mission_id)
            raise HTTPException(404, "Mission not exists")
    
    if exists_mission["status"] != "NEW" : 
            logger.error("Mission is not new")
            raise HTTPException(400, "Mission not available")

    if exists_agent["is_active"] == False : 
            logger.error("agent %s is inactive", agent_id)
            raise HTTPException(400, "Agent is not active")
        
    if exists_mission["risk_level"] == "CRITICAL" : 
        if exists_agent["agent_rank"] != "Commander": 
           logger.error("Mission CRITICAL and agent %s not Commander",agent_id)
           raise HTTPException(400 , "Only commander can handle critical missions")

    logger.info("Verifie if agent %s don't have more > 3 missions", agent_id)       
    assigned_mission = mission_db.get_open_missions_by_agent(agent_id) 
    if len(assigned_mission) >= 3 : 
        logger.error(f"Agent {agent_id} has {len(assigned_mission)}")
        raise HTTPException(400, "Agents has reached maximum missions")
    
    success = mission_db.assign_mission(mission_id, agent_id)
    if not success: 
         raise HTTPException(500, "Servor error")
    
    logger.info("agent %s assigned mission %s succesfuly", agent_id, mission_id)
    return {"message" : f"Mission {mission_id} assigned succesfuly for agent {agent_id}"}


@router_mission.put("/{mission_id}/start")
def start_mission(mission_id : int ):
    status = "IN_PROGRESS"
    logger.info("status = IN_PROGRESS")
    result = mission_db.update_mission_status(mission_id, status)

    if result == "mission not found": 
        logger.error("Not found mission %s", mission_id)
        raise HTTPException(404, result)
    
    if result != "Status updated successfully" : 
        logger.error("Failed ")
        raise HTTPException(400, result )
    
    return {"message": result}


@router_mission.put("/{mission_id}/complete")
def complete_mission(mission_id : int ):
    status = "COMPLETED"
    mission_test = mission_db.get_missions_by_id(mission_id)
    result = mission_db.update_mission_status(mission_id, status)

    if not  mission_test["assigned_agent_id"]: 
            raise HTTPException(400 , "you can't completed mission if" \
            " you not assigned agent , choose cancel ")

    if result == "mission not found": 
        raise HTTPException(404, result)
    
    if result != "Status updated successfully" : 
        raise HTTPException(400, result )
    else : 
        mission = mission_db.get_missions_by_id(mission_id)
        agent = mission["assigned_agent_id"]
        
        completed = agent_db.increment_completed(agent)
    
    return {"message": result, "completed": completed}

@router_mission.put("/{mission_id}/fail")
def failed_mission(mission_id : int ):
    status = "FAILED"

    mission_test = mission_db.get_missions_by_id(mission_id)

    if not  mission_test["assigned_agent_id"]: 
            raise HTTPException(400 , "you can't completed mission if" \
            "you not assigned agent , choose cancel ")

    result = mission_db.update_mission_status(mission_id, status)
    if result == "mission not found": 
        raise HTTPException(404, result)
    
    if result != "Status updated successfully" : 
        raise HTTPException(400, result )
    else : 
        mission = mission_db.get_missions_by_id(mission_id)
        agent = mission["assigned_agent_id"]
    
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



@router_mission.get("/{mission_id}")
def get_mission_by_id(mission_id : int ):
    mission = mission_db.get_missions_by_id(mission_id)
    if not mission:
        logger.error("Mission Id : %s not found", mission_id)
        raise HTTPException(404, "Mission not found")
    return mission

