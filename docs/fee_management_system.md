# Fee Management System

The Fee Management System is a comprehensive solution for managing school fees, including tuition, sports, and transportation fees. It provides features for creating fee structures, assigning fees to students, generating payment schedules, collecting payments, and sending reminders.

## Features

- **Fee Categories**: Create and manage different types of fees (tuition, sports, transportation, etc.)
- **Fee Structures**: Define fee structures with amounts, frequencies, and due dates
- **Student Fee Assignment**: Assign fee structures to students with customization options
- **Fee Schedules**: Generate payment schedules based on fee structures and frequencies
- **Payment Collection**: Record fee payments with receipts and track payment status
- **Transportation Fees**: Manage transportation routes, fees, and student enrollments
- **Reminders**: Send automated reminders for upcoming and overdue payments
- **WhatsApp Integration**: Send fee reminders and payment confirmations via WhatsApp

## Setup

### Database Migration

After deploying the code, run the migration script to create the necessary database tables:

```bash
python migrations/fee_system_upgrade.py
```

### WhatsApp Integration

To enable WhatsApp integration, you need to set up a WhatsApp Business API account and configure the following environment variables:

```
WHATSAPP_API_KEY=your_api_key
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_API_VERSION=v17.0
```

## Usage Guide

### Fee Categories

1. Go to Admin Dashboard > Fee Management > Fee Categories
2. Create categories for different types of fees (tuition, sports, transportation, etc.)
3. Specify whether the fee is recurring and its frequency

### Fee Structures

1. Go to Admin Dashboard > Fee Management > Fee Structures
2. Create fee structures for different standards/grades
3. Specify the amount, frequency, due date, and late fee details

### Student Fee Assignment

1. Go to Admin Dashboard > Fee Management > Student Fees
2. Assign fee structures to students
3. Customize amounts, discounts, and installments if needed
4. Fee schedules will be automatically generated based on the assignment

### Payment Collection

1. Go to Admin Dashboard > Fee Management > Payments
2. Record payments for students
3. Select the fee structure and schedule
4. Specify the amount, payment method, and other details
5. A receipt will be generated and notifications will be sent to the student and parent

### Transportation Fees

1. Go to Admin Dashboard > Fee Management > Transportation
2. Create transportation routes with fees
3. Enroll students in transportation services
4. Fee schedules will be automatically generated

### Reminders

1. Go to Admin Dashboard > Fee Management > Reminders
2. Configure reminder settings
3. Send reminders manually or let the system send them automatically
4. View reminder history

## Fee Schedule Generation

Fee schedules are generated based on the following rules:

1. **Frequency**: Determines how often payments are due (monthly, quarterly, semi-annually, annually)
2. **Installments**: Divides the total amount into multiple installments
3. **Due Date**: The date by which the payment should be made
4. **Late Fee**: Additional amount charged if payment is made after the due date

## WhatsApp Notifications

The system can send the following types of WhatsApp notifications:

1. **Fee Reminders**: Sent before the due date to remind about upcoming payments
2. **Overdue Reminders**: Sent after the due date to remind about overdue payments
3. **Payment Confirmations**: Sent after a payment is recorded to confirm receipt

## Reporting

The system provides the following reports:

1. **Fee Collection Summary**: Summary of fees collected by category, standard, etc.
2. **Outstanding Dues**: List of students with outstanding dues
3. **Payment History**: History of payments made by a student
4. **Reminder History**: History of reminders sent to students/parents

## Troubleshooting

### WhatsApp Integration Issues

If WhatsApp notifications are not being sent:

1. Check that the WhatsApp API credentials are correctly configured
2. Verify that the phone numbers are in the correct format (with country code)
3. Check the logs for any error messages

### Fee Schedule Issues

If fee schedules are not being generated correctly:

1. Check that the fee structure has a valid frequency and due date
2. Verify that the student fee assignment has the correct number of installments
3. Try regenerating the schedules from the student fee details page
