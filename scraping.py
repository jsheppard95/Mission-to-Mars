# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

def scrape_all():
    """
    scrape_all
    Calls functions defined in this module to scrape Mars websites and return
    data

    Parameters:
    -----------
    None

    Returns:
    --------
    data : dict
        Mars data dictionary containing elements:
        news_title: NASA Mars most recent article title
        news_paragraph: NASA Mars most recent article description
        featured_image: JPL Mars most recent image
        facts: spacefacts table of Mars facts
        last_modified: acquisition time
    """
    # Initiate headless driver
    browser = Browser("chrome", executable_path="/usr/local/bin/chromedriver",
                      headless=True)
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemisphere_images(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop the webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    """
    mars_news
    Navigates to NASA Mars news site and return first article's
    headline and description.

    Parameters:
    -----------
    browser : splinter.Browser
        spliter.Browser object instantiated with chromedriver executable_path

    Returns:
    --------
    (news_title, news_p) : tuple
        news_title : str, first article headline
        news_p : str, first article description
    """
    # Visit the mars nasa news site
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object
    html = browser.html
    news_soup = soup(html, "html.parser")

    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # Use the parent element to find the first `a` tag and save it as
        # `news_title`
        news_title = slide_elem.find("div", class_="content_title").\
            get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").\
            get_text()
    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):
    """
    featured_image
    Navigates to JPL Mars images site and return URL of first image

    Parameters:
    -----------
    browser : splinter.Browser
        spliter.Browser object instantiated with chromedriver executable_path

    Returns:
    --------
    img_url : str
        URL of the first image found on the JPL Mars image site.
    """
    # Visit URL
    url = "https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html"
    browser.visit(url)

    # Find and click the full image button
    # find_by_tag returns list with 2 elements, 2nd -> 'FULL IMAGE'
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, "html.parser")

    try:
        # Find the relative image url
        img_url_rel = img_soup.find("img", class_="fancybox-image").get("src")
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

def mars_facts():
    """
    mars_facts
    Navigates to space-facts Marse website and returns table of Mars facts

    Parameters:
    -----------
    None
    
    Returns:
    --------
    df.to_html() : str
        Pandas DataFrame of Mars Facts in html format
    """
    try:
        # use `pd.read_html` to scrape the facts table into a DataFrame
        # List of DataFrames, 0 and 2 = Basic Facts
        df = pd.read_html("https://space-facts.com/mars/")[0]
    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns = ["Description", "Value"]
    df.set_index("Description", inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

def hemisphere_images(browser):
    # Visit the URL
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    url_base = "https://astrogeology.usgs.gov"
    browser.visit(url)

    # Create list to hold images and titles
    hemisphere_image_urls = []  # list of dictionaries [{url: title}, ...]

    # Retrieve image URL and title for each hemisphere
    html = browser.html
    mars_soup = soup(html, "html.parser")

    try:
        # Find main box containing 4 hemisphere image titles/links
        img_soup = mars_soup.find("div", class_="collapsible results")
        img_links = img_soup.find_all("div", class_="item")

        # Iterate through each image in box
        for link in img_links:
            hemispheres = {}
            entry_desc = link.find("div", class_="description")
            image_page = entry_desc.find("a", class_="itemLink product-item")
            # Extract title
            title = image_page.get_text()

            # Extract URL of the image-specifc page and go there
            image_page_rel = image_page.attrs["href"]
            image_page_full = url_base + image_page_rel
            browser.visit(image_page_full)

            html = browser.html
            img_soup = soup(html, "html.parser")
            
            # Find "Download" box
            download_soup = img_soup.find("div", class_="downloads")
            # Extract link to "Sample"
            img_url = download_soup.find("li").find("a").attrs["href"]
            
            # Store image URL and title in single-hemisphere dictionary and append dict to full list
            hemispheres["img_url"] = img_url
            hemispheres["title"] = title
            hemisphere_image_urls.append(hemispheres)
    except BaseException:
        return None
    
    # Return hemispher_image_urls dictionary
    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as a script, print scraped data
    print(scrape_all())