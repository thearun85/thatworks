import os

class SchedulerConfig:

    INSTANCE_ID = os.getenv("SCHEDULER_ID", "scheduler-1")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/monitor")
    LOOP_INTERVAL = os.getenv("LOOP_INTERVAL", 10)
    BATCH_SIZE = os.getenv("BATCH_SIZE", 10)

    MAX_BACKOFF = 3600
    BACKOFF_MULTIPLIER = 2
    LOCK_TIMEOUT = 60

config = SchedulerConfig()
