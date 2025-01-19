from typing import Callable, Any
from datetime import datetime
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

logger = logging.getLogger(__name__)

class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        
    async def start(self):
        try:
            self.scheduler.start()
            logger.info("Scheduler started successfully")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise

    def schedule_interval_task(
        self,
        task: Callable,
        seconds: int = None,
        minutes: int = None,
        hours: int = None,
        task_id: str = None,
        **kwargs: Any
    ):
        """Schedule a task to run at fixed intervals."""
        try:
            # Validate that at least one time parameter is provided
            if all(param is None for param in [seconds, minutes, hours]):
                raise ValueError("At least one interval parameter (seconds, minutes, or hours) must be specified")
            
            # Convert None values to 0 for the IntervalTrigger
            seconds = seconds or 0
            minutes = minutes or 0
            hours = hours or 0
            
            job_id = task_id or f"{task.__name__}_{datetime.utcnow().timestamp()}"
            self.scheduler.add_job(
                task,
                trigger=IntervalTrigger(
                    seconds=seconds,
                    minutes=minutes,
                    hours=hours
                ),
                id=job_id,
                replace_existing=True,
                **kwargs
            )
            logger.info(f"Scheduled interval task: {job_id}")
            return job_id
        except Exception as e:
            logger.error(f"Failed to schedule interval task: {e}")
            raise 