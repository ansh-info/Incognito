import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import mysql.connector
import time

# MySQL connection configuration
db_config = {
    'user': 'root',
    'password': '9084Mysql#',
    'host': '127.0.0.1',  # Assuming Docker is set up to use the host network
    'database': 'data_collection',
}

# Function to create the table if it does not exist
def create_table_if_not_exists():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # SQL statement to create the table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS web_stackoverflow (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ProfileURL VARCHAR(255),
            user_id VARCHAR(50),
            github_link VARCHAR(255),
            reputation VARCHAR(50),
            reached VARCHAR(50),
            answers VARCHAR(50),
            questions VARCHAR(50),
            gold_badge_score INT,
            silver_badge_score INT,
            bronze_badge_score INT,
            top_5_tags VARCHAR(255)
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("Table 'web_stackoverflow' checked/created successfully.")

    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")
    finally:
        cursor.close()
        conn.close()

# Function to insert data into MySQL
def insert_into_mysql(data):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert query
        insert_query = """
        INSERT INTO web_stackoverflow (
            ProfileURL, user_id, github_link, reputation, reached, answers, questions,
            gold_badge_score, silver_badge_score, bronze_badge_score, top_5_tags
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Insert data
        cursor.execute(insert_query, (
            data['ProfileURL'], data['user_id'], data['github_link'], data['reputation'],
            data['reached'], data['answers'], data['questions'], data['gold_badge_score'],
            data['silver_badge_score'], data['bronze_badge_score'], data['top_5_tags']
        ))
        
        conn.commit()
        print(f"Inserted data for user {data['user_id']} into MySQL.")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

# Selenium function to get profile links
def get_profile_links(base_url, num_pages):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(options=chrome_options)
    user_links = []

    for i in range(1, num_pages + 1):
        url = base_url.format(i)
        driver.get(url)
        time.sleep(10)

        user_list = driver.find_elements(By.CLASS_NAME, 'user-details')
        for user in user_list:
            a_tag = user.find_element(By.TAG_NAME, 'a')
            if a_tag:
                profile_url = a_tag.get_attribute('href')
                user_links.append(profile_url)

    driver.quit()
    return user_links

# Function to clean and convert numeric strings to integers
def clean_numeric_value(value):
    # Remove commas and convert to integer; if conversion fails, return 0
    return int(value.replace(',', '')) if value and value.replace(',', '').isdigit() else 0

# Function to scrape user profile
def scrape_user_profile(profile_url):
    response = requests.get(profile_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    github_link = None
    social_section = soup.find('div', class_='ps-relative mb16')
    if social_section:
        social_links = social_section.find_all('a')
        for link in social_links:
            href = link.get('href', '')
            if 'github.com' in href:
                github_link = href
                break

    if not github_link:
        return None

    stats_section = soup.find('div', id='stats')
    if stats_section:
        reputation = stats_section.find_all('div', class_='fs-body3 fc-black-600')[0].text.strip()
        reached = stats_section.find_all('div', class_='fs-body3 fc-black-600')[1].text.strip()
        answers = stats_section.find_all('div', class_='fs-body3 fc-black-600')[2].text.strip()
        questions = stats_section.find_all('div', class_='fs-body3 fc-black-600')[3].text.strip()
    else:
        reputation = reached = answers = questions = None

    badges = soup.find_all('div', class_='flex--item s-card bar-md')
    gold_badge_score = clean_numeric_value(badges[0].find('div', class_='fs-title fw-bold fc-black-600').text.strip()) if badges else 0
    silver_badge_score = clean_numeric_value(badges[1].find('div', class_='fs-title fw-bold fc-black-600').text.strip()) if badges else 0
    bronze_badge_score = clean_numeric_value(badges[2].find('div', class_='fs-title fw-bold fc-black-600').text.strip()) if badges else 0

    tags = soup.find_all('div', class_='flex--item ws-nowrap')
    top_5_tags = ','.join([tags[i].text.strip() for i in range(min(5, len(tags)))])

    user_data = {
        'ProfileURL': profile_url,
        'user_id': profile_url.split('/')[-2],
        'github_link': github_link,
        'reputation': reputation,
        'reached': reached,
        'answers': answers,
        'questions': questions,
        'gold_badge_score': gold_badge_score,
        'silver_badge_score': silver_badge_score,
        'bronze_badge_score': bronze_badge_score,
        'top_5_tags': top_5_tags
    }

    return user_data

# Main execution
base_url = "https://stackoverflow.com/users?page={}&tab=reputation&filter=quarter"
num_pages = 2

# Create table if not exists
create_table_if_not_exists()

# Get all profile links
profile_links = get_profile_links(base_url, num_pages)

# Scrape each profile and insert into MySQL
for profile_link in profile_links:
    print(f"Scraping the link: {profile_link}...")
    user_data = scrape_user_profile(profile_link)

    if user_data is None:
        print(f"Skipping user: {profile_link}, no GitHub link found.")
        continue

    # Insert scraped data into MySQL
    insert_into_mysql(user_data)
