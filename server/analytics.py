from sqlalchemy.orm import Session
from models import ActivityLog
from datetime import datetime

def log_user_activity(db: Session, user_id: int, action: str, details: str = None):
    log = ActivityLog(user_id=user_id, action=action, details=details)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def generate_activity_report(db: Session, start_date: datetime, end_date: datetime):
    logs = db.query(ActivityLog).filter(
        ActivityLog.timestamp >= start_date,
        ActivityLog.timestamp <= end_date
    ).all()

    report = {}
    for log in logs:
        user_id = log.user_id
        if user_id not in report:
            report[user_id] = []
        report[user_id].append({
            "action": log.action,
            "timestamp": log.timestamp,
            "details": log.details,
        })
    return report