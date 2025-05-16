from app import create_app, db
from app.utils.fee_utils import send_overdue_reminders
from app.models.academic import Notification
from app.models.user import User, StudentProfile

app = create_app()
with app.app_context():
    # Send overdue reminders
    notification_types = ['email', 'whatsapp']
    reminders_sent = send_overdue_reminders(notification_types)
    
    print(f"Sent {reminders_sent} overdue reminders")
    
    # Check notifications for Bharath Ramachandran
    username = 'bharath.ramachandran111923'
    user = User.query.filter_by(username=username).first()
    
    if not user:
        print(f"User with username {username} not found.")
        exit(1)
    
    # Get notifications for the user
    notifications = Notification.query.filter_by(
        user_id=user.id,
        category='fee'
    ).order_by(Notification.created_at.desc()).all()
    
    print(f"\nFound {len(notifications)} fee notifications for {user.first_name} {user.last_name}:")
    
    for i, notification in enumerate(notifications, 1):
        print(f"\n{i}. {notification.title}")
        print(f"   Message: {notification.message}")
        print(f"   Created at: {notification.created_at.strftime('%d-%m-%Y %H:%M:%S')}")
        print(f"   Is read: {notification.is_read}")
    
    print("\nReminder process complete.")
