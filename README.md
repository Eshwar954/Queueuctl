#  QueueCTL — CLI-Based Background Job Queue System

**QueueCTL** is a lightweight, CLI-driven background job queue system built for managing background jobs with worker processes, automatic retries, exponential backoff, and a Dead Letter Queue (DLQ).  
It’s written in **Python**, uses **SQLite** for persistence, and supports multiple concurrent workers.

---

##  Features

-  Enqueue background jobs with shell commands  
-  Persistent job storage (SQLite)  
-  Multiple worker threads for parallel job execution  
-  Automatic retries on failure with exponential backoff  
-  Dead Letter Queue (DLQ) for permanently failed jobs  
-  Configurable retry count and backoff base via CLI  
-  Graceful worker shutdown (no lost jobs)  
-  Clean and intuitive CLI interface  

---

##  Tech Stack

- **Language:** Python 3.x  
- **Database:** SQLite (via `sqlite3` module)  
- **Concurrency:** Python threading  
- **CLI Framework:** argparse  
- **OS Support:** Cross-platform (Windows, macOS, Linux)

---

##  Project Structure

###  What Each File Does

| File | Description |
|------|--------------|
| **queuectl.py** | Main CLI controller — parses commands like enqueue, worker, status, list, and dlq. |
| **db.py** | Handles database connection setup and schema creation. |
| **job_manager.py** | Manages job lifecycle (enqueue, retry, list, status, DLQ operations). |
| **worker_manager.py** | Spawns worker threads that process background jobs concurrently. |
| **config_manager.py** | Handles configuration (e.g., max_retries, backoff_base). |
| **queue.db** | SQLite database file that stores job data (auto-generated). |


---

##  Job Schema

Each job is stored as a row in the `jobs` table:

| Field | Type | Description |
|-------|------|-------------|
| id | TEXT | Unique job identifier |
| command | TEXT | Shell command to execute |
| state | TEXT | Job state (`pending`, `processing`, `completed`, `failed`, `dead`) |
| attempts | INTEGER | Number of retry attempts |
| max_retries | INTEGER | Maximum retry limit |
| created_at | TEXT | Creation timestamp |
| updated_at | TEXT | Last update timestamp |
| next_run_at | INTEGER | Time (Unix) when next retry is scheduled |

---

##  Job Lifecycle

| State | Description |
|--------|-------------|
| **pending** | Waiting to be picked by a worker |
| **processing** | Currently executing |
| **completed** | Successfully executed |
| **failed** | Failed but still retryable |
| **dead** | Permanently failed (moved to DLQ) |

---

##  Setup Instructions

### 1️ Clone the Repository
```bash
git clone https://github.com/Eshwar954/Queueuctl.git
cd Queuectl
```

### 2️ Run Database Initialization (auto)

The first CLI command will automatically create `queue.db`.

### 3️ Install Python (if not installed)

Make sure you have **Python 3.8+** installed:

```bash
python --version
```
##  How to Run Commands

After cloning the repository and setting up Python, run all commands from inside the `queuectl` folder.

---

### Enqueue a Job
Add a new background job to the queue.

```bash
python queuectl.py enqueue --command "echo Hello"
```

---

### Start Worker(s)
Start one or more workers to process queued jobs.

```bash
python queuectl.py worker --count 2
```

---

### Update Configuration
Set configuration parameters such as retry count or backoff base.

```bash
python queuectl.py config max_retries 5
python queuectl.py config backoff_base 2
```

---

### View Job Status Summary
Display counts of jobs by their current state.

```bash
python queuectl.py status
```

---

### List Jobs by State
List all jobs or filter by a specific state.

```bash
python queuectl.py list
python queuectl.py list --state pending
python queuectl.py list --state completed
```

---

### View Dead Letter Queue (DLQ)
View permanently failed jobs stored in the DLQ.

```bash
python queuectl.py dlq list
```

---

### Retry a DLQ Job
Move a failed job from the DLQ back into the pending queue for re-execution.

```bash
python queuectl.py dlq retry <job_id>
```

---

### Example Full Flow

```bash
# 1. Enqueue two jobs
python queuectl.py enqueue --command "echo Success"
python queuectl.py enqueue --command "bash -c 'exit 1'"

# 2. Start a worker
python queuectl.py worker --count 1

# 3. Check job summary
python queuectl.py status

# 4. View DLQ
python queuectl.py dlq list

# 5. Retry a failed job
python queuectl.py dlq retry <job_id>
```

---

### Tip
Press **Ctrl + C** anytime to stop workers gracefully — they will finish the current job before shutting down.





