from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from lxml import etree 
import pandas as pd
import time

"""
df = pd.read_csv("all_reviews.csv", index_col=0)
print(df.shape)
"""


our_stores = ["3770 Dryland Way Easton, PA", "313 Lancaster Ave Wayne, PA", 
              "3045 Center Valley Parkway, Suite 118 Center Valley, PA", 
              "1609 N Main Street Suite 1101 Warrington, PA", "4 Airport Square North Wales, PA",
              "310 E 3rd St Bethlehem, PA", "1804 Chestnut Street Philadelphia, PA",
              "4034 Walnut Street Philadelphia, PA", "236 S 11th St Philadelphia, PA", 
              "807 N 2nd Street Philadelphia, PA"]

generic_review_categories = ["Service", "Meal type", "Price per person", "Food #", "Service #", 
                             "Atmosphere #", "Recommended dishes", "Recommendation for vegetarians", 
                             "Vegetarian offerings", "Dietary restrictions", "Parking space", 
                             "Parking options", "Wheelchair accessibility", "Kid-friendliness"]


df = pd.read_csv("all_US_locations_revised.csv", index_col=0)

review_nums = {}

for store in our_stores:
    review_nums[store] = df.loc[store]["number_of_reviews"]



"""
# get all US playa bowls locations 
driver = webdriver.Chrome()
driver.get("https://www.playabowls.com/locations")
location_address = driver.find_elements(By.XPATH, "//span[@id='location-address']")
location_city_state = driver.find_elements(By.XPATH, "//span[@id='location-city-state']")
playa_locations = []
for i in range(len(location_address)):
    address_html = location_address[i].get_attribute('outerHTML')
    city_state_html = location_city_state[i].get_attribute('outerHTML')
    address_soup = BeautifulSoup(address_html, 'html.parser')
    city_state_soup = BeautifulSoup(city_state_html, 'html.parser')
    full_address = address_soup.text.strip() + " " + city_state_soup.text.strip()
    playa_locations.append(full_address)
driver.quit()



all_playa = pd.read_csv("all_US_locations_revised.csv", index_col=0)
index_list = all_playa.index.tolist()
discrepancies = []
for location in playa_locations:
    if location not in index_list:
        discrepancies.append(location)
print(discrepancies)


# get all tropical smoothie cafe locations in PA
driver = webdriver.Chrome()
driver.get("https://locations.tropicalsmoothiecafe.com/pa")
time.sleep(6)
cookie_truster = driver.find_element(By.XPATH, "//button[@id='onetrust-accept-btn-handler']")
cookie_truster.click()
time.sleep(3)
location_elements = driver.find_elements(By.XPATH, "//ul[@class='region-list']/li")
tropical_locations = []
for element in location_elements:
    html = element.get_attribute("outerHTML")
    soup = BeautifulSoup(html, 'html.parser')
    tropical_locations.append(soup.find("a").text + " PA")
driver.quit()


playa_stars_reviews = {}
test_iterations = 0
failed_locations = []
# scrape all US playa bowls locations, get number of reviews and number of stars
driver = webdriver.Chrome()
driver.get("https://www.google.com/maps/")
time.sleep(3)
for location in playa_locations:
    # if (test_iterations == 5):
        # break
    try:
        # driver.get("https://www.google.com/maps/")
        search = driver.find_element(By.XPATH, "//input[@class='fontBodyMedium searchboxinput xiQnY ']")
        substring = "place"
        search_str = " " if (substring in driver.current_url) else "Playa Bowls "
        search.send_keys(search_str + location)
        time.sleep(1)
        search.send_keys(Keys.ARROW_DOWN)
        time.sleep(1)
        search.send_keys(Keys.ENTER)
        time.sleep(2)
        stars = driver.find_element(By.XPATH, "//div[@class='F7nice ']/span[1]/span[1]")
        ratings = driver.find_element(By.XPATH, "//div[@class='F7nice ']/span[2]/span[1]/span")
        star_html = stars.get_attribute("outerHTML")
        star_soup = BeautifulSoup(star_html, 'html.parser')
        star_num = float(star_soup.text.strip())
        rating_html = ratings.get_attribute("outerHTML")
        rating_soup = BeautifulSoup(rating_html, 'html.parser')
        rating_num = rating_soup.text.replace("(", "").replace(")", "")
        if ("," in rating_num):
            rating_num = rating_num.replace(",", "")
        rating_num = (int)(rating_num)
        playa_stars_reviews[location] = [star_num, rating_num]
        review = []
        generic_ratings = []
        if location in our_stores:
            review_button = driver.find_element(By.XPATH, "//button[@aria-label='Reviews for Playa Bowls']")
            review_button.click()
            time.sleep(2)
            body = driver.find_element(By.XPATH, "//div[@class='m6QErb DxyBCb kA9KIf dS8AEf XiKgde ']")
            for i in range(int(rating_num / 10)): # will use rating num if this is integrated with above full location scraping
                last_element = driver.find_elements(By.XPATH, "//div[@class='jftiEf fontBodyMedium ']")[-1]
                driver.execute_script("arguments[0].scrollIntoView();", last_element)
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(2)
            more_buttons = driver.find_elements(By.XPATH, "//button[@aria-label='See more']")
            for element in more_buttons:
                element.click()
    # /div/div/div[4]/div[2]/div"
            for element in (driver.find_elements(By.XPATH, "//div[@class='jftiEf fontBodyMedium ']")):
                html = element.get_attribute('outerHTML')
                soup = BeautifulSoup(html, 'html.parser')
                try:
                    review_text = soup.find_all("span", class_='wiI7pd')[0].text
                    review.append(review_text)
                except Exception:
                    pass
                try:
                    generic_elements = soup.find_all("span", class_='RfDO5c')
                    for i in range(len(generic_elements)):
                        temp = []
                        text = generic_elements[i].span.text
                        temp.append(text)
                    generic_ratings.append(temp)
                except Exception:
                    pass
        driver.quit()
        print(playa_stars_reviews[location])
        print(len(review))
        print(len(generic_ratings))
        print(review)
        print(generic_ratings)
        test_iterations+=1
        break
    

        # test_iterations += 1
    except Exception: # handle unopened locations
        failed_locations.append(location)
        driver.get("https://www.google.com/maps/")
        time.sleep(5)
        continue




# run the program again for locations that broke the program the first time around
# locations will either be nonexistent/unopened or they just didn't load properly
driver.get("https://www.google.com/maps/")
time.sleep(5)
for location in failed_locations:
    try:
        # driver.get("https://www.google.com/maps/")
        search = driver.find_element(By.XPATH, "//input[@class='fontBodyMedium searchboxinput xiQnY ']")
        substring = "place"
        search_str = " " if (substring in driver.current_url) else "Playa Bowls "
        search.send_keys(search_str + location)
        time.sleep(1)
        search.send_keys(Keys.ARROW_DOWN)
        time.sleep(1)
        search.send_keys(Keys.ENTER)
        time.sleep(8)
        stars = driver.find_element(By.XPATH, "//div[@class='F7nice ']/span[1]/span[1]")
        ratings = driver.find_element(By.XPATH, "//div[@class='F7nice ']/span[2]/span[1]/span")
        star_html = stars.get_attribute("outerHTML")
        star_soup = BeautifulSoup(star_html, 'html.parser')
        star_num = float(star_soup.text.strip())
        rating_html = ratings.get_attribute("outerHTML")
        rating_soup = BeautifulSoup(rating_html, 'html.parser')
        rating_num = rating_soup.text.replace("(", "").replace(")", "")
        if ("," in rating_num):
            rating_num = rating_num.replace(",", "")
        rating_num = (int)(rating_num)
        playa_stars_reviews[location] = [star_num, rating_num]
    except Exception:
        driver.get("https://www.google.com/maps/@42.713088,-73.2004352,14z?entry=ttu&g_ep=EgoyMDI0MTAyMS4xIKXMDSoASAFQAw%3D%3D")
        time.sleep(5)
        continue
playa_US = pd.DataFrame.from_dict(playa_stars_reviews, orient='index', columns = ['stars', 'number_of_reviews'])
playa_US.to_csv("all_US_locations.csv", index=True, header=True)

driver = webdriver.Chrome()
driver.get("https://www.google.com/maps/")
tropical_stars_reviews = {}
failed_locations = []
for location in tropical_locations:
    try:
        search = driver.find_element(By.XPATH, "//input[@class='fontBodyMedium searchboxinput xiQnY ']")
        substring = "place"
        search_str = " " if (substring in driver.current_url) else "Tropical Smoothie Cafe "
        search.send_keys(search_str + location)
        time.sleep(1)
        search.send_keys(Keys.ARROW_DOWN)
        time.sleep(1)
        search.send_keys(Keys.ENTER)
        time.sleep(3)
        stars = driver.find_element(By.XPATH, "//div[@class='F7nice ']/span[1]/span[1]")
        ratings = driver.find_element(By.XPATH, "//div[@class='F7nice ']/span[2]/span[1]")
        star_html = stars.get_attribute("outerHTML")
        star_soup = BeautifulSoup(star_html, 'html.parser')
        star_num = float(star_soup.text.strip())
        rating_html = ratings.get_attribute("outerHTML")
        rating_soup = BeautifulSoup(rating_html, 'html.parser')
        rating_num = int(rating_soup.text.replace("(", "").replace(")", ""))
        tropical_stars_reviews[location] = [star_num, rating_num]
        # test_iterations += 1
    except Exception: # handle unopened locations
        failed_locations.append(location)
        driver.get("https://www.google.com/maps/")
        time.sleep(5)
        continue
driver.quit()

print(failed_locations)

tropical_PA = pd.DataFrame.from_dict(tropical_stars_reviews, orient='index', columns = ['stars', 'number_of_reviews'])
tropical_PA.to_csv("tropical_PA.csv", index=True, header=True)
"""


driver = webdriver.Chrome()
driver.get("https://www.google.com/maps/")
time.sleep(4)
all_reviews = []
# if the current location is a target PA store, scrape all reviews along with number and stars 
for location in our_stores:
    search = driver.find_element(By.XPATH, "//input[@class='fontBodyMedium searchboxinput xiQnY ']")
    substring = "place"
    search_str = " " if (substring in driver.current_url) else "Playa Bowls "
    search.send_keys(search_str + location)
    time.sleep(1)
    search.send_keys(Keys.ARROW_DOWN)
    time.sleep(1)
    search.send_keys(Keys.ENTER)
    time.sleep(5)
    rating_num = review_nums[location]
    
    ratings = driver.find_element(By.XPATH, "//div[@class='F7nice ']/span[2]/span[1]")
    rating_html = ratings.get_attribute("outerHTML")
    rating_soup = BeautifulSoup(rating_html, 'html.parser')
    rating_num = int(rating_soup.text.replace("(", "").replace(")", ""))
    
    review_button = driver.find_element(By.XPATH, "//button[@aria-label='Reviews for Playa Bowls']")
    review_button.click()
    time.sleep(5)
    body = driver.find_element(By.XPATH, "//div[@class='m6QErb DxyBCb kA9KIf dS8AEf XiKgde ']")

    
    for i in range(int(rating_num / 10)): # will use rating num if this is integrated with above full location scraping
        more_buttons = driver.find_elements(By.XPATH, "//button[@aria-label='See more']")
        for element in more_buttons:
            element.click()
        last_element = driver.find_elements(By.XPATH, "//div[@class='jftiEf fontBodyMedium ']")[-1]
        driver.execute_script("arguments[0].scrollIntoView();", last_element)
        for i in range(10):
            body.send_keys(Keys.PAGE_DOWN)
        time.sleep(2)
    

    # /div/div/div[4]/div[2]/div"
    for element in (driver.find_elements(By.XPATH, "//div[@class='jftiEf fontBodyMedium ']")):
        review_content = {}
        html = element.get_attribute('outerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        review_content["name"] = soup.find(class_="jftiEf fontBodyMedium")["aria-label"]
        review_stars = soup.find_all("span", class_="kvMYJc")[0]["aria-label"].split(" ")[0]
        review_content["location"] = location
        review_content["stars"] = review_stars
        try:
            review_text = soup.find_all("span", class_='wiI7pd')[0].text
            review_content["text"] = review_text
        except Exception:
            review_content["text"] = "N/A"
            pass
        try:
            generics = [element.span.text for element in soup.find_all("span", class_="RfDO5c")]
            for count,ele in enumerate(generics):
                if (isinstance(ele, str) and ": " in ele):
                    split = ele.split(": ")
                    generics[count] = split[0] + " #"
                    generics.insert(count + 1, int(split[1]))
            for s in generic_review_categories:
                if s in generics:
                    index = generics.index(s)
                    review_content[s] = generics[index + 1]
                else:
                    review_content[s] = "N/A"
        except Exception:
            pass
        all_reviews.append(review_content)
driver.quit()

print(all_reviews)

df = pd.DataFrame(all_reviews)
df.set_index("name", inplace=True)
df.to_csv("all_reviews_2.csv", index=True, header=True)
