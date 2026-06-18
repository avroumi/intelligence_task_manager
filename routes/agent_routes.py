from logs.logger_param import logger
from database.agent_db import AgentDB
from database.db_connection import DataBaseConnection

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

db = DataBaseConnection()
agent_db = AgentDB(db)


class CreateAgent(BaseModel): 

    name : str = Field(min_length=1 , max_length=50)
    specialty : str = Field(min_length=1 , max_length=100)
    is_active : bool | None = None 
    completed_missions : int | None = None 
    failed_missions : int | None = None 
    agent_rank : Literal["Junior", "Senior", "Commander"]

class UpdateAgent(BaseModel):

    name : str | None = Field(default=None, min_length=1 , max_length=50)
    specialty : str | None= Field(default= None, min_length=1 , max_length=100)
    is_active : bool | None = None 
    completed_missions : int | None = None 
    failed_missions : int | None = None 
    agent_rank : Literal["Junior", "Senior", "Commander"] | None = None 




router_agent = APIRouter(prefix="/agents" , tags=["Agents"])


@router_agent.post("", status_code=201)
def create_agent(data : CreateAgent): 
    logger.info(f"Create new_agent : data {data}")
    legal_data = data.model_dump(exclude_none=True)
    if not legal_data:
        logger.error("Data not eligible : %s",data)
        raise HTTPException(400, "You don't have data")
    
    result = agent_db.create_agent(legal_data)
    logger.info("Agent create succesfully : %s", result)
    return {"message" : result}

@router_agent.get("")
def get_all_agent(): 
    return agent_db.get_all_agents()


@router_agent.put("/{agent_id}")
def update_agent(agent_id : int , data : UpdateAgent):
    logger.info("Update the agent %s", agent_id)
    agent_exist = agent_db.get_agent_by_id(agent_id) 
    if not agent_exist:
        logger.error("Id not found : %s", agent_id)
        raise HTTPException(404, "Not found agent")
     

    updated_data = data.model_dump(exclude_none=True)
    if not updated_data : 
        logger.error("Data not eligible : %s", updated_data)
        raise HTTPException(400 , "Not data")
    
    success = agent_db.update_agent(agent_id, updated_data)
    if not success :
        logger.error("Update failed")
        raise HTTPException(400 , "Ineligible data")
    
    logger.info("Agent update succesfully id : %s , rowcont : %s",agent_id,success)
    return {"message": "Agent updated succesfuly"}

@router_agent.put("/{agent_id}/deactivate")
def deactivate_agent(agent_id): 
    logger.info("Deactivate agent %s",agent_id)
    agent_exist = agent_db.get_agent_by_id(agent_id) 
    if not agent_exist:
        logger.error("Agent %s not fond ", agent_id)
        raise HTTPException(404, "Not found agent")
    
    result = agent_db.deactivate_agent(agent_id)
    logger.info("Deactivate succesfully : %s",result)
    return {"message" : result }

@router_agent.get("/{agent_id}/performance")
def get_performance_agent_by_id(agent_id): 
    logger.info("Try to get performance agent %s", agent_id)

    result = agent_db.get_agent_performance(agent_id)
    if result == "agent not found": 
        logger.error("Agent %s not found ", agent_id)
        raise HTTPException(404, result)
    logger.info("Performance catch succeuflly ")
    return result 

    
@router_agent.get("/{agent_id}")
def get_agent_by_id(agent_id : int ): 
    logger.info("Try to find agent by id : %s",agent_id)
    agent = agent_db.get_agent_by_id(agent_id)
    if not agent : 
        logger.error("Agent id %s not found", agent_id)
        raise HTTPException(404, "Agent not found")
    
    return agent 
