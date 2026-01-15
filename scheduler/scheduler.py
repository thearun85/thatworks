from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
import time
from datetime import datetime, timezone, timedelta

from .config import config
from app.services import check_health
from app.models import MonitoredUrl, HealthCheck, SchedulerLock
import logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self):
        self.scheduler_id = config.INSTANCE_ID
        self.running = False
        self.engine = create_engine(config.DATABASE_URL)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def acquire_lock(self, session:Session, url:MonitoredUrl)->bool:
    
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=config.LOCK_TIMEOUT)    
        existing_lock = session.get(SchedulerLock, url.id)
        if existing_lock:
            if existing_lock.expires_at <= now:
                existing_lock.locked_by = self.scheduler_id
                existing_lock.locked_at = now
                existing_lock.expires_at = expires_at
                session.commit()
                return True
            else:
                return False

        else:
            try:
                lock = SchedulerLock(
                    monitored_url_id = url.id,
                    locked_by = self.scheduler_id,
                    locked_at = now,
                    expires_at=expires_at,
                )
                session.add(lock)
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                return False
        
    def release_lock(self, session: Session, url: MonitoredUrl):
        lock = session.get(SchedulerLock, url.id)
        if lock and lock.locked_by == self.scheduler_id:
            session.delete(lock)
            session.commit()
        
    def get_due_urls(self, session:Session):
        now = datetime.now(timezone.utc)
        stmt = (
                select(MonitoredUrl)
                .where(MonitoredUrl.is_active == True)
                .where(
                    (MonitoredUrl.next_check_at == None) |
                    (MonitoredUrl.next_check_at < now)
                )
                .limit(config.BATCH_SIZE)
            )
        result = session.execute(stmt)
        urls = result.scalars().all()
        return urls

    def check_single_url(self, session:Session, url: MonitoredUrl):
        logger.info(f"Processing {url.url}")
        if not self.acquire_lock(session, url):
            logger.info(f"Another scheduler holds a lock on {url.url}")
            return
        try:
            result = check_health(url.url, url.timeout_s)
            hc = HealthCheck(
                url = url.url,
                timeout_s = url.timeout_s,
                status_code = result.get("status_code"),
                is_healthy = True if result.get("status") == "healthy" else False,
                response_time_ms = result.get("response_time_ms"),
                error = result.get("error"),
            )
            session.add(hc)
            now = datetime.now(timezone.utc)
            url.last_checked_at = now

            if result.get("status") == "healthy":
                url.next_check_at = now + timedelta(seconds=url.check_interval_s)
                url.consecutive_failures = 0
            else:
                url.consecutive_failures +=1
                backoff_seconds = min(
                   url.check_interval_s * (config.BACKOFF_MULTIPLIER ** url.consecutive_failures)
                , config.MAX_BACKOFF)
                url.next_check_at = now + timedelta(seconds=backoff_seconds)
            session.commit()
        finally:
            logger.info(f"Releasing lock on {url.url}")
            self.release_lock(session, url)
    
    def run_once(self):
        with self.SessionLocal() as session:
            urls = self.get_due_urls(session)
            for url in urls:
                try:
                    self.check_single_url(session, url)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    logger.error(f"Failed while processing {url.url}: {str(e)}")
                
        
    def run(self):
        self.running = True
        while self.running:
            logger.info(f"{self.scheduler_id} is running")
            self.run_once()
            logger.info(f"{self.scheduler_id} taking a break")
            time.sleep(config.LOOP_INTERVAL)
        


def main():
    scheduler = Scheduler()

    try:
        logger.info(f"Starting scheduler {scheduler.scheduler_id}")
        scheduler.run()
    except KeyboardInterrupt as e:
        scheduler.running = False
        logger.info(f"Stopping scheduler {scheduler.scheduler_id}")


if __name__ == '__main__':
    main()
