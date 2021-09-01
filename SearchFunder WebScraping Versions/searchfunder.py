#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import re
import time

import pandas as pd
import lxml
from bs4 import BeautifulSoup

pd.options.display.max_rows = 4000


# In[2]:


URL = 'https://www.searchfunder.com'

session = requests.session()

front = session.get(URL)
csrf_token = re.findall(r'<input type="hidden" name="_token" value="(.*)"', 
front.text)[0]

cookies = session.cookies

payload = {
    'email': 'danny.salzman@chicagobooth.edu',
    'password': '!y4^%gY6z3IQ',
    '_token': csrf_token,
}

r = requests.post(URL + '/auth/login', data=payload, cookies=cookies)


# In[3]:


searchfunds_HTML = requests.get(URL + '/searchfund/allsearchfunds', cookies=r.cookies)


# In[5]:


datasearchfund_id = re.findall('data-searchfund_id="[0-9]+"',searchfunds_HTML.text)
searchfund_data_index = list(map(int,re.findall('[0-9]+',str(datasearchfund_id))))


# In[6]:


table = pd.read_html(searchfunds_HTML.text)
searchfunds = table[0][table[0]['name'].notna()]
searchfunds = searchfunds.reset_index()
searchfunds.index = searchfund_data_index
cols = [0,1]
searchfunds.drop(searchfunds.columns[cols], axis=1,inplace=True)
#searchfunds.to_csv("searchfund_raw2.csv")


# In[7]:





# In[366]:


enrichment = []


# In[332]:


enrichment.loc[enrichment['searchfund_index'] == 10]


# In[365]:


type(searchfund_data_index[-1])


# In[367]:


enrichment = []
for index in searchfund_data_index:
    print(index)
    data = requests.get(URL + '/searchfund/ajaxsearchfundrow/'+str(index), cookies=r.cookies)
    time.sleep(0.05)
    soup = BeautifulSoup(data.content, 'html.parser')
    
    ## Get company info
    company_rows=soup.find_all(class_="col-md-3")
    try:
        searchWebsite = re.split(r'\t+',company_rows[0].text)[1].strip('\n')
    except:
        searchWebsite = ""
    try:
        companyWebsite= re.split(r'\t+',company_rows[1].text)[1].strip('\n')
    except:
        companyWebsite=""
    try:
        industry = re.split(r'\t+',company_rows[2].text)[1].strip('\n')
    except:
        industry=""
    try:
        location = re.split(r'\t+',company_rows[3].text)[1].strip('\n')
    except:
        location=""

    
    
    ## Get Searcher info
    searchers=[]
    try:
        searcher_rows=soup.find_all(class_="col-md-12")[0]
        for searcher_row in searcher_rows:
            try:
                searchers.append(re.split(r'\t+',searcher_row.text)[-1].strip('\n'))
            except:
                searchers.append("")
        searchers = list(filter(None, searchers))
    except:
        searchers


    ## Get Investor info
    investors=[]
    try:
        investor_rows=soup.find_all(class_="col-md-12")[2]
        for investor_row in investor_rows:
            try:
                investors.append(re.split(r'\t+',investor_row.text)[-1].strip('\n'))
            except:
                investors.append("")
        investors = list(filter(None, investors))
    except:
        investors

    ## Get Associate info
    associates=[]
    try:
        associate_rows=soup.find_all(class_="col-md-12")[4]
        for associate_row in associate_rows:
            try:
                associates.append(re.split(r'\t+',associate_row.text)[-1].strip('\n'))
            except:
                associates.append("")
        associates = list(filter(None, associates))
    except:
        associates
    
    enrichmentData = {'searchfund_index': index, 'searchWebsite': searchWebsite,'companyWebsite': companyWebsite,'industry':industry,'location':location,'searchers':searchers,'investors':investors,'associates':associates}
    #print(enrichmentData)
    enrichment.append(enrichmentData)
    
    


# In[368]:


enrichmentDF = pd.DataFrame(enrichment)


# In[193]:


data = requests.get(URL + '/searchfund/ajaxsearchfundrow/6', cookies=r.cookies)


# In[194]:


soup = BeautifulSoup(data.content, 'html.parser')


# In[195]:


## Get company info
company_rows=soup.find_all(class_="col-md-3")
try:
    searchWebsite = re.split(r'\t+',company_rows[0].text)[1].strip('\n')
except:
    searchWebsite = ""
try:
    companyWebsite= re.split(r'\t+',company_rows[1].text)[1].strip('\n')
except:
    companyWebsite=""
try:
    industry = re.split(r'\t+',company_rows[2].text)[1].strip('\n')
except:
    industry=""
try:
    location = re.split(r'\t+',company_rows[3].text)[1].strip('\n')
except:
    location=""
    
    
## Get Searcher info
searchers=[]
try:
    searcher_rows=soup.find_all(class_="col-md-12")[0]
    for searcher_row in searcher_rows:
        try:
            searchers.append(re.split(r'\t+',searcher_row.text)[-1].strip('\n'))
        except:
            searchers.append("")
    searchers = list(filter(None, searchers))
    print(searchers)
except:
    searchers
    
    
## Get Investor info
investors=[]
try:
    investor_rows=soup.find_all(class_="col-md-12")[2]
    for investor_row in investor_rows:
        try:
            investors.append(re.split(r'\t+',investor_row.text)[-1].strip('\n'))
            index= index +1
        except:
            investors.append("")
    investors = list(filter(None, investors))
    print(investors)
except:
    investors
    
## Get Associate info
associates=[]
try:
    associate_rows=soup.find_all(class_="col-md-12")[4]
    for associate_row in associate_rows:
        try:
            associates.append(re.split(r'\t+',associate_row.text)[-1].strip('\n'))
        except:
            associates.append("")
    associates = list(filter(None, associates))
    print(associates)
except:
    associates


# In[352]:


enrichmentDF


# In[382]:


#searchfunds = pd.merge([searchfunds, enrichment], how='right',on='searchfund_index')

merged = pd.merge(searchfunds, enrichmentDF, left_index=True, right_on='searchfund_index')
merged


# In[383]:


merged['name'] = merged['name'].str.split("|", n = 1, expand = True)[0]
merged['formed'] = merged['formed'].str.split(" ", n = 1, expand = True)[0]
merged['acquired'] = merged['acquired'].str.split(" ", n = 1, expand = True)[0]


# In[385]:


#merged['formed'] = pd.to_datetime(merged['formed'].dropna, format='%Y%m%d')
merged


# In[386]:


merged.to_csv("searchfund_allV3.csv")


# In[315]:


searchfunds.loc[10]


# In[12]:


ndcaTable = pd.DataFrame(None)
for index in range(0,9): 
    ndcaURL = 'https://nadca.com/find-a-professional?distance%5Bpostal_code%5D=&distance%5Bcountry%5D=us&distance%5Bsearch_distance%5D=100&distance%5Bsearch_units%5D=mile&province=All&country=us&title=&emp_admin_first_name=&emp_admin_last_name=&title_1=&field_company_admin_value=&field_employee_certification_tid=All&field_company_job_type_tid=All&field_company_services_tid=All&items_per_page=100&page='+str(index)
    ndcaData = requests.get(ndcaURL)
    ndcaTable = ndcaTable.append(pd.read_html(ndcaData.text)[0])




# In[7]:


ndcaTable


# In[ ]:




