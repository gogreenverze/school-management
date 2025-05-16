"""
Scheduler utility for running periodic tasks like sending fee reminders.
"""
import logging
import threading
import time
import atexit
from datetime import datetime, timedelta
from app import create_app
from app.utils.fee_utils import send_fee_reminders, send_overdue_reminders

# Configure logging
logger = logging.getLogger(__name__)

class SchedulerThread(threading.Thread):
    """Thread for running scheduled tasks"""
    
    def __init__(self, app=None):
        """Initialize scheduler thread
        
        Args:
            app: Flask application instance
        """
        super().__init__()
        self.daemon = True
        self.app = app or create_app()
        self.stop_event = threading.Event()
        self.tasks = []
        
        # Register default tasks
        self.register_task(self.send_upcoming_fee_reminders, 86400)  # Daily
        self.register_task(self.send_overdue_fee_reminders, 86400)  # Daily
        
        # Register exit handler
        atexit.register(self.shutdown)
    
    def register_task(self, task_func, interval, last_run=None):
        """Register a task to be run periodically
        
        Args:
            task_func (callable): Function to run
            interval (int): Interval in seconds
            last_run (datetime, optional): Last run time. If None, will run immediately.
        """
        self.tasks.append({
            'func': task_func,
            'interval': interval,
            'last_run': last_run or (datetime.now() - timedelta(days=1))
        })
    
    def run(self):
        """Run the scheduler thread"""
        logger.info("Scheduler thread started")
        
        while not self.stop_event.is_set():
            now = datetime.now()
            
            for task in self.tasks:
                # Check if task should run
                if (now - task['last_run']).total_seconds() >= task['interval']:
                    try:
                        with self.app.app_context():
                            task['func']()
                        task['last_run'] = now
                        logger.info(f"Task {task['func'].__name__} completed successfully")
                    except Exception as e:
                        logger.error(f"Error running task {task['func'].__name__}: {str(e)}")
            
            # Sleep for a minute before checking again
            time.sleep(60)
    
    def shutdown(self):
        """Shutdown the scheduler thread"""
        logger.info("Shutting down scheduler thread")
        self.stop_event.set()
    
    def send_upcoming_fee_reminders(self):
        """Send reminders for upcoming fee payments"""
        logger.info("Sending upcoming fee reminders")
        
        # Send reminders for payments due in 7 days
        count_7_days = send_fee_reminders(days_before=7)
        logger.info(f"Sent {count_7_days} reminders for payments due in 7 days")
        
        # Send reminders for payments due in 3 days
        count_3_days = send_fee_reminders(days_before=3)
        logger.info(f"Sent {count_3_days} reminders for payments due in 3 days")
        
        # Send reminders for payments due tomorrow
        count_1_day = send_fee_reminders(days_before=1)
        logger.info(f"Sent {count_1_day} reminders for payments due tomorrow")
        
        return count_7_days + count_3_days + count_1_day
    
    def send_overdue_fee_reminders(self):
        """Send reminders for overdue fee payments"""
        logger.info("Sending overdue fee reminders")
        
        count = send_overdue_reminders()
        logger.info(f"Sent {count} reminders for overdue payments")
        
        return count

def start_scheduler(app=None):
    """Start the scheduler thread
    
    Args:
        app: Flask application instance
        
    Returns:
        SchedulerThread: Scheduler thread instance
    """
    scheduler = SchedulerThread(app)
    scheduler.start()
    return scheduler
