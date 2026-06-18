from logs.logger_param import logger
from database.agent_db import AgentDB
from database.db_connection import DataBaseConnection

from fastapi import APIRouter, HTTPException,Request
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
    legal_data = data.model_dump(exclude_none=True)
    if not legal_data:
        raise HTTPException(400, "You don't have data")
    
    result = agent_db.create_agent(legal_data)
    return {"message" : result}

@router_agent.get("")
def get_all_agent(): 
    return agent_db.get_all_agents()

@router_agent.get("/{agent_id}")
def get_agent_by_id(agent_id): 
    agent = agent_db.get_agent_by_id(agent_id)
    if not agent : 
        raise HTTPException(404, "Agent not found")
    return agent 

@router_agent.put("/{agent_id}")
def update_agent(agent_id : int , data : UpdateAgent):

    agent_exist = agent_db.get_agent_by_id(agent_id) 
    if not agent_exist:
        raise HTTPException(404, "Not found agent")
     

    updated_data = data.model_dump(exclude_none=True)
    if not updated_data : 
        raise HTTPException(400 , "Not data")
    
    success = agent_db.update_agent(agent_id, updated_data)
    if not success :
        raise HTTPException(400 , "Ineligible data")
    return {"message": "Agent updated succesfuly"}

@router_agent.put("/{agent_id}/deactivate")
def deactivate_agent(agent_id): 
    agent_exist = agent_db.get_agent_by_id(agent_id) 
    if not agent_exist:
        raise HTTPException(404, "Not found agent")
    
    result = agent_db.deactivate_agent(agent_id)

    return {"message" : result }

@router_agent.get("/{agent_id}/performance")
def get_performance_agent_by_id(agent_id): 

    result = agent_db.get_agent_performance(agent_id)
    if result == "agent not found": 
        raise HTTPException(404, result)
    return result 

    
