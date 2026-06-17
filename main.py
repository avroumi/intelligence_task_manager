from database.db_connection import DataBaseConnection
from database.agent_db import AgentDB
from database.mission_db import MissionDB

db = DataBaseConnection()
repo = AgentDB(db)
repo_mission = MissionDB(db)

# print(repo.create_agent({"name":"avroumi", "specialty": "boomer", "completed_missions": "1","failed_missions": "1", "agent_rank" : "Senior"}))
# print(repo.get_all_agents())
# # print(repo.get_agent_by_id(3))
# print(repo.deactivate_agent(1))
# print(repo.get_agent_by_id(1))
# print(repo.increment_failed(1))
# print(repo.get_agent_by_id(1))
# print(repo.increment_failed(1))
# # print(repo.get_agent_by_id(1))
# print(repo.get_agent_performance(5))
# print(repo.count_active_agents())


# print(repo_mission.create_mission_({"title" : "lebvanon","description": "balbala", 
#                                     "location" : "yes" , "difficulty" : "4" , "importance" : "90", "status": "IN_PROGRESS"}))

# risk = {"title" : "lebvanon","description": "balbala", 
#                                     "location" : "yes" , "difficulty" : "4" , "importance" : "7"}

# print(int(risk["importance"]))
# print(repo_mission.assign_mission(10, 3))
# print(repo_mission.get_all_missions())
# print(repo_mission.get_open_missions_by_agent(1))
# print(repo_mission.get_all_missions())

# print(repo_mission.count_by_status("J"))
# print(repo_mission.get_top_agent())
# # print(repo_mission.update_mission_status(1,"IN_PROGRESS"))
# print(repo_mission.get_missions_by_id(1))
# print(repo_mission.count_open_missions())
print(repo_mission.get_open_missions_by_agent(2))
# print(repo_mission.assign_mission(2,2))
# print(repo.get_agent_by_id(2))
# print(repo_mission.get_missions_by_id(2))