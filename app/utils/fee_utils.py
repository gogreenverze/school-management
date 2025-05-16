"""
Fee utility functions for fee calculations, schedule generation, and reminders.
"""
import logging
import os
from datetime import datetime, timedelta, date
from app import db
from app.models.finance import (
    FeeSchedule, StudentFeeStructure, FeeReminder, FeePayment,
    SportFeeSchedule, TransportationFeeSchedule,
    Invoice, InvoiceItem, InvoicePayment,
    STATUS_PENDING, STATUS_COMPLETED, STATUS_OVERDUE,
    INVOICE_STATUS_DRAFT, INVOICE_STATUS_SENT, INVOICE_STATUS_PAID,
    INVOICE_STATUS_PARTIALLY_PAID, INVOICE_STATUS_OVERDUE, INVOICE_STATUS_CANCELLED,
    INVOICE_TYPE_TUITION, INVOICE_TYPE_SPORTS, INVOICE_TYPE_TRANSPORTATION, INVOICE_TYPE_COMBINED
)
from app.models.user import StudentProfile
from app.models.academic import Notification
from app.utils.whatsapp import send_fee_reminder, send_overdue_reminder
from app.utils.email import send_fee_reminder_email, send_invoice_email
from app.utils.pdf_utils import generate_invoice_pdf
from sqlalchemy import and_

# Configure logging
logger = logging.getLogger(__name__)

def generate_fee_schedules(student_fee_structure):
    """Generate fee schedules for a student fee structure

    Args:
        student_fee_structure: StudentFeeStructure object

    Returns:
        list: List of created FeeSchedule objects
    """
    base_structure = student_fee_structure.base_structure
    frequency = base_structure.frequency
    installments = student_fee_structure.installments
    effective_amount = student_fee_structure.effective_amount

    # Delete any existing pending schedules
    FeeSchedule.query.filter_by(
        student_fee_structure_id=student_fee_structure.id,
        status=STATUS_PENDING
    ).delete()

    # Calculate installment amount
    installment_amount = round(effective_amount / installments, 2)

    # Generate schedules based on frequency and installments
    schedules = []
    due_date = student_fee_structure.effective_due_date or date.today()

    for i in range(1, installments + 1):
        # Calculate due date based on frequency and installment number
        if i > 1:
            if frequency == 'monthly':
                due_date = add_months(due_date, 1)
            elif frequency == 'quarterly':
                due_date = add_months(due_date, 3)
            elif frequency == 'semi_annually':
                due_date = add_months(due_date, 6)
            elif frequency == 'annually':
                due_date = add_months(due_date, 12)

        # Create fee schedule
        schedule = FeeSchedule(
            student_fee_structure_id=student_fee_structure.id,
            installment_number=i,
            amount=installment_amount,
            due_date=due_date,
            status=STATUS_PENDING
        )
        db.session.add(schedule)
        schedules.append(schedule)

    db.session.commit()
    return schedules

def generate_sport_fee_schedules(student, sport, sport_fee):
    """Generate sport fee schedules for a student

    Args:
        student: StudentProfile object
        sport: Sport object
        sport_fee: SportFee object

    Returns:
        list: List of created SportFeeSchedule objects
    """
    frequency = sport_fee.frequency
    amount = sport_fee.amount

    # Delete any existing pending schedules
    SportFeeSchedule.query.filter_by(
        student_id=student.id,
        sport_id=sport.id,
        sport_fee_id=sport_fee.id,
        status=STATUS_PENDING
    ).delete()

    # Generate schedules based on frequency
    schedules = []
    due_date = date.today()

    # Determine number of installments based on duration
    installments = 1
    if sport_fee.duration:
        if frequency == 'monthly':
            installments = sport_fee.duration
        elif frequency == 'quarterly':
            installments = (sport_fee.duration + 2) // 3
        elif frequency == 'semi_annually':
            installments = (sport_fee.duration + 5) // 6
        elif frequency == 'annually':
            installments = (sport_fee.duration + 11) // 12

    for i in range(1, installments + 1):
        # Calculate due date based on frequency and installment number
        if i > 1:
            if frequency == 'monthly':
                due_date = add_months(due_date, 1)
            elif frequency == 'quarterly':
                due_date = add_months(due_date, 3)
            elif frequency == 'semi_annually':
                due_date = add_months(due_date, 6)
            elif frequency == 'annually':
                due_date = add_months(due_date, 12)

        # Create fee schedule
        schedule = SportFeeSchedule(
            student_id=student.id,
            sport_id=sport.id,
            sport_fee_id=sport_fee.id,
            installment_number=i,
            amount=amount,
            due_date=due_date,
            status=STATUS_PENDING
        )
        db.session.add(schedule)
        schedules.append(schedule)

    db.session.commit()
    return schedules

def generate_transportation_fee_schedules(student_transportation):
    """Generate transportation fee schedules for a student

    Args:
        student_transportation: StudentTransportation object

    Returns:
        list: List of created TransportationFeeSchedule objects
    """
    transportation_fee = student_transportation.transportation_fee
    frequency = transportation_fee.frequency
    effective_amount = student_transportation.effective_amount

    # Delete any existing pending schedules
    TransportationFeeSchedule.query.filter_by(
        student_transportation_id=student_transportation.id,
        status=STATUS_PENDING
    ).delete()

    # Generate schedules based on frequency
    schedules = []
    start_date = student_transportation.start_date
    end_date = student_transportation.end_date or add_months(start_date, 12)  # Default to 1 year if no end date

    # Calculate number of installments based on frequency and duration
    months_duration = months_between(start_date, end_date)

    installments = 1
    if frequency == 'monthly':
        installments = months_duration
    elif frequency == 'quarterly':
        installments = (months_duration + 2) // 3
    elif frequency == 'semi_annually':
        installments = (months_duration + 5) // 6
    elif frequency == 'annually':
        installments = (months_duration + 11) // 12

    due_date = start_date

    for i in range(1, installments + 1):
        # Calculate due date based on frequency and installment number
        if i > 1:
            if frequency == 'monthly':
                due_date = add_months(due_date, 1)
            elif frequency == 'quarterly':
                due_date = add_months(due_date, 3)
            elif frequency == 'semi_annually':
                due_date = add_months(due_date, 6)
            elif frequency == 'annually':
                due_date = add_months(due_date, 12)

        # Skip if due date is after end date
        if due_date > end_date:
            continue

        # Create fee schedule
        schedule = TransportationFeeSchedule(
            student_transportation_id=student_transportation.id,
            installment_number=i,
            amount=effective_amount,
            due_date=due_date,
            status=STATUS_PENDING
        )
        db.session.add(schedule)
        schedules.append(schedule)

    db.session.commit()
    return schedules

def send_fee_reminders(days_before=7, notification_types=None):
    """Send fee reminders for upcoming payments

    Args:
        days_before (int): Number of days before due date to send reminder
        notification_types (list): List of notification types to send (email, whatsapp, sms)

    Returns:
        int: Number of reminders sent
    """
    if notification_types is None:
        notification_types = ['email', 'whatsapp']

    today = date.today()
    reminder_date = today + timedelta(days=days_before)

    # Get all pending fee schedules due on reminder date
    schedules = FeeSchedule.query.filter(
        FeeSchedule.status == STATUS_PENDING,
        FeeSchedule.due_date == reminder_date
    ).all()

    reminders_sent = 0

    for schedule in schedules:
        student_fee = schedule.student_fee_structure
        student = student_fee.student

        # Create reminder record
        reminder = FeeReminder(
            student_id=student.id,
            fee_structure_id=student_fee.fee_structure_id,
            fee_schedule_id=schedule.id,
            due_date=schedule.due_date,
            amount_due=schedule.amount,
            reminder_type='upcoming',
            message=f"Fee payment of ₹{schedule.amount} is due on {schedule.due_date.strftime('%d-%m-%Y')}."
        )

        # Send notifications
        for notification_type in notification_types:
            reminder.notification_type = notification_type

            if notification_type == 'email':
                if student.parent_id and student.parent.user.email:
                    send_fee_reminder_email(student.parent.user, student, reminder)
                    reminder.sent = True
                    reminder.sent_date = datetime.utcnow()
                    reminders_sent += 1

            elif notification_type == 'whatsapp':
                if student.parent_id and student.parent.phone:
                    send_fee_reminder(student, schedule)
                    reminder.sent = True
                    reminder.sent_date = datetime.utcnow()
                    reminders_sent += 1

        # Create notification for student
        student_notification = Notification(
            user_id=student.user_id,
            title="Upcoming Fee Payment",
            message=f"Fee payment of ₹{schedule.amount} is due on {schedule.due_date.strftime('%d-%m-%Y')}.",
            category="fee",
            related_id=schedule.id
        )
        db.session.add(student_notification)

        db.session.add(reminder)

    db.session.commit()
    return reminders_sent

def send_overdue_reminders(notification_types=None):
    """Send reminders for overdue payments

    Args:
        notification_types (list): List of notification types to send (email, whatsapp, sms)

    Returns:
        int: Number of reminders sent
    """
    if notification_types is None:
        notification_types = ['email', 'whatsapp']

    today = date.today()

    # Get all overdue fee schedules
    schedules = FeeSchedule.query.filter(
        FeeSchedule.status == STATUS_PENDING,
        FeeSchedule.due_date < today
    ).all()

    reminders_sent = 0

    for schedule in schedules:
        student_fee = schedule.student_fee_structure
        student = student_fee.student
        days_overdue = (today - schedule.due_date).days

        # Check if a reminder was sent in the last 7 days
        recent_reminder = FeeReminder.query.filter(
            FeeReminder.student_id == student.id,
            FeeReminder.fee_schedule_id == schedule.id,
            FeeReminder.reminder_type == 'overdue',
            FeeReminder.sent_date > (datetime.utcnow() - timedelta(days=7))
        ).first()

        if recent_reminder:
            continue

        # Create reminder record
        reminder = FeeReminder(
            student_id=student.id,
            fee_structure_id=student_fee.fee_structure_id,
            fee_schedule_id=schedule.id,
            due_date=schedule.due_date,
            amount_due=schedule.amount,
            reminder_type='overdue',
            message=f"Fee payment of ₹{schedule.amount} was due on {schedule.due_date.strftime('%d-%m-%Y')} and is now {days_overdue} days overdue."
        )

        # Send notifications
        for notification_type in notification_types:
            reminder.notification_type = notification_type

            if notification_type == 'email':
                if student.parent_id and student.parent_profile and student.parent_profile.user.email:
                    send_fee_reminder_email(student.parent_profile.user, student, reminder)
                    reminder.sent = True
                    reminder.sent_date = datetime.utcnow()
                    reminders_sent += 1

            elif notification_type == 'whatsapp':
                if student.parent_id and student.parent_profile and student.parent_profile.phone:
                    send_overdue_reminder(student, schedule, days_overdue)
                    reminder.sent = True
                    reminder.sent_date = datetime.utcnow()
                    reminders_sent += 1

        # Create notification for student
        student_notification = Notification(
            user_id=student.user_id,
            title="Overdue Fee Payment",
            message=f"Fee payment of ₹{schedule.amount} was due on {schedule.due_date.strftime('%d-%m-%Y')} and is now {days_overdue} days overdue.",
            category="fee",
            related_id=schedule.id
        )
        db.session.add(student_notification)

        db.session.add(reminder)

    db.session.commit()
    return reminders_sent

def add_months(source_date, months):
    """Add months to a date

    Args:
        source_date (date): Source date
        months (int): Number of months to add

    Returns:
        date: New date with months added
    """
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return date(year, month, day)

def months_between(start_date, end_date):
    """Calculate number of months between two dates

    Args:
        start_date (date): Start date
        end_date (date): End date

    Returns:
        int: Number of months
    """
    return (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
