import os
import mysql.connector
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# MySQL database connection details for user data
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME')
}

# MySQL database connection details for logging
log_db_config = {
    'user': os.getenv('LOG_DB_USER'),
    'password': os.getenv('LOG_DB_PASSWORD'),
    'host': os.getenv('LOG_DB_HOST'),
    'database': os.getenv('LOG_DB_NAME')
}

# Email sender details
smtp_user = os.getenv('SMTP_USER')
smtp_password = os.getenv('SMTP_PASSWORD')

# Email subject
subject = "Invitation to Attempt Online Coding Interview Test"

# Email template
email_template = """
Dear {username},

We are pleased to inform you that you are a potential candidate for our company Doodle. We invite you to attempt an online coding interview test.

Use the username '{username}' and email ID '{email}' to register yourself at the web UI login portal, and then login using the same username or email ID with the password you entered while registering.

Please click on the following link to start the test:
Local: http://localhost:3000
On Your Network: http://192.168.1.9:3000

Best regards,
The Doodle Team
"""

# Function to get user data from the database
def get_user_data():
    logging.info("Fetching user data from the database.")
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        query = "SELECT user_id, username, email FROM suitable_candidates"
        cursor.execute(query)
        result = cursor.fetchall()
        logging.info(f"Fetched {len(result)} users from the database.")
        return result
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

# Function to log email sending status to the logging database
def log_email_status(user_id, email, status, error_message=None):
    try:
        connection = mysql.connector.connect(**log_db_config)
        cursor = connection.cursor()
        query = """
        INSERT INTO email_interview_logging (user_id, email, status, error_message)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, email, status, error_message))
        connection.commit()
        logging.info(f"Logged email status for {email}: {status}")
    except mysql.connector.Error as err:
        logging.error(f"Error logging email status for {email}: {err}")
    finally:
        cursor.close()
        connection.close()

# Function to send email using SMTP
def send_email(user):
    to_email = user['email']
    message_content = email_template.format(username=user['username'], email=user['email'])
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message_content, 'plain'))

    try:
        logging.info(f"Attempting to send email to {to_email}.")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        logging.info(f"Email sent to {to_email}.")
        print(f"Email sent to {to_email}.")
        log_email_status(user['user_id'], to_email, 'Sent')
    except smtplib.SMTPAuthenticationError as auth_error:
        logging.error(f"Authentication failed: {auth_error}")
        print(f"Authentication failed for {to_email}: {auth_error}")
        log_email_status(user['user_id'], to_email, 'Failed', str(auth_error))
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {e}")
        print(f"Failed to send email to {to_email}: {e}")
        log_email_status(user['user_id'], to_email, 'Failed', str(e))
    finally:
        server.quit()

# Main function to fetch data and send emails
def main():
    logging.info("Starting the email sending process.")
    user_data = get_user_data()
    if not user_data:
        logging.error("No user data found. Exiting.")
        print("No user data found. Exiting.")
        return

    for user in user_data:
        send_email(user)

    logging.info("Email sending process completed.")
    print("Email sending process completed.")

if __name__ == "__main__":
    main()
