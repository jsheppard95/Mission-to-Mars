# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd

# Set the executable path and initialize the chrome browser in splinter
executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
browser = Browser("chrome", **executable_path)

# NASA News Scraping
# Visit the mars nasa news site
url = "https://mars.nasa.gov/news/"
browser.visit(url)

# Optional delay for loading the page
browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

# Convert the browser html to a soup object
html = browser.html
news_soup = soup(html, "html.parser")

slide_elem = news_soup.select_one("ul.item_list li.slide")

# Use the parent element to find the first `a` tag and save it as `news_title`
news_title = slide_elem.find("div", class_="content_title").get_text()

# Use the parent element to find the paragraph text
news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

# JPL Featured Images
# Visit URL
url = "https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html"
browser.visit(url)

# Find and click the full image button
full_image_elem = browser.find_by_tag('button')[1]  # find_by_tag returns list with 2 elements, 2nd -> 'FULL IMAGE'
full_image_elem.click()

# Parse the resulting html with soup
html = browser.html
img_soup = soup(html, "html.parser")

# Find the relative image url
img_url_rel = img_soup.find("img", class_="fancybox-image").get("src")

# Use the base URL to create an absolute URL
img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

df = pd.read_html("https://space-facts.com/mars/")[0]  # List of DataFrames, 0 and 2 = Basic Facts
df.columns = ["description", "value"]
df.set_index("description", inplace=True)

df.to_html()

browser.quit()