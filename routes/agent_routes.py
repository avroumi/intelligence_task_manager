from logs.logger_param import logger
from database.agent_db import AgentDB

from fastapi import APIRouter, HTTPException,Request
from pydantic import BaseModel, Field
from typing import Literal


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




def create_router_agent(agent_db : AgentDB) -> APIRouter:
    router = APIRouter(prefix="/agents" , tags="[Agents]")


    @router.post("", status_code=201)
    def create_agent(data : CreateAgent): 
        legal_data = data.model_dump(exclude_none=True)
        if not legal_data:
            raise HTTPException(400, "You don't have data")
        
        result = agent_db.create_agent(legal_data)
        return {"message" : result}
    
