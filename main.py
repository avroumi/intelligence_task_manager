from database.db_connection import DataBaseConnection
from database.agent_db import AgentDB
from database.mission_db import MissionDB

from routes.agent_routes import router_agent
from routes.mission_routes import router_mission
from routes.report_routes import router_report

from fastapi import FastAPI,Request
from contextlib import asynccontextmanager
from logs.logger_param import logger





db = DataBaseConnection()



@asynccontextmanager
async def lifespan(app : FastAPI):
    db.setup()
    yield

app = FastAPI(title="Intelligence Task Manager", lifespan=lifespan)

@app.middleware("http")
async def middleware(req : Request, call_next):
    logger.info(f"START | {req.method} |{req.url.path} ")
    response = await call_next(req)
    logger.info(f"END | {req.method} | {req.url.path} | status={response.status_code} ")

    return response




app.include_router(router_agent)
app.include_router(router_mission)
app.include_router(router_report)


