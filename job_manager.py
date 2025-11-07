# job_manager.py
import json, uuid
from datetime import datetime, timezone
from db import get_conn
from db import get_conn

# ------------------ STATUS COMMAND ------------------
def job_status():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT state, COUNT(*) as count FROM jobs GROUP BY state;")
    rows = cur.fetchall()
    print("\nJob Status Summary:")
    for r in rows:
        print(f"  {r['state']:<10} {r['count']}")
    conn.close()


# ------------------ LIST COMMAND ------------------
def list_jobs(state=None):
    conn = get_conn()
    cur = conn.cursor()
    if state:
        cur.execute("SELECT * FROM jobs WHERE state=?", (state,))
    else:
        cur.execute("SELECT * FROM jobs;")
    rows = cur.fetchall()

    if not rows:
        print("No jobs found.")
    else:
        print("\nJobs:")
        for r in rows:
            print(f"  {r['id']} | {r['state']} | attempts={r['attempts']}/{r['max_retries']} | {r['command']}")
    conn.close()


# ------------------ DLQ LIST ------------------
def dlq_list():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs WHERE state='dead';")
    rows = cur.fetchall()
    if not rows:
        print("No jobs in DLQ.")
    else:
        print("\nDead Letter Queue Jobs:")
        for r in rows:
            print(f"  {r['id']} | attempts={r['attempts']} | {r['command']}")
    conn.close()


# ------------------ DLQ RETRY ------------------
def dlq_retry(job_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs WHERE id=? AND state='dead'", (job_id,))
    job = cur.fetchone()
    if not job:
        print(f"Job {job_id} not found in DLQ.")
    else:
        cur.execute("UPDATE jobs SET state='pending', attempts=0, next_run_at=0 WHERE id=?", (job_id,))
        conn.commit()
        print(f"Job {job_id} moved back to pending queue.")
    conn.close()


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def enqueue_job(payload_json):
    try:
        job = json.loads(payload_json)
    except json.JSONDecodeError as e:
        print("Invalid JSON payload:", e)
        return
    
    job_id = job.get("id", f"job-{uuid.uuid4().hex[:8]}")
    command = job.get("command")
    if not command:
        print("Missing 'command' in job JSON")
        return

    now = now_iso()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO jobs (id, command, state, attempts, max_retries, created_at, updated_at)
        VALUES (?, ?, 'pending', 0, ?, ?, ?)
    """, (job_id, command, job.get("max_retries", 3), now, now))
    conn.commit()
    conn.close()
    print(f"Job {job_id} enqueued successfully")
