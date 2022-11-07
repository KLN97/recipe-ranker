# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 10:42:47 2022

@author: khila
"""




#%%
from utils.scraper import get_all_recipes
   


# %%
import pandas as pd

df=pd.DataFrame(get_all_recipes())
df=df[df.review_nums>10]
df_num=df[['rating', 'review_nums']]
# %%
df_num.plot.scatter('review_nums', 'rating')

# %%
df_num.groupby('rating').count()
# %%
