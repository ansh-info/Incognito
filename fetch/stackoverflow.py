import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from operations import insert_stackoverflow_data

#Using selenium to tackle lazy loading and to fetch the proper user data for the given base url.
#once we get the proper user profile link, we can use it to scrape the candidate profiles
def get_profile_links(base_url, num_pages):

    chrome_options = Options() #for mainf the code run in headless state
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--window-size=1920x1080") #make layout looks as expected

    driver = webdriver.Chrome(options=chrome_options)
    user_links = [] #to store all the links


    for i in range(950, num_pages + 1): #Once check pages from 30-36.
        url = base_url.format(i) #dynamically update the pages
        #print(f'check the url: {url}')  --CHeckpoint
        
        driver.get(url)
    
        time.sleep(10)  # wait until tha page loads completely
        
        # Once done, get the HTML content and parse with BeautifulSoup
        #soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find all user profile links nested under the class user-details
        user_list = driver.find_elements(By.CLASS_NAME, 'user-details')
        
        for user in user_list:
            a_tag = user.find_element(By.TAG_NAME, 'a')
            if a_tag:
                profile_url = a_tag.get_attribute('href')
                user_links.append(profile_url)
        
        print(f"check collected links for the page num {i}: {len(user_links)}")

    # Close
    driver.quit()

    return user_links

def convert_reached_to_number(reached_str):
    # Convert strings like '554k', '21.1m', '135.4m', '1b' to actual numbers
    reached_str = reached_str.lower().strip()  # Handle lowercase and remove any extra spaces
    
    if reached_str.endswith('k'):
        return float(reached_str[:-1]) * 1000  # Convert 'k' to thousand
    elif reached_str.endswith('m'):
        return float(reached_str[:-1]) * 1000000  # Convert 'm' to million
    elif reached_str.endswith('b'):
        return float(reached_str[:-1]) * 1000000000  # Convert 'b' to billion
    else:
        return float(reached_str)  # If it's a plain number, just convert to float
    
def convert_str_to_int(str_to_conv):
    ##Convert a string like '19,919' to an integer by removing commas. If no commas, return as integer
    # Check if the string contains a comma (Did this to insert the data as per schema)
    if ',' in str_to_conv:
        return int(str_to_conv.replace(',', ''))  # Remove commas and convert to integer
    else:
        return int(str_to_conv)  # If no commas, convert directly to integer


def scrape_user_profile(profile_url): #Scrape the candidate profile page and collect relevant info
    response = requests.get(profile_url, headers = {'User-agent': 'your bot 0.1'})
    soup = BeautifulSoup(response.text, 'html.parser')
    print(f"Response Status Code for {profile_url}: {response.status_code}")

    #Find gitHub link if exists in profilr to extract further data from gitub
    github_link = None
    social_section = soup.find('div', class_='ps-relative mb16')
    if social_section:
        social_links = social_section.find_all('a')
        for link in social_links:
            href = link.get('href', '')
            if 'github.com' in href:
                github_link = href
                break  # Exit once GitHub link is found

    #If no GitHub link is found, return None to skip this user
    if not github_link:
        return None

    # Extract from stats section of the page (reputation,answers count etc)
    stats_section = soup.find('div', id='stats')

    if stats_section:
        reputation_str = stats_section.find_all('div', class_='fs-body3 fc-black-600')[0].text.strip()
        reputation = convert_str_to_int(reputation_str)
        reached_str = stats_section.find_all('div', class_='fs-body3 fc-black-600')[1].text.strip()
        reached = convert_reached_to_number(reached_str)
        answers_str = stats_section.find_all('div', class_='fs-body3 fc-black-600')[2].text.strip()
        answers = convert_str_to_int(answers_str) 
        questions = stats_section.find_all('div', class_='fs-body3 fc-black-600')[3].text.strip()
    else:
        reputation = reached = answers = questions = None #fill none if not found

    # Find and extract all the badge related info.
    badges = soup.find_all('div', class_='flex--item s-card bar-md')
    
    # Extract the scores for gold, silver, and bronze badges
    gold_badge_div=  badges[0].find('div', class_='fs-title fw-bold fc-black-600') #check if the badge exists for an user
    gold_badge_score_str = gold_badge_div.text.strip() if gold_badge_div else '0' 
    gold_badge_score= convert_str_to_int(gold_badge_score_str)

    silver_badge_div= badges[1].find('div', class_='fs-title fw-bold fc-black-600')
    silver_badge_score_str = silver_badge_div.text.strip() if silver_badge_div else '0' 
    silver_badge_score=convert_str_to_int(silver_badge_score_str)

    bronze_badge_div = badges[2].find('div', class_='fs-title fw-bold fc-black-600')
    bronze_badge_score_str = bronze_badge_div.text.strip() if bronze_badge_div else '0'
    bronze_badge_score=convert_str_to_int(bronze_badge_score_str)
    
    # Extract top5 tags
    tags = soup.find_all('div', class_='flex--item ws-nowrap')
    top_5_tags = ','.join([tags[i].text.strip() for i in range(min(5,len(tags)))])

    user_data = {
        'profileURL': profile_url,
        'user_id': profile_url.split('/')[-2],  # Extract userid from the URL itself
        'githubUrl': github_link,
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

# main code
base_url = "https://stackoverflow.com/users?page={}&tab=reputation&filter=quarter"
num_pages = 955  # Adjust as needed
    
# Step 1: Get all profile links
profile_links = get_profile_links(base_url, num_pages)    

# Step 2: Scrape each profile and insert the data into the database
for profile_link in profile_links:
    print(f"Scraping the link: {profile_link}...")
    user_data = scrape_user_profile(profile_link)

    # Skip this user if no GitHub link is found (i.e., user_data is None from scrape_user_profile fn )
    if user_data is None:
        print(f"Skipping user: {profile_link}, no GitHub link found.")
        continue  # fetch data for the next user

    # Insert the user data into the database
    try:
        insert_stackoverflow_data(user_data)  # Insert the data into the database
    except Exception as e:
        print(f"Failed to insert data for {user_data['user_id']}: {e}")

print(f'Successfully fetched and inserted data for profiles from StackOverflow!')