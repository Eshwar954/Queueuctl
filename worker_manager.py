# worker_manager.py
import time, subprocess, threading, os
from datetime import datetime, timezone
from db import get_conn

STOP_FLAG = threading.Event()

def now_ts(): return int(datetime.now(timezone.utc).timestamp())

def pick_job(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT id FROM jobs
        WHERE state='pending' AND (next_run_at <= ? OR next_run_at=0)
        ORDER BY created_at LIMIT 1
    """, (now_ts(),))
    row = cur.fetchone()
    if not row: return None
    job_id = row["id"]
    cur.execute("UPDATE jobs SET state='processing' WHERE id=? AND state='pending'", (job_id,))
    conn.commit()
    if cur.rowcount == 0: return None
    cur.execute("SELECT * FROM jobs WHERE id=?", (job_id,))
    return cur.fetchone()

def handle_result(conn, job, code):
    cur = conn.cursor()
    if code == 0:
        cur.execute("UPDATE jobs SET state='completed', updated_at=? WHERE id=?", (datetime.now().isoformat(), job["id"]))
        print(f"{job['id']} completed")
    else:
        attempts = job["attempts"] + 1
        if attempts <= job["max_retries"]:
            delay = 2 ** attempts
            cur.execute("UPDATE jobs SET state='pending', attempts=?, next_run_at=?, updated_at=? WHERE id=?",
                        (attempts, now_ts() + delay, datetime.now().isoformat(), job["id"]))
            print(f"{job['id']} failed. retry in {delay}s")
        else:
            cur.execute("UPDATE jobs SET state='dead', updated_at=? WHERE id=?", (datetime.now().isoformat(), job["id"]))
            print(f"{job['id']} moved to DLQ")
    conn.commit()

def worker_loop(i):
    conn = get_conn()
    print(f"Worker-{i} running...")
    while not STOP_FLAG.is_set():
        job = pick_job(conn)
        if not job:
            time.sleep(1)
            continue
        print(f"Worker-{i} processing {job['id']}")
        code = subprocess.call(job["command"], shell=True)
        handle_result(conn, job, code)
    conn.close()

def start_workers(count):
    threads = []
    STOP_FLAG.clear()
    for i in range(count):
        t = threading.Thread(target=worker_loop, args=(i+1,), daemon=True)
        threads.append(t)
        t.start()
    print(f"{count} worker(s) started. Ctrl+C to stop.")
    try:
        while any(t.is_alive() for t in threads): time.sleep(0.5)
    except KeyboardInterrupt:
        STOP_FLAG.set()
        print("Stopping workers gracefully...")
        for t in threads: t.join()
