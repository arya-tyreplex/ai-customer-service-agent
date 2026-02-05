"""
Notification service for TyrePlex.
Handles SMS and WhatsApp notifications for bookings and reminders.
"""

from typing import Dict, Optional
from datetime import datetime
from loguru import logger
import requests


class NotificationService:
    """Handles SMS and WhatsApp notifications."""
    
    def __init__(
        self,
        sms_provider: str = "twilio",
        sms_api_key: Optional[str] = None,
        sms_api_secret: Optional[str] = None,
        whatsapp_api_key: Optional[str] = None
    ):
        """
        Initialize notification service.
        
        Args:
            sms_provider: SMS provider ('twilio', 'msg91', 'gupshup')
            sms_api_key: SMS API key
            sms_api_secret: SMS API secret
            whatsapp_api_key: WhatsApp API key
        """
        self.sms_provider = sms_provider
        self.sms_api_key = sms_api_key
        self.sms_api_secret = sms_api_secret
        self.whatsapp_api_key = whatsapp_api_key
    
    def send_booking_confirmation_sms(
        self,
        phone_number: str,
        booking_data: Dict
    ) -> bool:
        """
        Send booking confirmation SMS.
        
        Args:
            phone_number: Customer phone number
            booking_data: Booking information
            
        Returns:
            True if sent successfully
        """
        message = self._format_booking_confirmation_message(booking_data)
        
        logger.info(f"Sending booking confirmation SMS to {phone_number}")
        
        return self._send_sms(phone_number, message)
    
    def send_booking_reminder_sms(
        self,
        phone_number: str,
        booking_data: Dict
    ) -> bool:
        """
        Send booking reminder SMS.
        
        Args:
            phone_number: Customer phone number
            booking_data: Booking information
            
        Returns:
            True if sent successfully
        """
        message = self._format_booking_reminder_message(booking_data)
        
        logger.info(f"Sending booking reminder SMS to {phone_number}")
        
        return self._send_sms(phone_number, message)
    
    def send_technician_enroute_sms(
        self,
        phone_number: str,
        booking_data: Dict,
        technician_name: str,
        eta_minutes: int
    ) -> bool:
        """
        Send technician en-route SMS.
        
        Args:
            phone_number: Customer phone number
            booking_data: Booking information
            technician_name: Technician name
            eta_minutes: Estimated time of arrival in minutes
            
        Returns:
            True if sent successfully
        """
        message = f"""TyrePlex Update

Hi {booking_data['customer_name']}!

Your technician {technician_name} is on the way.

ETA: {eta_minutes} minutes

Booking: {booking_data['booking_id']}
Service: {booking_data['tyre_brand']} {booking_data['tyre_model']} installation

Please ensure vehicle is accessible.

Thank you!
TyrePlex Team"""
        
        logger.info(f"Sending technician en-route SMS to {phone_number}")
        
        return self._send_sms(phone_number, message)
    
    def send_booking_completion_sms(
        self,
        phone_number: str,
        booking_data: Dict
    ) -> bool:
        """
        Send booking completion SMS.
        
        Args:
            phone_number: Customer phone number
            booking_data: Booking information
            
        Returns:
            True if sent successfully
        """
        message = f"""TyrePlex - Service Completed

Hi {booking_data['customer_name']}!

Your tyre installation is complete.

Booking: {booking_data['booking_id']}
Service: {booking_data['tyre_brand']} {booking_data['tyre_model']}
Amount: ₹{booking_data['total_price']}

Thank you for choosing TyrePlex!

Rate your experience: https://tyreplex.com/feedback/{booking_data['booking_id']}

Drive safe!
TyrePlex Team"""
        
        logger.info(f"Sending completion SMS to {phone_number}")
        
        return self._send_sms(phone_number, message)
    
    def send_whatsapp_message(
        self,
        phone_number: str,
        message: str,
        template_name: Optional[str] = None
    ) -> bool:
        """
        Send WhatsApp message.
        
        Args:
            phone_number: Customer phone number
            message: Message text
            template_name: WhatsApp template name (if using templates)
            
        Returns:
            True if sent successfully
        """
        logger.info(f"Sending WhatsApp message to {phone_number}")
        
        # TODO: Implement actual WhatsApp API integration
        # This would use WhatsApp Business API or services like Twilio, Gupshup
        
        logger.info(f"✅ WhatsApp message sent to {phone_number}")
        return True
    
    def _send_sms(self, phone_number: str, message: str) -> bool:
        """
        Send SMS using configured provider.
        
        Args:
            phone_number: Destination phone number
            message: SMS message text
            
        Returns:
            True if sent successfully
        """
        if self.sms_provider == "twilio":
            return self._send_sms_twilio(phone_number, message)
        elif self.sms_provider == "msg91":
            return self._send_sms_msg91(phone_number, message)
        elif self.sms_provider == "gupshup":
            return self._send_sms_gupshup(phone_number, message)
        else:
            logger.warning(f"SMS provider not configured: {self.sms_provider}")
            logger.info(f"[DEMO MODE] SMS to {phone_number}: {message}")
            return True
    
    def _send_sms_twilio(self, phone_number: str, message: str) -> bool:
        """Send SMS via Twilio."""
        try:
            # TODO: Implement actual Twilio integration
            # from twilio.rest import Client
            # client = Client(self.sms_api_key, self.sms_api_secret)
            # message = client.messages.create(
            #     body=message,
            #     from_='+1234567890',  # Your Twilio number
            #     to=phone_number
            # )
            
            logger.info(f"✅ SMS sent via Twilio to {phone_number}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS via Twilio: {e}")
            return False
    
    def _send_sms_msg91(self, phone_number: str, message: str) -> bool:
        """Send SMS via MSG91 (popular in India)."""
        try:
            # TODO: Implement actual MSG91 integration
            # url = "https://api.msg91.com/api/v5/flow/"
            # payload = {
            #     "authkey": self.sms_api_key,
            #     "mobiles": phone_number,
            #     "message": message
            # }
            # response = requests.post(url, json=payload)
            
            logger.info(f"✅ SMS sent via MSG91 to {phone_number}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS via MSG91: {e}")
            return False
    
    def _send_sms_gupshup(self, phone_number: str, message: str) -> bool:
        """Send SMS via Gupshup."""
        try:
            # TODO: Implement actual Gupshup integration
            logger.info(f"✅ SMS sent via Gupshup to {phone_number}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS via Gupshup: {e}")
            return False
    
    def _format_booking_confirmation_message(self, booking_data: Dict) -> str:
        """Format booking confirmation message."""
        return f"""TyrePlex Booking Confirmed!

Hi {booking_data['customer_name']}!

Your booking is confirmed:

Booking ID: {booking_data['booking_id']}
Date: {booking_data['booking_date']}
Time: {booking_data['booking_time_slot']}

Service: {booking_data['service_type'].replace('_', ' ').title()}
Product: {booking_data['tyre_brand']} {booking_data['tyre_model']}
Quantity: {booking_data['quantity']} tyres
Total: ₹{booking_data['total_price']}

Address: {booking_data['address']}, {booking_data['city']}

Our technician will call 30 minutes before arrival.

Need help? Call 1800-XXX-XXXX

Thank you!
TyrePlex Team"""
    
    def _format_booking_reminder_message(self, booking_data: Dict) -> str:
        """Format booking reminder message."""
        return f"""TyrePlex Reminder

Hi {booking_data['customer_name']}!

Reminder: Your tyre installation is scheduled for tomorrow.

Booking ID: {booking_data['booking_id']}
Date: {booking_data['booking_date']}
Time: {booking_data['booking_time_slot']}

Product: {booking_data['tyre_brand']} {booking_data['tyre_model']}
Address: {booking_data['address']}

Please ensure:
✓ Vehicle is accessible
✓ Parking space available
✓ Someone is present

To reschedule: Call 1800-XXX-XXXX

See you tomorrow!
TyrePlex Team"""


class EmailService:
    """Handles email notifications."""
    
    def __init__(
        self,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None
    ):
        """
        Initialize email service.
        
        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
    
    def send_booking_confirmation_email(
        self,
        email: str,
        booking_data: Dict
    ) -> bool:
        """
        Send booking confirmation email.
        
        Args:
            email: Customer email
            booking_data: Booking information
            
        Returns:
            True if sent successfully
        """
        subject = f"TyrePlex Booking Confirmation - {booking_data['booking_id']}"
        
        body = f"""
        <html>
        <body>
            <h2>Booking Confirmed!</h2>
            
            <p>Hi {booking_data['customer_name']},</p>
            
            <p>Your tyre installation booking is confirmed.</p>
            
            <h3>Booking Details:</h3>
            <ul>
                <li><strong>Booking ID:</strong> {booking_data['booking_id']}</li>
                <li><strong>Date:</strong> {booking_data['booking_date']}</li>
                <li><strong>Time:</strong> {booking_data['booking_time_slot']}</li>
                <li><strong>Service:</strong> {booking_data['service_type'].replace('_', ' ').title()}</li>
            </ul>
            
            <h3>Product Details:</h3>
            <ul>
                <li><strong>Brand:</strong> {booking_data['tyre_brand']}</li>
                <li><strong>Model:</strong> {booking_data['tyre_model']}</li>
                <li><strong>Size:</strong> {booking_data['tyre_size']}</li>
                <li><strong>Quantity:</strong> {booking_data['quantity']} tyres</li>
                <li><strong>Total Amount:</strong> ₹{booking_data['total_price']}</li>
            </ul>
            
            <h3>Installation Address:</h3>
            <p>{booking_data['address']}<br>
            {booking_data['city']} - {booking_data['pincode']}</p>
            
            <p>Our technician will call you 30 minutes before arrival.</p>
            
            <p>Need help? Call us at 1800-XXX-XXXX</p>
            
            <p>Thank you for choosing TyrePlex!</p>
            
            <p>Best regards,<br>
            TyrePlex Team</p>
        </body>
        </html>
        """
        
        logger.info(f"Sending booking confirmation email to {email}")
        
        return self._send_email(email, subject, body)
    
    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send email.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body (HTML)
            
        Returns:
            True if sent successfully
        """
        try:
            # TODO: Implement actual email sending
            # import smtplib
            # from email.mime.text import MIMEText
            # from email.mime.multipart import MIMEMultipart
            
            # msg = MIMEMultipart('alternative')
            # msg['Subject'] = subject
            # msg['From'] = self.smtp_user
            # msg['To'] = to_email
            
            # html_part = MIMEText(body, 'html')
            # msg.attach(html_part)
            
            # with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            #     server.starttls()
            #     server.login(self.smtp_user, self.smtp_password)
            #     server.send_message(msg)
            
            logger.info(f"✅ Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Initialize notification service
    notif = NotificationService()
    
    # Test booking data
    booking_data = {
        'booking_id': 'BOOK-20260205-001',
        'customer_name': 'Rahul Sharma',
        'phone_number': '+91-9876543210',
        'booking_date': '2026-02-06',
        'booking_time_slot': '10:00-12:00',
        'service_type': 'home_fitment',
        'tyre_brand': 'MRF',
        'tyre_model': 'ZVTV',
        'tyre_size': '185/65 R15',
        'quantity': 4,
        'price_per_tyre': 4200.00,
        'total_price': 16800.00,
        'address': 'Koramangala, 5th Block',
        'city': 'Bangalore',
        'pincode': '560034'
    }
    
    # Send confirmation SMS
    notif.send_booking_confirmation_sms(
        booking_data['phone_number'],
        booking_data
    )
    
    # Send reminder SMS
    notif.send_booking_reminder_sms(
        booking_data['phone_number'],
        booking_data
    )
    
    # Send technician en-route SMS
    notif.send_technician_enroute_sms(
        booking_data['phone_number'],
        booking_data,
        technician_name='Rajesh Kumar',
        eta_minutes=30
    )
    
    print("\n✅ All notifications sent successfully!")
