# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 10:42:47 2022

@author: khila
"""

import time

from selenium import webdriver

from dotenv import load_dotenv
import os


load_dotenv()


driver = webdriver.Chrome(os.getenv('PATH_TO_CHROMEDRIVER'))  # Optional argument, if not specified will search path.

driver.get('http://www.bbc.co.uk/');

time.sleep(5) # Let the user actually see something!

search_box = driver.find_element_by_name('q')

search_box.send_keys('ChromeDriver')

search_box.submit()

time.sleep(5) # Let the user actually see something!

driver.quit()


#https://www.bbc.co.uk/food/ingredients/a-z/a/2#featured-content


#%%

from bs4 import BeautifulSoup

import time

from selenium import webdriver

from dotenv import load_dotenv
import re
import os


load_dotenv()

from time import process_time

#%%

class BBCFoodRecipeExtractor:
    
    """
    A class to extract recipe and review data from BBC food recipes
    """
    def __init__(self, webdriver_path=os.getenv('PATH_TO_CHROMEDRIVER')):
        self.webdriver_path = webdriver_path
        self.url = False
        self.no_reviews=False
        
        
    def get_bs4(self, url, retry=False):
        
        if url==self.url and retry==False:
            
            return self.soup
        driver = webdriver.Chrome(self.webdriver_path)
        driver.get(url)
        html = driver.page_source
        driver.close()
        self.html = html
        self.soup = BeautifulSoup(html,'html.parser')
        self.url = url
        return self.soup
    
    def get_rating(self, url, retry=False):
        self.get_bs4(url, retry)
        reviewed = self.soup.find(class_="recipe-ratings")
        pattern = 'Be the first to rate this recipe'
        if re.search(pattern, str(reviewed)):
            self.no_reviews = True
            print("not reviewed")
            return None
        else:
            rating_tag = self.soup.find(class_="aggregate-rating")
            str_tag=str(rating_tag)
            pattern = 'aria-label="[^>]+'
            rating_text=re.search(pattern, str_tag).group(0)
            
            rating=0
            if "half" in rating_text:
                rating+=0.5
                
            for i in range(1,5):
                if str(i) in rating_text:
                    rating+=i
            if "5 of 5" in rating_text:
                    rating=5
            elif rating==0:
                    rating=None
            return rating
            
    def get_review_numbers(self, url, retry=False):
        self.get_bs4(url, retry)
        reviewed = self.soup.find(class_="recipe-ratings")
        pattern = 'Be the first to rate this recipe'
        if re.search(pattern, str(reviewed)):
            self.no_reviews = True
            print("not reviewed")
            return None
        else:
            review_no_tag=self.soup.find(class_="aggregate-rating__total gel-long-primer-bold")
            str_review_no = str(review_no_tag)
            pattern = '\d+ ratings'
            review_text=re.search(pattern, str_review_no).group(0)
            review_num=[int(s) for s in review_text.split() if s.isdigit()][0]
            
            return review_num
        
    def get_ingredients(self, url, retry=False):
        self.get_bs4(url, retry)
        ingredients=self.soup.find_all(class_="recipe-ingredients__list-item")
        
        ingredient_list=[ingredient.get_text() for ingredient in ingredients]
        
        return ingredient_list
    
    def get_method(self, url, retry=False):
        self.get_bs4(url, retry)
        method=self.soup.find_all(class_="recipe-method__list-item-text")
        step_list=[step.get_text() for step in method]
        return step_list
    
    def get_all(self, url, retry=False):
        rating = self.get_rating(url,retry)
        review_nums = self.get_review_numbers(url, retry)
        ingredients = self.get_ingredients(url, retry)
        method = self.get_method(url, retry)
        
        return {'rating':rating, 'review_nums':review_nums, 'ingredients':\
                ingredients, 'method':method}

#%%
t1_start = process_time() 
extractor=BBCFoodRecipeExtractor()

url='https://www.bbc.co.uk/food/recipes/beef_bulgogi_88615'

recipe=extractor.get_all(url)
t1_stop = process_time()

print("Elapsed time:", t1_stop, t1_start) 
   
print("Elapsed time during the whole program in seconds:",
                                         t1_stop-t1_start) 
#%%
        
'''
def get_recipe_data(url):
    url = "https://www.bbc.co.uk/food/recipes/smoky_roasted_tomato_39800"
    
    browser = webdriver.Chrome(os.getenv('PATH_TO_CHROMEDRIVER'))
    browser.get(url)
    html = browser.page_source
    browser.close()
    
    
    soup = BeautifulSoup(html,'html.parser')
    
    pattern = 'Be the first to rate this recipe'
    reviewed=soup.find(class_="recipe-ratings")
    
    if re.search(pattern, str(reviewed)):
        
        print("not reviewed")
        return None, 0, None, None
    
    else:
    
        rating_tag=soup.find(class_="aggregate-rating")
        
        str_tag=str(rating_tag)
        
        pattern = 'aria-label="[^>]+'
        
        rating_text=re.search(pattern, str_tag).group(0)
        
        rating=0
        
        if "half" in rating_text:
            print("half")
            rating+=0.5
            
        for i in range(1,5):
            if str(i) in rating_text:
                rating+=i
        if "5 of 5" in rating_text:
                rating=5
        elif rating==0:
                rating=None
                
        print(str(rating) + " out of 5")
        
        
        
        review_no_tag=soup.find(class_="aggregate-rating__total gel-long-primer-bold")
        
        str_review_no = str(review_no_tag)
        
        pattern = '\d+ ratings'
        
        review_text=re.search(pattern, str_review_no).group(0)
        
        review_num=[int(s) for s in review_text.split() if s.isdigit()][0]
        
        print("review number:  " + str(review_num))
        
    
    ingredients=soup.find_all(class_="recipe-ingredients__list-item")
    
    for ingredient in ingredients:
        print(ingredient.get_text())
        
    
    
    methods=soup.find_all(class_="recipe-method__list-item-text")
    
    for method in methods:
        print(method.get_text())
        '''