# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 11:30:07 2022

@author: khila
"""
#%%
import recipe_scraper
#%%
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
print(SCRIPT_DIR)

from recipe_scraper.utils.scraper import get_all_recipes
   
   
   
          
    
    
    
    

def main():
    
    get_all_recipes()



if __name__ == "__main__":
    print("executing")
    main()
    