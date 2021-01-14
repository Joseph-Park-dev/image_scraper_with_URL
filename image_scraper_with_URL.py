from selenium import webdriver
import requests
import os
import time
import io
from PIL import Image
import hashlib
import msvcrt

'''
Web Image Scraper
- Give this a URL, you get the image.

Original Author 
-"Fabian Bosler" on towardsdatascience.com 
[https://towardsdatascience.com/image-scraping-with-python-a96feda8af2d]
- "eamander" on GitHub [https://github.com/eamander/Pinterest_scraper]

Code Modified by
- JungBae Park (Joseph Park)
'''

class InputManager(object):
    def __init__(self):
        self.print_menu()
        self.img_source = None

    def print_menu(self):
        print("""

            Web Image Scraper_ver 1.11
            - Give it the URL, you get the image.

            Original Author 
            -"Fabian Bosler" on towardsdatascience.com 
            [https://towardsdatascience.com/image-scraping-with-python-a96feda8af2d]
            - "eamander" on GitHub [https://github.com/eamander/Pinterest_scraper]

            Code Modified by
            - JungBae Park (Joseph Park)

            """)

    def get_search_info(self):
        while self.img_source == None:
            URL = input("Please insert the URL containing images [Google] > ")
            img_source = self.verify_user_input(URL)
            if img_source != None:
                self.img_source = img_source
                break

        if img_source == "Google":
            print("""

                Current Image Source : Google

                """)
            return URL, None, None
        elif img_source == "Pinterest" :
            print("""

                Current Image Source : Pinterest

                """)
            login_Pinterest_ID = input("Please insert your ID on Pinterest > ")
            login_Pinterest_PWD = input("Please insert your Password on Pinterest")
            return print("Pinterest features hasn't been updated yet")

    def get_destination_folder(self):
        folder_name = None
        folder_location = None

        folder_location = input("Please insert the destination to save image > ")
        folder_name = input("How would you name your image folder? > ")
        return os.path.join(folder_location,'_'.join(folder_name.split(' ')))

    def get_image_count(self):
        return int(input("How many images are you willing to download? > "))

    def verify_user_input(self, URL):
        src = None
        if URL.find("www.pinterest.co.kr") != -1:
            src = "Pinterest"
        elif URL.find("www.google.com") != -1:
            src = "Google"
        else:
            print("Error : Please insert the valid URL")
        return src

########## Fabian Bosler's Code, modified by JungBae Park ##########
class URLImageScraper(object):
    def __init__(self, driver_path):
        my_input_manager = InputManager()
        self.URL, self.login_Pinterest_ID, self.login_Pinterest_PWD = my_input_manager.get_search_info()
        self.folder_location = my_input_manager.get_destination_folder()
        self.max_download_count = my_input_manager.get_image_count()
        self.wd = webdriver.Chrome(executable_path=driver_path)
        self.num_of_downloads = 0
    
    def __del__(self):
        self.wd.quit()
        self.show_result()

    def search_and_download(self, driver_path):
        if not os.path.exists(self.folder_location):
            os.makedirs(self.folder_location)

        res = self.fetch_image_urls(wd= self.wd, sleep_between_interactions=0.5)
            
        for elem in res:
            self.persist_image(elem)
            self.num_of_downloads += 1

    def fetch_image_urls(self, wd:webdriver, sleep_between_interactions:int=1):
        def scroll_to_end(wd):
            self.wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(sleep_between_interactions)    
        
        # build the google query
        # load the page
        wd.get(self.URL)

        image_urls = set()
        download_count = 0
        results_start = 0
        while download_count < self.max_download_count:
            scroll_to_end(wd)

            # get all image thumbnail results
            thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
            number_results = len(thumbnail_results)
            
            print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
            
            for img in thumbnail_results[results_start:number_results]:
                # try to click every thumbnail such that we can get the real image behind it
                try:
                    img.click()
                    time.sleep(sleep_between_interactions)
                except Exception:
                    continue

                # extract image urls    
                actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
                for actual_image in actual_images:
                    if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                        image_urls.add(actual_image.get_attribute('src'))

                download_count = len(image_urls)

                if len(image_urls) >= self.max_download_count:
                    print(f"Found: {len(image_urls)} image links, done!")
                    break
            else:
                print("Found:", len(image_urls), "image links, looking for more ...")
                time.sleep(30)
                return
                load_more_button = wd.find_element_by_css_selector(".mye4qd")
                if load_more_button:
                    wd.execute_script("document.querySelector('.mye4qd').click();")

            # move the result startpoint further down
            results_start = len(thumbnail_results)

        return image_urls

    
    def persist_image(self, URL:str):
        try:
            image_content = requests.get(URL).content

        except Exception as e:
            print(f"ERROR - Could not download {URL} - {e}")

        try:
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert('RGB')
            file_path = os.path.join(self.folder_location,hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
            with open(file_path, 'wb') as f:
                image.save(f, "JPEG", quality=85)
            print(f"SUCCESS - saved {URL} - as {file_path}")
        except Exception as e:
            print(f"ERROR - Could not save {URL} - {e}")

    def show_result(self):
        print("""
            Process Finished

            Number of Downloaded Images : {num_of_dwn}
            Location of Folder containing Images : {folder_loc}
            """.format(
                num_of_dwn = self.num_of_downloads,
                folder_loc = self.folder_location)
            )

########## Fabian Bosler's Code, modified by JungBae Park ##########

def main():
    DRIVER_PATH = "./ChromeDriver/chromedriver.exe"
    my_image_scraper = URLImageScraper(DRIVER_PATH)
    my_image_scraper.search_and_download(DRIVER_PATH)
    del my_image_scraper

    query = input("Type anything to exit > ")
    if query != None:
        return

if __name__ == "__main__":
    main()