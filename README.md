# Automated News Aggregator API

This project is a complete backend system built with **FastAPI**, **Celery**, and **MySQL**, designed to automatically fetch top headlines from an external News API every minute and serve them to users via a lightning-fast REST endpoint.

---

## 🏗️ System Architecture & How It Works

This application is composed of **three separate running services** that work together:

### 1. The FastAPI Web Server (`app/main.py`)
This is the user-facing web server. It listens for incoming HTTP requests and queries the MySQL database. It does **not** fetch news directly from the Internet because that would make the API too slow for users. 

### 2. The Celery Worker (`app/worker.py`)
This is the background "muscle" of the project. It runs independently from the web server. When it receives a signal, this worker reaches out to `https://newsapi.org`, downloads the latest JSON headlines, and securely inserts the new rows into the MySQL database using SQLAlchemy.

### 3. The Celery Beat Scheduler (`app/worker.py`)
This is the background "alarm clock". It holds a strict 60-second countdown timer. Every minute, it sends a message through the **Redis Message Broker** telling the Celery Worker to wake up and fetch new articles.

### 🧠 The Role of Redis
When the Beat Scheduler yells "Wake up!", the Celery Worker might be busy. **Redis** acts as the fast, in-memory middleman queue. The Scheduler drops the "fetch news" task into the Redis bucket, and the Worker pulls tasks out of the bucket as fast as it can.

---

## 🛠️ Prerequisites & Installation

To run this application, you must have the following installed on your machine:
- **Python 3.8+**
- **MySQL Server**
- **Redis** (Installed via WSL on Windows, or natively on Linux/Mac)

### 1. Clone the Repository & Configure Credentials
Create a `.env` file in the root directory and add your secret keys:
```env
MYSQL_USER="root"
MYSQL_PASSWORD="your_mysql_password"
MYSQL_HOST="localhost"
MYSQL_PORT="3306"
MYSQL_DB="news_db"
NEWS_API_KEY="your_free_key_from_newsapi.org"
CELERY_BROKER_URL="redis://localhost:6379/0"
CELERY_RESULT_BACKEND="redis://localhost:6379/0"
```

### 2. Install Dependencies
Open a terminal and create a Python virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

### 3. Initialize the Database
Run the helper script to create the `news_db` table automatically inside your MySQL server:
```powershell
python init_db.py
```

---

## 🚀 How to Run the Application

You need to open **3 separate terminal windows**.
In **every terminal**, make sure to activate the virtual environment first:
```powershell
.\venv\Scripts\Activate
```

### Terminal 1: Start the Web API
```powershell
uvicorn app.main:app --reload
```

### Terminal 2: Start the Background Worker
```powershell
celery -A app.worker.celery_app worker -l INFO -P eventlet
```

### Terminal 3: Start the Background Scheduler
```powershell
celery -A app.worker.celery_app beat -l INFO
```

---

## 📡 API Usage & Response

Once the 3 terminals are running, the application will begin fetching data in the background instantly.

### Check the Endpoint
You can fetch articles for a specific date by visiting this URL in your browser or Postman:

**`GET http://127.0.0.1:8000/news?date=YYYY-MM-DD`**

*(Example: `http://127.0.0.1:8000/news?date=2024-03-04`)*

### Example JSON Response
Our system uses custom FastAPI Middleware to calculate exactly how fast the server processed the request, and automatically injects `"total_time_taken": "[time] ms"` at the very bottom of the response.

```json
{
  "data": [
    {
      "source_name": "TechCrunch",
      "author": "Jane Doe",
      "title": "A breakthrough in AI technology",
      "description": "Researchers announce new model...",
      "url": "https://techcrunch.com/article...",
      "published_at": "2024-03-04T12:00:00Z",
      "id": 1,
      "published_date": "2024-03-04",
      "created_at": "2024-03-04T12:01:03.453Z"
    }
  ],
  "total_time_taken": "8.43 ms"
}
```

### Interactive Documentation
Because we built this using FastAPI, you get beautiful, automatic Swagger documentation. 
You can view it and test your API directly by visiting: **`http://127.0.0.1:8000/docs`**
