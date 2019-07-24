#!/usr/bin/env python
# coding: utf-8

# In[101]:


# import data

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

energy_data = pd.read_csv('EnergyData201812.csv')

energy_data.head()

energy_data.dtypes


# In[102]:


# convert columns to date, to enable profiling by date

energy_data['startTime'] = pd.to_datetime(energy_data['startTime'])
energy_data['endTime'] = pd.to_datetime(energy_data['endTime'])

energy_data['startDate'] = energy_data.startTime.dt.date
energy_data['endDate'] = energy_data.endTime.dt.date

# check it has worked
energy_data.head(100)



# In[103]:


# only use relevant columns, and calculate weekday for profiling

energy_data = energy_data[['id','startTime','startDate','value']]

energy_data['startDate'] = pd.to_datetime(energy_data['startDate'])

energy_data['weekday'] = energy_data['startDate'].dt.day_name()

#check 
energy_data.head()


# In[104]:


#first step to calculate proportion of energy use across the week
#reset index to create dataframe

weekly_profile = energy_data.groupby(['weekday'])['value'].sum()

total_energy = energy_data.groupby(['weekday'])['value'].sum() / energy_data.value.sum() * 100

total_energy = total_energy.reset_index()

#check
total_energy.head(7)


# In[107]:


#reordering weekday column to flow in day order, make it easier to view profile change across the week
cats = [ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

total_energy['weekday'] = total_energy['weekday'].astype('category', categories=cats, ordered=True)

from pandas.api.types import CategoricalDtype
cat_type = CategoricalDtype(categories=cats, ordered=True)
total_energy['weekday'] = total_energy['weekday'].astype(cat_type)

total_energy = total_energy.sort_values("weekday")

total_energy_ordered =  total_energy.set_index("weekday")



# In[108]:


#plot bar chart

total_energy_ordered.plot(kind='bar')


# In[24]:


# confirming that all boilers used on similar days, this will identify problems/missing data

energy_days = energy_data.groupby(['id'])['startDate'].nunique()
                                   
energy_days.plot(kind='bar')


# In[32]:


# does total boiler volume vary across the set, and what is the distribution shape?

boiler_vol = energy_data.groupby(['id'])['value'].sum()

boiler_vol.head()

plt.hist(boiler_vol,bins=50)


# In[33]:


#plot actual variation to see min and max

boiler_vol.plot(kind='bar')


# In[34]:


# collect useful stats

boiler_vol.describe()


# In[35]:


# does individual boiler variation across the set, and what is the distribution shape?

boiler_var = energy_data.groupby(['id'])['value'].std()

boiler_var.plot(kind='bar')


# In[36]:


boiler_var.describe()


# In[37]:


plt.hist(boiler_var,bins=50)


# In[38]:


# aggregating total volume used to boiler level ahead of joining

energy_group = energy_data.groupby('id',as_index=False).agg({"value":"sum"})
                                   
energy_group


# In[40]:


#aggregating spread of data to boiler use, to join on total volume

energy_spread = energy_data.groupby('id',as_index=False).agg({"value":"std"})

energy_spread.columns= ["id", "spread"]


energy_spread


# In[41]:


#joining value and spread to create final table

energy_id = pd.merge(energy_group, energy_spread, on = ['id'], how = 'inner')

energy_id.head()


# In[44]:


# categorise volume according to size relative to the median, seems more sensible that the mean based on histogram

energy_id.loc[energy_id.value < energy_id.value.median(), 'Volume'] = 'Low'
energy_id.loc[energy_id.value >= energy_id.value.median(), 'Volume'] = 'High'
energy_id.head()


# In[45]:


# categorise spread according to size relative to the mean

energy_id.loc[energy_id.spread < energy_id.spread.mean(), 'Variation'] = 'Low'
energy_id.loc[energy_id.spread >= energy_id.spread.mean(), 'Variation'] = 'High'

energy_id.head()


# In[47]:


#check columns have pulled through correctly

energy_id = energy_id[['id','value','spread', 'Volume','Variation']]
energy_id.head()


# In[48]:


#categorise boiler ids by volume and variation

energy_id['Category'] = 0

energy_id.loc[(energy_id['Volume'] == 'High')  & (energy_id['Variation'] == 'High'), 'Category'] = 'High Vol High Variation'
energy_id.loc[(energy_id['Volume'] == 'High') & (energy_id['Variation'] == 'Low'), 'Category'] = 'High Vol Low Variation'
energy_id.loc[(energy_id['Volume'] == 'Low')  & (energy_id['Variation'] == 'High'), 'Category'] = 'Low Vol High Variation'
energy_id.loc[(energy_id['Volume'] == 'Low')  & (energy_id['Variation'] == 'Low'), 'Category'] = 'Low Vol Low Variation'

energy_id.head(5)  


# In[51]:


#finally group boilers into meaningful categories

energy_categorised = energy_id[['id','Category']]

energy_categorised.loc[energy_categorised.Category == 'High Vol High Variation', 'Forecast'] = 'Volatile'
energy_categorised.loc[energy_categorised.Category == 'High Vol Low Variation', 'Forecast'] = 'Stable'
energy_categorised.loc[energy_categorised.Category == 'Low Vol High Variation', 'Forecast'] = 'Spiky'
energy_categorised.loc[energy_categorised.Category == 'Low Vol Low Variation', 'Forecast'] = 'Stable'


energy_categorised.head()


# In[53]:


#view final table

energy_categorised = energy_categorised[['id','Forecast']]

energy_categorised.head()


# In[56]:


#create graph to show distribution of categories

energy_categorised_count = energy_categorised.groupby(['Forecast'])['id'].count()
energy_categorised_count.head()

energy_categorised_count.plot(kind='bar')


# In[ ]:




