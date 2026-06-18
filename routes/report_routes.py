from logs.logger_param import logger
from database.agent_db import AgentDB
from database.db_connection import DataBaseConnection
from database.mission_db import MissionDB

from fastapi import  APIRouter

db = DataBaseConnection()
agent_db = AgentDB(db)
mission_db = MissionDB(db , agent_db)

router_report =  APIRouter(prefix="/reports", tags=["Reports"])

@router_report.get("/summary")
def get_all_reports():
    logger.info("Start to catch all reports")
    active_agent = agent_db.count_active_agents()
    total_missions = mission_db.count_all_missions()
    open_missions = mission_db.count_open_missions()
    completed_missions = mission_db.count_by_status("COMPLETED")
    failed_missions = mission_db.count_by_status("FAILED")
    critical_missions = mission_db.count_critical_missions()

    return [active_agent, total_missions, open_missions, completed_missions,failed_missions,critical_missions ]

@router_report.get("/missions-by-status")
def report_by_status():
    logger.info("start to get all missions by status")
    return mission_db.count_all_mission_by_status()

@router_report.get("/top-agent")
def get_top_agent():
    logger.info("Start to get the top agent ")
    return mission_db.get_top_agent()