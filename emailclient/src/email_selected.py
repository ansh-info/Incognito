# import os
# import mysql.connector
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from dotenv import load_dotenv
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # Load environment variables from .env file
# load_dotenv()

# # MySQL database connection details for submissions
# db_config = {
#     'user': os.getenv('DB_USER1'),
#     'password': os.getenv('DB_PASSWORD1'),
#     'host': os.getenv('DB_HOST1'),
#     'database': os.getenv('DB_NAME1')
# }

# # MySQL database connection details for logging
# log_db_config = {
#     'user': os.getenv('LOG_DB_USER1'),
#     'password': os.getenv('LOG_DB_PASSWORD1'),
#     'host': os.getenv('LOG_DB_HOST1'),
#     'database': os.getenv('LOG_DB_NAME1')
# }

# # Email sender details
# smtp_user = os.getenv('SMTP_USER')
# smtp_password = os.getenv('SMTP_PASSWORD')

# # Email subjects and templates
# subject_pass = "Congratulations! You've Passed the Coding Interview"
# subject_fail = "Coding Interview Result"

# email_template_pass = """
# Dear {username},

# Congratulations! We are pleased to inform you that you have successfully passed our coding interview. We are excited to have you join our team.

# Best regards,
# The Doodle Team
# """

# email_template_fail = """
# Dear {username},

# We regret to inform you that you did not pass the coding interview. We appreciate your effort and encourage you to try again in the future.

# Best regards,
# The Doodle Team
# """

# # Function to get submission data from the database
# def get_submission_data():
#     logging.info("Fetching submission data from the database.")
#     try:
#         connection = mysql.connector.connect(**db_config)
#         cursor = connection.cursor(dictionary=True)
#         query = "SELECT submission_id, user_id, question_id, code, result, email FROM submissions"
#         cursor.execute(query)
#         result = cursor.fetchall()
#         logging.info(f"Fetched {len(result)} submissions from the database.")
#         return result
#     except mysql.connector.Error as err:
#         logging.error(f"Error: {err}")
#         return []
#     finally:
#         cursor.close()
#         connection.close()

# # Function to log email sending status to the logging database
# def log_email_status(submission, status, error_message=None):
#     try:
#         connection = mysql.connector.connect(**log_db_config)
#         cursor = connection.cursor()
#         query = """
#         INSERT INTO email_selection_logging (submission_id, user_id, question_id, code, result, email, status, error_message)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         cursor.execute(query, (
#             submission['submission_id'], submission['user_id'], submission['question_id'], submission['code'],
#             submission['result'], submission['email'], status, error_message))
#         connection.commit()
#         logging.info(f"Logged email status for {submission['email']}: {status}")
#     except mysql.connector.Error as err:
#         logging.error(f"Error logging email status for {submission['email']}: {err}")
#     finally:
#         cursor.close()
#         connection.close()

# # Function to send email using SMTP
# def send_email(submission):
#     to_email = submission['email']
#     username = f"user{submission['user_id']}"  # Assuming username is derived from user_id
#     subject = subject_pass if submission['result'] == 1 else subject_fail
#     email_template = email_template_pass if submission['result'] == 1 else email_template_fail
#     message_content = email_template.format(username=username)
    
#     msg = MIMEMultipart()
#     msg['From'] = smtp_user
#     msg['To'] = to_email
#     msg['Subject'] = subject
#     msg.attach(MIMEText(message_content, 'plain'))

#     try:
#         logging.info(f"Attempting to send email to {to_email}.")
#         server = smtplib.SMTP('smtp.gmail.com', 587)
#         server.starttls()
#         server.login(smtp_user, smtp_password)
#         server.send_message(msg)
#         logging.info(f"Email sent to {to_email}.")
#         print(f"Email sent to {to_email}.")
#         log_email_status(submission, 'Sent')
#     except smtplib.SMTPAuthenticationError as auth_error:
#         logging.error(f"Authentication failed: {auth_error}")
#         print(f"Authentication failed for {to_email}: {auth_error}")
#         log_email_status(submission, 'Failed', str(auth_error))
#     except Exception as e:
#         logging.error(f"Failed to send email to {to_email}: {e}")
#         print(f"Failed to send email to {to_email}: {e}")
#         log_email_status(submission, 'Failed', str(e))
#     finally:
#         server.quit()

# # Main function to fetch data and send emails
# def main():
#     logging.info("Starting the email sending process.")
#     submission_data = get_submission_data()
#     if not submission_data:
#         logging.error("No submission data found. Exiting.")
#         print("No submission data found. Exiting.")
#         return

#     for submission in submission_data:
#         send_email(submission)

#     logging.info("Email sending process completed.")
#     print("Email sending process completed.")

# if __name__ == "__main__":
#     main()


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

# MySQL database connection details for submissions
db_config = {
    'user': os.getenv('DB_USER1'),
    'password': os.getenv('DB_PASSWORD1'),
    'host': os.getenv('DB_HOST1'),
    'database': os.getenv('DB_NAME1')
}

# MySQL database connection details for logging
log_db_config = {
    'user': os.getenv('LOG_DB_USER1'),
    'password': os.getenv('LOG_DB_PASSWORD1'),
    'host': os.getenv('LOG_DB_HOST1'),
    'database': os.getenv('LOG_DB_NAME1')
}

# Email sender details
smtp_user = os.getenv('SMTP_USER')
smtp_password = os.getenv('SMTP_PASSWORD')

# Email subjects and templates
subject_pass = "Congratulations! You've Passed the Coding Interview"
subject_fail = "Coding Interview Result"

email_template_pass = """
Dear {username},

Congratulations! We are pleased to inform you that you have successfully passed our coding interview. We are excited to have you join our team.

Best regards,
The Doodle Team
"""

email_template_fail = """
Dear {username},

We regret to inform you that you did not pass the coding interview. We appreciate your effort and encourage you to try again in the future.

Best regards,
The Doodle Team
"""

# Function to get the latest submissions for each question by each user
def get_latest_submissions():
    logging.info("Fetching the latest submission data from the database.")
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT t1.submission_id, t1.user_id, t1.question_id, t1.code, t1.result, t1.email 
        FROM submissions t1
        JOIN (
            SELECT user_id, question_id, MAX(submission_id) as max_submission_id
            FROM submissions
            GROUP BY user_id, question_id
        ) t2 ON t1.user_id = t2.user_id AND t1.question_id = t2.question_id AND t1.submission_id = t2.max_submission_id
        """
        cursor.execute(query)
        result = cursor.fetchall()
        logging.info(f"Fetched {len(result)} latest submissions from the database.")
        return result
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

# Function to log email sending status to the logging database
def log_email_status(submission, status, error_message=None):
    try:
        connection = mysql.connector.connect(**log_db_config)
        cursor = connection.cursor()
        query = """
        INSERT INTO email_selection_logging (submission_id, user_id, question_id, code, result, email, status, error_message)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            submission['submission_id'], submission['user_id'], submission['question_id'], submission['code'],
            submission['result'], submission['email'], status, error_message))
        connection.commit()
        logging.info(f"Logged email status for {submission['email']}: {status}")
    except mysql.connector.Error as err:
        logging.error(f"Error logging email status for {submission['email']}: {err}")
    finally:
        cursor.close()
        connection.close()

# Function to send email using SMTP
def send_email(to_email, username, passed):
    subject = subject_pass if passed else subject_fail
    email_template = email_template_pass if passed else email_template_fail
    message_content = email_template.format(username=username)
    
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
        return 'Sent', None
    except smtplib.SMTPAuthenticationError as auth_error:
        logging.error(f"Authentication failed: {auth_error}")
        print(f"Authentication failed for {to_email}: {auth_error}")
        return 'Failed', str(auth_error)
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {e}")
        print(f"Failed to send email to {to_email}: {e}")
        return 'Failed', str(e)
    finally:
        server.quit()

# Main function to fetch data and send emails
def main():
    logging.info("Starting the email sending process.")
    latest_submissions = get_latest_submissions()
    if not latest_submissions:
        logging.error("No submission data found. Exiting.")
        print("No submission data found. Exiting.")
        return

    # Process submissions by user
    user_results = {}
    for submission in latest_submissions:
        user_id = submission['user_id']
        if user_id not in user_results:
            user_results[user_id] = {
                'total_questions': 0,
                'passed_questions': 0,
                'submissions': []
            }
        user_results[user_id]['total_questions'] += 1
        if submission['result'] == 1:
            user_results[user_id]['passed_questions'] += 1
        user_results[user_id]['submissions'].append(submission)

    # Determine if user passed overall and send emails
    for user_id, data in user_results.items():
        passed = data['passed_questions'] >= data['total_questions'] * 0.8  # Example threshold: pass if at least 80% of questions are correct
        email = data['submissions'][0]['email']
        username = f"user{user_id}"  # Assuming username is derived from user_id
        status, error_message = send_email(email, username, passed)
        for submission in data['submissions']:
            log_email_status(submission, status, error_message)

    logging.info("Email sending process completed.")
    print("Email sending process completed.")

if __name__ == "__main__":
    main()


