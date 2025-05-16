"""
WhatsApp integration utility for sending notifications.
This module provides functions to send WhatsApp messages using the WhatsApp Business API.
"""
import os
import json
import requests
import logging
from datetime import datetime
from flask import current_app, render_template
from threading import Thread
from sqlalchemy.exc import OperationalError

# Configure logging
logger = logging.getLogger(__name__)

# WhatsApp message types
MESSAGE_TYPE_TEXT = 'text'
MESSAGE_TYPE_TEMPLATE = 'template'
MESSAGE_TYPE_MEDIA = 'media'

# WhatsApp template types
TEMPLATE_TYPE_FEE_REMINDER = 'fee_reminder'
TEMPLATE_TYPE_FEE_RECEIPT = 'fee_receipt'
TEMPLATE_TYPE_FEE_OVERDUE = 'fee_overdue'
TEMPLATE_TYPE_PAYMENT_CONFIRMATION = 'payment_confirmation'

class WhatsAppClient:
    """WhatsApp Business API client for sending messages"""

    def __init__(self, api_key=None, phone_number_id=None, version=None):
        """Initialize WhatsApp client with API credentials"""
        # Try to get config from database if not provided
        if not api_key or not phone_number_id:
            try:
                # Import here to avoid circular imports
                from app.models.settings import WhatsAppConfig
                config = WhatsAppConfig.get_active_config()
                if config:
                    api_key = api_key or config.api_key
                    phone_number_id = phone_number_id or config.phone_number_id
                    version = version or config.api_version
            except (ImportError, OperationalError):
                # Fall back to environment variables if database is not available
                logger.warning("Could not get WhatsApp config from database, falling back to environment variables")

        # Fall back to environment variables if still not set
        self.api_key = api_key or os.environ.get('WHATSAPP_API_KEY')
        self.phone_number_id = phone_number_id or os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
        self.version = version or os.environ.get('WHATSAPP_API_VERSION', 'v17.0')
        self.base_url = f"https://graph.facebook.com/{self.version}/{self.phone_number_id}/messages"

        if not self.api_key or not self.phone_number_id:
            logger.warning("WhatsApp API credentials not configured. Messages will not be sent.")

    def send_message(self, to, message_type, message_content):
        """Send a WhatsApp message

        Args:
            to (str): Recipient's phone number with country code (e.g., "919876543210")
            message_type (str): Type of message (text, template, media)
            message_content (dict): Content of the message based on type

        Returns:
            dict: Response from WhatsApp API
        """
        if not self.api_key or not self.phone_number_id:
            logger.warning("WhatsApp API credentials not configured. Message not sent.")
            return {"error": "WhatsApp API credentials not configured"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": message_type
        }

        # Add message content based on type
        if message_type == MESSAGE_TYPE_TEXT:
            payload["text"] = {"body": message_content}
        elif message_type == MESSAGE_TYPE_TEMPLATE:
            payload["template"] = message_content
        elif message_type == MESSAGE_TYPE_MEDIA:
            payload["media"] = message_content

        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response_data = response.json()

            if response.status_code != 200:
                logger.error(f"Failed to send WhatsApp message: {response_data}")
                return {"error": response_data}

            logger.info(f"WhatsApp message sent successfully: {response_data}")
            return response_data

        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return {"error": str(e)}

def send_whatsapp_async(app, client, to, message_type, message_content):
    """Send WhatsApp message asynchronously"""
    with app.app_context():
        client.send_message(to, message_type, message_content)

def send_whatsapp_message(to, message_type, message_content):
    """Send a WhatsApp message asynchronously

    Args:
        to (str): Recipient's phone number with country code (e.g., "919876543210")
        message_type (str): Type of message (text, template, media)
        message_content (dict): Content of the message based on type
    """
    client = WhatsAppClient()
    Thread(
        target=send_whatsapp_async,
        args=(current_app._get_current_object(), client, to, message_type, message_content)
    ).start()

def format_phone_number(phone):
    """Format phone number for WhatsApp API (remove spaces, dashes, etc.)

    Args:
        phone (str): Phone number to format

    Returns:
        str: Formatted phone number
    """
    # Remove all non-numeric characters
    phone = ''.join(filter(str.isdigit, phone))

    # Ensure it starts with country code (default to India +91)
    if not phone.startswith('91') and len(phone) == 10:
        phone = '91' + phone

    return phone

def send_fee_reminder(student, fee_schedule, message=None):
    """Send fee reminder via WhatsApp

    Args:
        student: StudentProfile object
        fee_schedule: FeeSchedule object
        message (str, optional): Custom message. If None, a default message is used.
    """
    # Get parent's phone number
    if not student.parent_id or not student.parent_profile or not student.parent_profile.phone:
        logger.warning(f"Cannot send WhatsApp reminder: No parent phone for student {student.id}")
        return False

    phone = format_phone_number(student.parent_profile.phone)

    # Prepare template parameters
    student_name = f"{student.user.first_name} {student.user.last_name}"
    amount = fee_schedule.amount
    due_date = fee_schedule.due_date.strftime("%d-%m-%Y")

    # Default message if none provided
    if not message:
        message = f"Fee reminder for {student_name}: ₹{amount} due on {due_date}. Please make the payment before the due date to avoid late fees."

    # Send template message
    template_content = {
        "name": "fee_reminder",
        "language": {"code": "en"},
        "components": [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": student_name},
                    {"type": "text", "text": f"₹{amount}"},
                    {"type": "text", "text": due_date}
                ]
            }
        ]
    }

    # Send message
    return send_whatsapp_message(phone, MESSAGE_TYPE_TEMPLATE, template_content)

def send_payment_confirmation(student, payment):
    """Send payment confirmation via WhatsApp

    Args:
        student: StudentProfile object
        payment: FeePayment object
    """
    # Get parent's phone number
    if not student.parent_id or not student.parent_profile or not student.parent_profile.phone:
        logger.warning(f"Cannot send WhatsApp confirmation: No parent phone for student {student.id}")
        return False

    phone = format_phone_number(student.parent_profile.phone)

    # Prepare template parameters
    student_name = f"{student.user.first_name} {student.user.last_name}"
    amount = payment.amount_paid
    receipt_number = payment.receipt_number
    payment_date = payment.payment_date.strftime("%d-%m-%Y")

    # Send template message
    template_content = {
        "name": "payment_confirmation",
        "language": {"code": "en"},
        "components": [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": student_name},
                    {"type": "text", "text": f"₹{amount}"},
                    {"type": "text", "text": receipt_number},
                    {"type": "text", "text": payment_date}
                ]
            }
        ]
    }

    # Send message
    return send_whatsapp_message(phone, MESSAGE_TYPE_TEMPLATE, template_content)

def send_overdue_reminder(student, fee_schedule, days_overdue):
    """Send overdue fee reminder via WhatsApp

    Args:
        student: StudentProfile object
        fee_schedule: FeeSchedule object
        days_overdue (int): Number of days the payment is overdue
    """
    # Get parent's phone number
    if not student.parent_id or not student.parent_profile or not student.parent_profile.phone:
        logger.warning(f"Cannot send WhatsApp overdue reminder: No parent phone for student {student.id}")
        return False

    phone = format_phone_number(student.parent_profile.phone)

    # Prepare template parameters
    student_name = f"{student.user.first_name} {student.user.last_name}"
    amount = fee_schedule.amount
    due_date = fee_schedule.due_date.strftime("%d-%m-%Y")

    # Send template message
    template_content = {
        "name": "fee_overdue",
        "language": {"code": "en"},
        "components": [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": student_name},
                    {"type": "text", "text": f"₹{amount}"},
                    {"type": "text", "text": due_date},
                    {"type": "text", "text": str(days_overdue)}
                ]
            }
        ]
    }

    # Send message
    return send_whatsapp_message(phone, MESSAGE_TYPE_TEMPLATE, template_content)
