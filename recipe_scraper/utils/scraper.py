# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 12:12:37 2022

@author: khila
"""
#%%
from bs4 import BeautifulSoup

import time

from selenium import webdriver

from dotenv import load_dotenv
import re
import os
import string

import numpy as np
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.chrome.service import Service
import json
load_dotenv()

from os import listdir



#%%
def recipe_info_extractor(recipe_urls, driver, json_file):
    
    extractor=BBCFoodRecipeExtractor(driver)
    extracted_recipes=[]
    i=0
    for url in recipe_urls:
        info=extractor.get_all(url)
        extracted_recipes.append(info)
        i+=1
        
        if i%10==0:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(extracted_recipes, f, ensure_ascii=False, indent=4)

    with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(extracted_recipes, f, ensure_ascii=False, indent=4)


    return extracted_recipes


class BBCFoodRecipeExtractor:
    
    """
    A class to extract recipe and review data from BBC food recipes
    """
    def __init__(self, driver=False, webdriver_path=os.getenv('PATH_TO_CHROMEDRIVER')):
        
        if driver:
            self.driver=driver
            self.close_driver=False
        else:
            self.driver=_setup_webdriver()
            self.close_driver=True
        self.webdriver_path = webdriver_path
        self.url = False
        self.no_reviews=False
        
    

    def get_bs4(self, url, retry=False):
        
        if url==self.url and retry==False:
            
            return self.soup

        self.driver.get(url)
        html = self.driver.page_source
        self.html = html
        if retry:
            time.sleep(2)
        self.soup = BeautifulSoup(html,'html.parser')
        self.url = url
        '''
        if self.close_driver:
            self.driver.close()
        '''

        if self.soup.find(class_="page-title__logo")==None:
            food_title=None
        else:
            food_title=self.soup.find(class_="page-title__logo").get_text()

        if food_title==None or food_title!='Food' \
            or 'OccasionsCuisinesIngredientsDishesCollections' not in self.soup.get_text():
        
            if retry==False:
                retry=1
            else:
                retry+=1
            
        
            time.sleep(10*retry)
        
            if retry<4:
                print(f"BBC Food timed out attempting retry {retry}")
                self.soup = self.get_bs4(url, retry)
        
            else:
                print("BBC Food extraction failed")
                print(url)

        return self.soup

    def check_recipe_not_found(self, url, retry=False):
        self.get_bs4(url, retry)
        if self.soup.find(class_="recipe-not-found__text gel-trafalgar")==None:
            return False
        else:
            return True





    def get_rating(self, url, retry=False):
        self.get_bs4(url, retry)
        if self.check_recipe_not_found(url):
            return None

        reviewed = self.soup.find(class_="recipe-ratings")
        pattern = 'Be the first to rate this recipe'
        if re.search(pattern, str(reviewed)):
            self.no_reviews = True
            #print("not reviewed")
            return None
        else:
            rating_tag = self.soup.find(class_="aggregate-rating")
            str_tag=str(rating_tag)
            pattern = '\d of 5 stars|\d and a half of 5 stars'
            if re.search(pattern, str_tag)==None:
                return self.get_rating(url,retry=0)
            rating_text=re.search(pattern, str_tag).group(0)
            
            rating=float(rating_text[0])

            
            if "half" in rating_text:
                rating+=0.5

            return rating
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
        if self.check_recipe_not_found(url):
            return None
        reviewed = self.soup.find(class_="recipe-ratings")
        pattern = 'Be the first to rate this recipe'
        if re.search(pattern, str(reviewed)):
            self.no_reviews = True
            #print("not reviewed")
            return None
        else:
            review_no_tag=self.soup.find(class_="aggregate-rating__total gel-long-primer-bold")
            str_review_no = review_no_tag.get_text()
            pattern = '\d+ rating'
            review_text=re.search(pattern, str_review_no).group(0)
            review_num=[int(s) for s in review_text.split() if s.isdigit()][0]
            
            return review_num
        
    def get_ingredients(self, url, retry=False):
        self.get_bs4(url, retry)
        if self.check_recipe_not_found(url):
            return None
        ingredients=self.soup.find_all(class_="recipe-ingredients__list-item")
        
        ingredient_list=[ingredient.get_text() for ingredient in ingredients]
        
        return ingredient_list
    
    def get_method(self, url, retry=False):
        if self.check_recipe_not_found(url):
            return None
        self.get_bs4(url, retry)
        method=self.soup.find_all(class_="recipe-method__list-item-text")
        step_list=[step.get_text() for step in method]
        return step_list
    
    def get_title(self, url, retry=False):
        if self.check_recipe_not_found(url):
            return 'Recipe not found - invalid URL'

        self.get_bs4(url, retry)
        title=self.soup.find(class_="gel-trafalgar content-title__text")
        
        return title.get_text()


    def get_all(self, url, retry=False):
        rating = self.get_rating(url,retry)
        review_nums = self.get_review_numbers(url, retry)
        ingredients = self.get_ingredients(url, retry)
        method = self.get_method(url, retry)
        title = self.get_title(url, retry)
        
        return {'title':title, 'rating':rating, 'review_nums':review_nums, 'ingredients':\
                ingredients, 'method':method, 'url':url}

 

#%%


def _setup_webdriver(path=os.getenv('PATH_TO_CHROMEDRIVER')):
    service = Service(executable_path=path)
    driver=webdriver.Chrome(service=service)
    return driver

def _get_first_ingredient_page(splits=4):
    first_page_list = ['https://www.bbc.co.uk/food/ingredients/a-z/'+c for c in string.ascii_lowercase]
    split_first_page = np.array_split(first_page_list, splits)
    return split_first_page


def _get_ingredient_page_soup(url, driver):
    
    global failed_ingredient_links
        
    driver.get(url)
    html = driver.page_source
    current_url = driver.current_url
    soup = BeautifulSoup(html,'html.parser')
    
    if soup.find(class_="page-title__logo")==None:
        food_title=None
    else:
        food_title=soup.find(class_="page-title__logo").get_text()
    
    if food_title==None or food_title!='Food':
        print("BBC Food timed out")
        time.sleep(3)
        soup = _get_ingredient_page_soup(url,driver)
    
    
        
    if "a-z" not in current_url:
        #print("there are no other pages")
        pass
        
    return soup

def _get_recipe_url_soup(url, driver, ingredient_url, retry=False):
    driver.get(url)
    html = driver.page_source
    current_url = driver.current_url
    soup = BeautifulSoup(html,'html.parser')
    
        
    if "a-z" not in current_url:
        multiple_letters=False
    else:
        multiple_letters=True
        
    if soup.find(class_="page-title__logo")==None:
        food_title=None
    else:
        food_title=soup.find(class_="page-title__logo").get_text()

    if food_title==None or food_title!='Food' \
        or 'OccasionsCuisinesIngredientsDishesCollections' not in soup.get_text():
        
        if retry==False:
            retry=1
        else:
            retry+=1
            
        
        time.sleep(10*retry)
        
        if retry<4:
            print(f"BBC Food timed out attempting retry {retry}")
            soup, multiple_letters = _get_recipe_url_soup(url, driver, ingredient_url, retry)
        
        else:
            print("BBC Food extraction failed")
            print(url)
            failed_ingredient_links.append(ingredient_url)
        
    return soup, multiple_letters
    
def _get_max_page(soup):

    page_list=[]
    for link in soup.find_all(class_="pagination__link gel-pica-bold"):
        #print(link.get_text())
        try:
            page_list.append(int(link.get_text()))
        except:
            pass
    if len(page_list)==0:
        return 1
            
    return max(page_list)

def _get_ingredient_links(first_page_urls, driver):
    
    letters = [url[-1] for url in first_page_urls]
    letters=''.join(letters)
    filename=os.getenv('PATH_TO_ALPHABETIC_PAGE_LINKS')+'\\urls-alphabet-'+ letters + '.txt'
    all_page_list=[]
    for url in first_page_urls:
        page_count=_get_max_page(_get_ingredient_page_soup(url,driver))
        for page in range(page_count):
            page_no = page+1
            all_page_list.append(url+f'/{page_no}')
            #print(url+f'/{page_no}')
    
    with open(filename, 'w') as f:
        for url in all_page_list:
            f.write(f'{url}\n')



def get_all_ingredient_pages(splits=4):
    
    for file in listdir(os.getenv('PATH_TO_ALPHABETIC_PAGE_LINKS')):
        if 'urls-alphabet.txt'==file:
            file_path=os.path.join(os.getenv('PATH_TO_ALPHABETIC_PAGE_LINKS'),file)
            urls=[]
            with open(file_path, 'r') as f:
                for line in f.readlines():
                    urls.append(line)
            return [url.strip() for url in urls]
        
        
    split_first_page = _get_first_ingredient_page(splits)
    
    drivers = [_setup_webdriver() for _ in range(splits)]

    with ThreadPoolExecutor(max_workers=splits) as executor:
        executor.map(_get_ingredient_links, split_first_page, drivers)

    [driver.quit() for driver in drivers]
    
    urls=[]
    for file in listdir(os.getenv('PATH_TO_ALPHABETIC_PAGE_LINKS')):
        file_path=os.path.join(os.getenv('PATH_TO_ALPHABETIC_PAGE_LINKS'),file)
        
        with open(file_path, 'r') as f:
            for line in f.readlines():
                urls.append(line)
        
        os.remove(file_path)
    
    filename=os.getenv('PATH_TO_ALPHABETIC_PAGE_LINKS')+'\\urls-alphabet.txt'
    with open(filename, 'w') as f:
        for url in urls:
            f.write(f'{url}')

        
    return [url.strip() for url in urls]
                

def _get_ingredient_list(urls, driver):
    

        
    unique_id=urls[0][43]+urls[0][45]
    

    filename=os.getenv('PATH_TO_INGREDIENT_LIST_LINKS')+'\\urls-ingredients-'+ unique_id + '.txt'
    for url in urls:
        soup = _get_ingredient_page_soup(url, driver)
        ing_list=soup.find_all(class_="promo promo__ingredient",  href=True)
        ing_links=['https://www.bbc.co.uk' + a['href'] for a in ing_list]
        
    
        with open(filename, 'a') as f:
            for url in ing_links:
                f.write(f'{url}')
                f.write('\n')

def get_recipe_list(soup):
    link_list = soup.find_all('a', href=True)

    recipe_list=[]

    for a in link_list:
        
        if '/food/recipes/' in a['href']:
            recipe_list.append('https://www.bbc.co.uk'+a['href'])



    for a in soup.find_all(class_="gel-pica"):
        
        if "1 - NaN" in a.get_text():
            #print("no recipes")
            pass
            
    return recipe_list
        
    
    
def get_all_ingredients(splits=8):
    
    for file in listdir(os.getenv('PATH_TO_INGREDIENT_LIST_LINKS')):
        if 'urls-ingredients.txt'==file:
            file_path=os.path.join(os.getenv('PATH_TO_INGREDIENT_LIST_LINKS'),file)
            urls=[]
            with open(file_path, 'r') as f:
                for line in f.readlines():
                    urls.append(line)
            return [url.strip() for url in urls]
    
    urls=get_all_ingredient_pages(splits)
    
    split_urls = np.array_split(urls, splits)
    
    drivers = [_setup_webdriver() for _ in range(splits)]

    with ThreadPoolExecutor(max_workers=splits) as executor:
        executor.map(_get_ingredient_list, split_urls, drivers)

    [driver.quit() for driver in drivers]
    
    urls=[]
    for file in listdir(os.getenv('PATH_TO_INGREDIENT_LIST_LINKS')):
        file_path=os.path.join(os.getenv('PATH_TO_INGREDIENT_LIST_LINKS'),file)
        
        with open(file_path, 'r') as f:
            for line in f.readlines():
                urls.append(line)
        
        os.remove(file_path)
    
    filename=os.getenv('PATH_TO_INGREDIENT_LIST_LINKS')+'\\urls-ingredients.txt'
    with open(filename, 'w') as f:
        for url in urls:
            f.write(f'{url}')
            
    return [url.strip() for url in urls]
            



def _get_recipe_link(ingredient_url, driver):

    
    
    first_ingredient_url = ingredient_url + '/a-z/a/1'
    soup, multiple_letters = _get_recipe_url_soup(first_ingredient_url, driver, ingredient_url=ingredient_url)
    recipe_list=[]
    if multiple_letters:
        alpha_urls = [ingredient_url+'/a-z/'+c for c in string.ascii_lowercase]
        
        for url in alpha_urls:
            soup, _ = _get_recipe_url_soup(url, driver, ingredient_url=ingredient_url)
            recipe_list += get_recipe_list(soup)
            page_count=_get_max_page(soup)
            if page_count>1:
                for page in range(1,page_count):
                    page_no = page+1
                    page_url=url+f'/{page_no}'
                    
                    soup, _ = _get_recipe_url_soup(page_url, driver, ingredient_url=ingredient_url)
                    recipe_list += get_recipe_list(soup)
                    
    else:
        recipe_list = get_recipe_list(soup)
            
    ing_name=ingredient_url[27:]
    
    filename=os.getenv('PATH_TO_RECIPE_LINKS')+f'\\urls-{ing_name}.txt'
    with open(filename, 'a') as f:
        for url in set(recipe_list):
            f.write(f'{url}')
            f.write('\n')
    
    
    return recipe_list
    

def _get_recipe_links(ingredient_urls, driver):

    
    
    for ingredient_url in ingredient_urls:
        _get_recipe_link(ingredient_url, driver)
      
        
def get_all_recipes_urls(workers=8):
    
    global failed_ingredient_links
    failed_ingredient_links=[]
    
    for file in listdir(os.getenv('PATH_TO_RECIPE_LINKS')):
        if 'urls-recipes.txt'==file:
            file_path=os.path.join(os.getenv('PATH_TO_RECIPE_LINKS'),file)
            urls=[]
            with open(file_path, 'r') as f:
                for line in f.readlines():
                    urls.append(line)
            return [url.strip() for url in urls]
    
    ingredients=get_all_ingredients(workers)
    exclude_ingredient=[]
    for file in listdir(os.getenv('PATH_TO_RECIPE_LINKS')):
        for ingredient in ingredients:
            if file[5:-4] in ingredient:
                exclude_ingredient.append(ingredient)
                
    
    ingredients=[ing for ing in ingredients if ing not in exclude_ingredient]
            
        
        #urls-{ing_name}.txt
    
    
    split_urls = np.array_split(ingredients, workers)
    drivers = [_setup_webdriver() for _ in range(workers)]

    with ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(_get_recipe_links, split_urls, drivers)

    [driver.quit() for driver in drivers]
    
    if failed_ingredient_links!=[]:
        driver = _setup_webdriver()
        for ingredient_url in set(failed_ingredient_links):
            _get_recipe_links(ingredient_url, driver)
       
    
    urls=[]
    for file in listdir(os.getenv('PATH_TO_RECIPE_LINKS')):
        file_path=os.path.join(os.getenv('PATH_TO_RECIPE_LINKS'),file)
        
        with open(file_path, 'r') as f:
            for line in f.readlines():
                urls.append(line)
        
        os.remove(file_path)
    
    filename=os.getenv('PATH_TO_RECIPE_LINKS')+'\\urls-recipes.txt'
    with open(filename, 'w') as f:
        for url in set(urls):
            f.write(f'{url}')
            
    return [url.strip() for url in urls]

def manage_recipe_files(recipes=[], delete=True):


    for file in listdir(os.getenv('PATH_TO_RECIPES')):
        file_path=os.path.join(os.getenv('PATH_TO_RECIPES'),file)
            
        with open(file_path, 'r', encoding='utf-8') as f:
            recipe_section=json.load(f)
            recipes+=recipe_section
        if delete:
            os.remove(file_path)

    return recipes

#%%
def get_all_recipes(workers=12,urls=False):

    



    for file in listdir(os.getenv('PATH_TO_RECIPES')):
        if 'recipes.json'==file:
            file_path=os.path.join(os.getenv('PATH_TO_RECIPES'),file)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                recipes=json.load(f)

            return recipes

    if urls==False:
        urls=get_all_recipes_urls(workers)

    recipes_extracted = manage_recipe_files()
    if recipes_extracted!=[]:
        with open(os.getenv('PATH_TO_RECIPES')+'\\old_recipes.json', 'w', encoding='utf-8') as f:
            json.dump(recipes_extracted, f, ensure_ascii=False, indent=4)
    
    exclude_url=[recipe['url'] for recipe in recipes_extracted]

    urls=[url for url in urls if url not in exclude_url]
    

    split_urls = np.array_split(urls, workers)
    drivers = [_setup_webdriver() for _ in range(workers)]
    json_filenames = [os.getenv('PATH_TO_RECIPES') +f'\\recipe_part_{i}.json' for i in range(workers)]


    with ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(recipe_info_extractor, split_urls, drivers, json_filenames)

    [driver.quit() for driver in drivers]
  
    recipes = manage_recipe_files()

    non_duplicate_recipes = [i for n, i in enumerate(recipes) if i not in recipes[n + 1:]]

    with open(os.getenv('PATH_TO_RECIPES')+'\\recipes.json', 'w', encoding='utf-8') as f:
        json.dump(non_duplicate_recipes, f, ensure_ascii=False, indent=4)

    return recipes





# %%
import pandas as pd

df=pd.DataFrame(get_all_recipes())
df=df[df.review_nums>10]
df_num=df[['rating', 'review_nums']]
# %%
df_num.plot.scatter('review_nums', 'rating')

# %%
