from flask import current_app, render_template
from flask_mail import Message
from app import mail
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    
    # Send email asynchronously
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(
        'Reset Your Password',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt', user=user, token=token),
        html_body=render_template('email/reset_password.html', user=user, token=token)
    )

def send_notification_email(user, notification):
    send_email(
        notification.title,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template('email/notification.txt', user=user, notification=notification),
        html_body=render_template('email/notification.html', user=user, notification=notification)
    )

def send_fee_reminder_email(user, student, fee_reminder):
    send_email(
        f'Fee Payment Reminder for {student.user.get_full_name()}',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template('email/fee_reminder.txt', user=user, student=student, reminder=fee_reminder),
        html_body=render_template('email/fee_reminder.html', user=user, student=student, reminder=fee_reminder)
    )
