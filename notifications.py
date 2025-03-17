import smtplib
from email.mime.text import MIMEText
import logging

class NotificationManager:
    def __init__(self, email_sender, email_password):
        self.email_sender = email_sender
        self.email_password = email_password

    def send_email(self, name, form, email, amount, total_paid, required_fee):
        try:
            remaining = required_fee - total_paid
            msg = MIMEText(f"""Dear Parent,
            
A payment of {amount:,} TSH has been received for {name} ({form}).
Total Paid: {total_paid:,} TSH
Remaining Balance: {remaining:,} TSH

Thank you,
School Administration""")
            msg['Subject'] = 'School Fee Payment Update'
            msg['From'] = self.email_sender
            msg['To'] = email

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.email_sender, self.email_password)
                server.send_message(msg)
            logging.info(f"Email sent to {email}")
            return True
        except Exception as e:
            logging.error(f"Email failed: {str(e)}")
            return False