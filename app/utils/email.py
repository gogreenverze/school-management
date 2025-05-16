from flask import current_app, render_template
from flask_mail import Message
from app import mail
from threading import Thread
import os

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
    # Ensure reminder_date is set
    from datetime import datetime, date
    if not fee_reminder.reminder_date:
        fee_reminder.reminder_date = datetime.utcnow()

    # Calculate days overdue if not already set
    if not hasattr(fee_reminder, 'days_overdue'):
        today = date.today()
        fee_reminder.days_overdue = (today - fee_reminder.due_date).days

    send_email(
        f'Fee Payment Reminder for {student.user.get_full_name()}',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template('email/fee_reminder.txt', user=user, student=student, reminder=fee_reminder),
        html_body=render_template('email/fee_reminder.html', user=user, student=student, reminder=fee_reminder)
    )

def send_invoice_email(user, student, invoice, pdf_path=None):
    """Send an invoice email with optional PDF attachment

    Args:
        user: User object (recipient)
        student: StudentProfile object
        invoice: Invoice object
        pdf_path: Path to the invoice PDF file (optional)
    """
    msg = Message(
        f'Invoice #{invoice.invoice_number} for {student.user.get_full_name()}',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email]
    )

    msg.body = render_template('email/invoice.txt', user=user, student=student, invoice=invoice)
    msg.html = render_template('email/invoice.html', user=user, student=student, invoice=invoice)

    # Attach PDF if provided
    if pdf_path and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], pdf_path)):
        with open(os.path.join(current_app.config['UPLOAD_FOLDER'], pdf_path), 'rb') as f:
            msg.attach(
                f"Invoice_{invoice.invoice_number}.pdf",
                'application/pdf',
                f.read()
            )

    # Send email asynchronously
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
