# How to Start the News API Project

This document explains where all your code is located and how to start the three main background services required for the project.

## 1. Project Structure Explained

Your project is structured like a modern Python application. The core code is kept inside an `app/` folder so it doesn't clutter the main root directory:

```text
Jarvis_Invest_Assignment/
│
├── .env                  # Your secret keys (MySQL password, NewsAPI key)
├── requirements.txt      # The list of downloaded Python libraries
├── init_db.py            # The script we ran to auto-create 'news_db'
├── venv/                 # The Python virtual environment (contains installed packages)
│
└── app/                  # *** ALL YOUR ACTUAL CODE IS HERE ***
    ├── main.py           # The FastAPI Web Server & the GET /news endpoint
    ├── models.py         # SQLAlchemy Database Schemas
    ├── database.py       # MySQL connection setup
    ├── logger.py         # Custom logging (INFO, ERROR, etc.)
    ├── schemas.py        # Pydantic data validation 
    ├── worker.py         # The Celery background job configuration
    │
    └── services/
        └── news_api.py   # *** THIS IS WHERE THE NEWS API LOGIC LIVES ***
```

If you ever need to show the interviewer where the News API request code is, tell them you architected it by placing API interactions inside the `app/services/` folder to keep the code clean and separated.

---

## 2. How to Start the 3 Services

To run this project, you need **3 separate PowerShell windows** open at the same time. 

In *every single window*, make sure you are in the `Jarvis_Invest_Assignment` folder, and **always** run this command first to activate your Python environment:
```powershell
.\venv\Scripts\Activate
```

### Terminal 1: Start the Web API (FastAPI)
This terminal runs the web server that answers user requests on port 8000.
```powershell
uvicorn app.main:app --reload
```

### Terminal 2: Start the Background Worker (Celery)
This terminal runs the background worker that actually executes the Python code to fetch the news and save it to MySQL.
```powershell
celery -A app.worker.celery_app worker -l INFO -P eventlet
```

### Terminal 3: Start the Scheduler (Celery Beat)
This terminal runs the "alarm clock". It holds a stopwatch and, every 60 seconds exactly, it sends a message to Terminal 2 (via Redis) saying "Wake up and fetch the news!"
```powershell
celery -A app.worker.celery_app beat -l INFO
```

Once all 3 terminals are running, the application is fully online! You can view the web API interactive documentation by opening your browser and going to:
**http://127.0.0.1:8000/docs**
