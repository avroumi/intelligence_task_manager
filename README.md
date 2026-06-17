PROJECT INTELLIGENCE TASK MANAGER : 


1/ This project aims to simplify the task and allow the system to define rules for assigning missions to soldiers, using an SQL table that will include statistics, statuses, and rules to manage everything systematically.

The SQL project is divided into two tables in the intelligence_db database:
    a/ agents
    b/ missions
We will detail these later, but it is with this data that we will be able to have clear and organized tracking.

2/ The project architecture unfolds as follows:(update think comming tommorow)

    intelligence-task-manager/
    ├── database/
    │   ├── db_connection.py
    │   ├── agent_db.py
    │   └── mission_db.py
    ├── README.md
    ├── requirements.txt
    └── .gitignore

3/ We have two SQL tables; I'll describe them now:
    a/ The `agents` table is responsible for information about agents, such as their ID, name, and specialty.

    It also contains the `is_active` logic, which is boolean, and information about their number of failed missions, completed missions, and their rank.
    Here sql table : 
    """
    CREATE TABLE IF NOT EXISTS agents(
        id INT PRIMARY KEY AUTO_INCREMENT , 
        name VARCHAR(50) NOT NULL , 
        specialty VARCHAR(100) NOT NULL , 
        is_active BOOLEAN DEFAULT TRUE , 
        completed_missions INT NOT NULL  DEFAULT 0  , 
        failed_missions INT NOT NULL DEFAULT 0 ,
        agent_rank ENUM("Junior", "Senior", "Commander") NOT NULL  )
    """

    b/ The missions table deals with the logic of missions and their importance; it contains its id, its name as a title, its description, its location, as well as its difficulty and its importance which defines its risk_level and the agents assigned.
    sql_table : 
    """
            CREATE TABLE IF NOT EXISTS missions(
        id INT PRIMARY  KEY AUTO_INCREMENT , 
        title VARCHAR(100) NOT NULL , 
        description TEXT NOT NULL , 
        location VARCHAR(100) NOT NULL , 
        difficulty INT NOT NULL CHECK(difficulty BETWEEN 1 AND 10 ), 
        importance INT NOT NULL CHECK(importance BETWEEN 1 AND 10 ), 
        status ENUM("NEW", "ASSIGNED", "IN_PROGRESS", "COMPLETED", "FAILED", "CANCELLED") DEFAULT "NEW", 
        risk_level VARCHAR(50) NOT NULL , 
        assigned_agent_id INT   
                       )      
    """

4/ Apart from that, we have 3 files, each with its own role: `db_connections` handles the connection logic to Docker via MySQL, including opening and closing. `agentDB` handles Docker with the SQL agent and applies CRUD operations; `missionDB` does the same, but with the `missions` table. Here's their method.

    a/ db_connections : 
    get_connection(): create connection with the database 
    create_database(): create the intelligence_db if not exists
    create_tables(): create table if not exists

    b/agentDB : 
    create_agent(data) : creates a new agent and returns the agent object
    get_all_agents() :  returns a list of all agents
    get_agent_by_id(id) : returns one agent by ID, or None
    update_agent(id, data) : UPDATE the entire row (id cannot be changed)
    deactivate_agent(id) : sets the agent to inactive

    increment_completed(id):  updates the number of completed tasks 
    increment_failed(id):  updates the number of failed tasks
    get_agent_performance(id) : returns a dictionary with these keys completed, failed, total, success_rate
                 (note that this value is calculated as success_rate - what percentage of tasks completed successfully out of the total)
    count_active_agents() :  returns the number of active agents

    c/missionDB 

    create_mission(data): Creates a new mission and returns the entire object
    get_all_missions() : returns all missions
    get_mission_by_id(id) : returns a single mission by ID, or None
    assign_mission(m_id, a_id): assigns a mission to an agent
    update_mission_status(id, status) is used for any status change
    get_open_missions_by_agent(id) returns ASSIGNED/IN_PROGRESS missions of an agent
    count_all_missions() : total missions
    count_by_status(status) : counts by a specific status
    count_open_missions():  counts open missions
    count_critical_missions() : counts CRITICAL missions
    get_top_agent() : the agent with the highest completed_missions


5/the rules of th project 
    
    
     1: rank must be Junior / Senior / Commander — any other value throws an error.
    2: difficulty and importance must be between 1 and 10 — otherwise an error.
    3: risk_level is calculated automatically when creating a task — the user does not submit it.
    4: An agent with is_active=False cannot accept tasks.
    5:  An agent cannot have more than 3 open tasks (ASSIGNED / IN_PROGRESS) at the same time.
    6: If risk_level=CRITICAL — only an agent with the Commander rank can accept the task.
    7: Only a task with the status NEW can be assigned. After assignment: status=ASSIGNED.
    8: Only a task with the status ASSIGNED can be started. After: status=IN_PROGRESS.
    9: Only a task with the status IN_PROGRESS can be finished and changed to failed or completed.
    10: Only a task with the status NEW or ASSIGNED can be canceled — otherwise an error.

6/ You need Docker to launch this project and connect to MySQL. Here's how: write this in your terminal. 

docker run -d --name intelligence-mysql -e MYSQL_ROOT_PASSWORD=1234 \
  -e MYSQL_DATABASE=Intelligence_db -p 3306:3306 mysql:8.0

  now active your mysql in docker and you can run it ; Good luck 

