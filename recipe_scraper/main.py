# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 10:42:47 2022

@author: khila
"""



#%%

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
print(SCRIPT_DIR)
#%%
from utils.scraper import get_all_recipes
   
#%%  

recipes=get_all_recipes()

    
# %%
recipes
# %%
