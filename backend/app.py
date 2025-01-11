from flask import Flask, render_template,jsonify 
from flask_cors import CORS
from pymongo import MongoClient 
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
import undetected_chromedriver as uc 
from pymongo import MongoClient 
import uuid 
import datetime 
import requests 
import time 
import random
import sys
print("Python version:", sys.version)

app = Flask(__name__) 
CORS(app, resources={r"/*": {"origins": "*"}})
client = MongoClient("mongodb+srv://sr33n3sh:sreenesH4@cluster0.e62e55q.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0") 
db = client.twitter_data 
collection = db.trending_topics
@app.route('/')
def home():
    return "Hello, Flask is working!"

@app.route('/scrape', methods=['GET'])
def scrape(): 
    # MongoDB configuration 
    client = MongoClient(mongodbURL)
    db = client["twitter_data"] 
    collection = db["trending_topics"]


    # Configure Selenium WebDriver using undetected_chromedriver
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    #options.add_argument(f"--proxy-server={PROXY}")
    # options.add_argument("--no-sandbox")  # Bypass OS security model
    # options.add_argument("--disable-dev-shm-usage") 
    options.add_argument("--headless")
    #options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = uc.Chrome(options=options)

    # Generate a unique ID for this scraping session
    unique_id = str(uuid.uuid4())

    try:
        # Open Twitter's login page
        url = "https://x.com/login"
        driver.get(url)

        # Wait for the login fields to load
        wait = WebDriverWait(driver, 10)
        username_field = wait.until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        #time.sleep(random.uniform(2,3))  # Wait for 2 to 5 seconds randomly

        # Enter the username/email
        username_field.send_keys(twitter_mail)  # Replace with your Twitter username or email
        username_field.send_keys(Keys.RETURN)

        username_field = wait.until(
        EC.presence_of_element_located((By.NAME, "text"))  # Or use By.CSS_SELECTOR, or By.XPATH
    )
        #time.sleep(random.uniform(2,3))
        # Enter the username
        username_field.send_keys(twitter_username)  # Replace with your actual username
        username_field.send_keys(Keys.RETURN)

        # Wait for the password field (if needed)
        password_field = wait.until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        #time.sleep(random.uniform(1,3))
        # Enter the password
        password_field.send_keys(twitter_password)  # Replace with your Twitter password
        password_field.send_keys(Keys.RETURN)
    # Wait for the "What's happening" section to load
        wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//div[contains(@class, 'css-175oi2r')]//div[@data-testid='trend']"))
        )

        # Now, extract the trending topics
        trending_topics_elements = driver.find_elements(
            By.XPATH, "//div[@data-testid='trend']//span[contains(@class, 'css-1jxf684') and not(ancestor::div[contains(@class, 'r-1d09ksm')]) and not(ancestor::div[contains(@class, 'r-14gqq1x')])]"
        )

        print(trending_topics_elements)
        # Extract the text for each topic and print
        trending_topics = [topic.text for topic in trending_topics_elements if topic.text.strip() != ""]
        
        print("Top Trending Topics:")
        print(trending_topics)
        for index, topic in enumerate(trending_topics, start=1):
            print(f"{index}. {topic}")

        # Get the current IP address used
        ip_address = requests.get("http://ipinfo.io/ip").text.strip()

        # Record the date and time of script completion
        end_time = datetime.datetime.now()

        # Store results in MongoDB
        record = {
            "unique_id": unique_id,
            "trend1": trending_topics[0] if len(trending_topics) > 0 else None,
            "trend2": trending_topics[1] if len(trending_topics) > 1 else None,
            "trend3": trending_topics[2] if len(trending_topics) > 2 else None,
            "trend4": trending_topics[3] if len(trending_topics) > 3 else None,
            "trend5": trending_topics[4] if len(trending_topics) > 4 else None,
            "end_time": end_time,
            "ip_address": ip_address
        }
        collection.insert_one(record)
        record['unique_id']=str(record['unique_id'])
        print(f"Data stored in MongoDB with unique ID: {unique_id}")
        return jsonify({'id':unique_id,"trend1": trending_topics[0] if len(trending_topics) > 0 else None,
            "trend2": trending_topics[1] if len(trending_topics) > 1 else None,
            "trend3": trending_topics[2] if len(trending_topics) > 2 else None,
            "trend4": trending_topics[3] if len(trending_topics) > 3 else None,"end_time": end_time,
            "ip_address": ip_address
        }), 200
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser
        driver.quit()

@app.route('/trends') 
def trends(): 
    scrape() 
    records = collection.find().sort("timestamp", -1)
    return render_template("trends.html", records=records)


if __name__ == "__main__": 
    app.run(debug=True,port=5001)