"""
Routes for admin settings.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from datetime import datetime

from app import db
from app.models.settings import WhatsAppConfig
from app.forms.settings import WhatsAppConfigForm
from app.utils.decorators import admin_required
from app.utils.whatsapp import WhatsAppClient, MESSAGE_TYPE_TEXT

admin_settings_bp = Blueprint('admin_settings', __name__, url_prefix='/admin_settings')

@admin_settings_bp.route('/whatsapp', methods=['GET', 'POST'])
@login_required
@admin_required
def whatsapp_config():
    """WhatsApp configuration page"""
    # Get existing config or create new one
    config = WhatsAppConfig.query.first()
    if not config:
        config = WhatsAppConfig()
        db.session.add(config)
        db.session.commit()
    
    form = WhatsAppConfigForm(obj=config)
    
    if form.validate_on_submit():
        # Update configuration
        form.populate_obj(config)
        config.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('WhatsApp configuration updated successfully!', 'success')
        return redirect(url_for('admin_settings.whatsapp_config'))
    
    return render_template('admin/settings/whatsapp_config.html', 
                          title='WhatsApp Configuration',
                          form=form,
                          config=config)

@admin_settings_bp.route('/whatsapp/test', methods=['POST'])
@login_required
@admin_required
def test_whatsapp():
    """Test WhatsApp configuration"""
    config = WhatsAppConfig.query.first()
    if not config:
        flash('WhatsApp configuration not found!', 'danger')
        return redirect(url_for('admin_settings.whatsapp_config'))
    
    form = WhatsAppConfigForm()
    
    if form.validate_on_submit():
        test_phone = form.test_phone.data
        
        if not test_phone:
            flash('Please enter a phone number to send test message!', 'warning')
            return redirect(url_for('admin_settings.whatsapp_config'))
        
        # Create WhatsApp client with current configuration
        client = WhatsAppClient(
            api_key=config.api_key,
            phone_number_id=config.phone_number_id,
            version=config.api_version
        )
        
        # Send test message
        test_message = f"This is a test message from {config.business_name} School Management System. If you received this message, WhatsApp integration is working correctly."
        
        try:
            response = client.send_message(test_phone, MESSAGE_TYPE_TEXT, test_message)
            
            if 'error' in response:
                config.last_test_status = False
                config.last_test_message = f"Error: {response['error']}"
                flash(f"Test failed: {response['error']}", 'danger')
            else:
                config.last_test_status = True
                config.last_test_message = "Test message sent successfully!"
                flash("Test message sent successfully!", 'success')
        except Exception as e:
            config.last_test_status = False
            config.last_test_message = f"Error: {str(e)}"
            flash(f"Test failed: {str(e)}", 'danger')
        
        config.last_test_date = datetime.utcnow()
        db.session.commit()
        
    return redirect(url_for('admin_settings.whatsapp_config'))
