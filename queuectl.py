import argparse
import json
from db import init_db
from job_manager import enqueue_job, job_status, list_jobs, dlq_list, dlq_retry
from worker_manager import start_workers
from config_manager import set_config

def main():
    parser = argparse.ArgumentParser(prog="queuectl", description="Background Job Queue CLI Tool")
    sub = parser.add_subparsers(dest="cmd")

    # ENQUEUE COMMAND 
    e = sub.add_parser("enqueue", help="Add a new job to the queue")
    e.add_argument("--command", required=True, help="Shell command to run for this job")
    e.add_argument("--max_retries", type=int, default=3, help="Maximum retry attempts for the job")

    # WORKER COMMAND 
    w = sub.add_parser("worker", help="Start background workers")
    w.add_argument("--count", type=int, default=1, help="Number of worker threads to start")

    # CONFIG COMMAND 
    c = sub.add_parser("config", help="Set configuration key/value")
    c.add_argument("key", help="Configuration key (e.g. max_retries, backoff_base)")
    c.add_argument("value", help="Configuration value")

    #STATUS COMMAND
    s = sub.add_parser("status", help="Show summary of job states")

    #LIST COMMAND
    l = sub.add_parser("list", help="List jobs by state")
    l.add_argument("--state", required=False, help="Filter by job state (pending, processing, completed, failed, dead)")

    #  DLQ COMMAND
    d = sub.add_parser("dlq", help="Manage Dead Letter Queue (DLQ)")
    d_sub = d.add_subparsers(dest="dlq_cmd")

    dlq_list_parser = d_sub.add_parser("list", help="List all DLQ jobs")
    dlq_retry_parser = d_sub.add_parser("retry", help="Retry a DLQ job")
    dlq_retry_parser.add_argument("job_id", help="Job ID to retry from DLQ")

    #PARSE & EXECUTE
    args = parser.parse_args()
    init_db()

    # ENQUEUE
    if args.cmd == "enqueue":
        payload = json.dumps({
            "command": args.command,
            "max_retries": args.max_retries
        })
        enqueue_job(payload)

    # WORKER
    elif args.cmd == "worker":
        start_workers(args.count)

    # CONFIG
    elif args.cmd == "config":
        set_config(args.key, args.value)

    # STATUS
    elif args.cmd == "status":
        job_status()

    # LIST
    elif args.cmd == "list":
        list_jobs(args.state)

    # DLQ
    elif args.cmd == "dlq":
        if args.dlq_cmd == "list":
            dlq_list()
        elif args.dlq_cmd == "retry":
            dlq_retry(args.job_id)
        else:
            print("Use: queuectl dlq list | queuectl dlq retry <job_id>")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
