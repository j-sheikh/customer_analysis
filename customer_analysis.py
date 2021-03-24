# -*- coding: utf-8 -*-
from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import re
import datetime as dt

data = pd.read_table("/content/drive/My Drive/31-M29/orders_train.txt",sep = ";")
print("Number of rows: {0:,}".format(len(data)))
print("Number of columns: {0:,}".format(len(data.columns)))

display(data.head())
print('\n Data Types:')
print(data.dtypes)

def color(val):
    color = "green"
    if val > 0:
        color = "lightcoral"
    if val > 10:
        color = "red"
    return 'background-color: %s' % color

A = data.describe().transpose()
B = pd.DataFrame(data.isna().sum()).rename(columns={0:"num missing"}, inplace=False)
B["pct missing in data"] = B["num missing"] / len(data) * 100

C = A.join(B, how="left")

display(C[["count", "min", "25%", "mean", "50%", "75%", "max", "std", "pct missing in data"]].round(3).style.applymap(color, subset=["pct missing in data"]))

def display_distribution(values_in, title, min_value=None, max_value=None):
    values = list(values_in.dropna())
    
    num_bins   = min(20, len(set(values)))
    log_prefix = ""
    
    if min_value != None:
        values = [max(min_value,x) for x in values]
    if max_value != None:
        values = [min(max_value,x) for x in values]
    
    if (min(values) > 0) & ((np.mean(values) > 2*np.median(values)) | (np.mean(values) < .75*np.median(values))):
        log_prefix = "log "
        values     = [np.log(x) for x in values] 
        
    plt.figure(figsize=(10,4))
    plt.hist(values, bins=num_bins)
    plt.xlabel("{0}Value".format(log_prefix))
    plt.ylabel("Frequency")
    plt.title("{0}\nLog of Values".format(title))
    plt.tight_layout()
    plt.show()

for ff in sorted(data.columns):
    if (data[ff].dtype == "float64") | (data[ff].dtype == "int64"):
        display_distribution(data[ff], "Feature Distribution of {0}".format(ff))

"""**Get unique values of all columns**"""

def all_unique_values_method(data):
  for col_name in data.columns:
    if data[col_name].dtypes == 'object':
      unique_cat = len(data[col_name].unique())
      unique_item_cat = data[col_name].unique()
      print(f"Feature {col_name} has {unique_cat} unique values")
      
all_unique_values_method(data)

"""**Note:** Through data.head() i saw that **deliveryDate** has had a question mark as entry value and in addition with a quick view in the PDF-Files of the DMC_task_2014.zip,i knew that **'?'** stands for missing values and also which feature contains missing values.
**check datecolumn for wrong/missing values**
Because the values in the different date columns has mostly the same form(yyyy-mm-dd),i specified the regex for especially these form.I can change the regex later for different dates,if a new dataset requires these.
"""

date_check_list = ['orderDate','deliveryDate','dateOfBirth','creationDate']

for x in date_check_list:
  wrong_value = []
  for y in data[x]:
    if re.search(r"[0-9]{4}-[0-9]{2}-[0-9]{2}",y) == None:
      wrong_value += y
  len_wrong_value = len(wrong_value)
  wrong_value_array = np.array(wrong_value) 
  wrong_value_unique = np.unique(wrong_value_array)
  print(f"Feature {x} has {len_wrong_value} wrong values:{wrong_value_unique}.")

"""I confirmed that 3 of the 4 date features contains the **?** which stands for a missing value.
In order to convert the date features into a datetime type i have to change the **?** to a missing value PANDAS can interpret.
"""

for x in date_check_list:
    data.loc[data[x] == '?',[x]] = np.nan
print(data.isna().sum())

"""**Checking for the five lowest and highest values in the date columns,to find outliers**"""

for x in date_check_list:
  lowestdate = data[x].sort_values()[:5]
  highestdate = data[x].sort_values(ascending = False)[:5]
  print(f"Feature \033[1m{x}\033[0;0m has the following five lowest values:\n{lowestdate}.\nand \033[1m{x}\033[0;0m the five highest values:\n{highestdate}")

"""dateOfBirth has outliers.The lowest five values are 1655-04-19 and 1900-11-19.
Checking these.
We also can see that **creationDate** and **orderDate** end at the *31-03-2013*,deliveryDate at *22-07-2013* .
"""

data[data.dateOfBirth <= '1900-11-19']

data[data.dateOfBirth == '1655-04-19']

(4041/481092)*100

"""We have 4038 customer with a dateOfBirth of 1900-11-19 and 3 customer with a dateOfBirth of 1655-04-19.
I decided to drop these 4041 rows because my guess is these are either values from the customers,who decided not to enter there real birthdate(privacy reasons) or manually created missing values form the company.Non or less these dates are outliers of the feature birthOfDate and only represent 0.84% of the overall observations.
"""

data.shape

data = data.drop(data[data.dateOfBirth <= '1900-11-19'].index)

data.shape

"""**Now i can convert the datetype** """

data['orderDate'] = pd.to_datetime(data['orderDate'])
data['deliveryDate'] = pd.to_datetime(data['deliveryDate'])
data['dateOfBirth'] = pd.to_datetime(data['dateOfBirth'])
data['creationDate'] = pd.to_datetime(data['creationDate'])

data.info()

"""**Inspecting and investigate categorical features.**"""

unique_values_list_cat = ['size','color','salutation','state']

for x in unique_values_list_cat:
  unique_values_cat = data[x].unique()
  len_unique_values_cat = len(unique_values_cat)
  print(f"Feature \033[1m{x}\033[0;0m has {len_unique_values_cat} unique categories:\n {unique_values_cat}.")

"""Like i mentioned before, i know that color has missing values and i can confirme that with the output above.
Besides that, some colors has doubles(brown/brwon,oliv/olive and blue/blau).
Also i detect that we have different size values,which represent most likely different cloth types.
"""

sorted(data.color.unique())

"""**Merge doubles**
For colors :
"""

data['color'] = data['color'].replace(to_replace = 'brwon',value = 'brown')
data['color'] = data['color'].replace(to_replace = 'blau',value = 'blue')
data['color'] = data['color'].replace(to_replace = 'oliv',value = 'olive')

"""For size:"""

data['size'] = data['size'].replace(to_replace = 'xxl',value = 'XXL')
data['size'] = data['size'].replace(to_replace = 'xl',value = 'XL')
data['size'] = data['size'].replace(to_replace = 'm',value = 'M')
data['size'] = data['size'].replace(to_replace = 'l',value = 'XL')
data['size'] = data['size'].replace(to_replace = 's',value = 'S')
data['size'] = data['size'].replace(to_replace = 'xs',value = 'XS')
data['size'] = data['size'].replace(to_replace = 'xxxl',value = 'XXXL')

all_unique_values_method(data)

"""**Finding missing values in categorical features**"""

def unique_values_list_cat_method():
  for x in unique_values_list_cat:
    missing_value = []
    for y in data[x]:
     if y == '?':
        missing_value += y
    len_missing_value = len(missing_value)
    missing_value_array = np.array(missing_value)
    missing_value_unique = np.unique(missing_value_array)
    print(f"Feature {x} has {len_missing_value} missing values:{missing_value_unique}.")
    
unique_values_list_cat_method()

"""**Giving the missing value *?* a better description**"""

data['color'] = data['color'].replace(to_replace = '?',value = 'unknown')

unique_values_list_cat_method()

"""**Change category data features to type category**"""

data['size'] = data['size'].astype('category')
data['color'] = data.color.astype('category')
data['salutation'] = data.salutation.astype('category')
data['state'] = data.state.astype('category')
print(data.dtypes)

"""**Compare the dates with each other to search for contradictions**"""

data[data.deliveryDate < data.orderDate]

data[data.deliveryDate == data.orderDate].head()

"""We have deliveries at the same day of the order.I think they make sense,due to express delivery options."""

data[data.creationDate <= data.dateOfBirth]

data[data.deliveryDate <= data.creationDate]

data[data.orderDate < data.creationDate]

"""There are some contradictions in the different dates for some customer.For later useig i drop these misleading rows."""

data.shape

data = data.drop(data[data.deliveryDate < data.orderDate].index)
data = data.drop(data[data.deliveryDate < data.creationDate].index)
data = data.drop(data[data.creationDate < data.dateOfBirth].index)

data.shape

"""**Checking for duplicated rows**"""

data.duplicated().sum()

"""**Diving deeper into the missing values**"""

no_deliveryDate = data['deliveryDate'].isna()
no_dateOfBirth = data['dateOfBirth'].isna()

data[no_deliveryDate]

data[(no_deliveryDate) & (data.returnShipment == 1)]

data[(no_deliveryDate)&(data.returnShipment == 0)]

data[(no_dateOfBirth)&(no_deliveryDate)]

"""All missing values for deliveryDate has no returnShipment,what seems logical,because you can't return a package u didn't get.We know that deliveryDate tracks the record until 22-07-2013, so normally a package ordered in March should be delivered until July.Therefore i drop these rows,because there are no more informatinos,why the package is missing and therefore not valid to use."""

data.shape

data = data.drop(data[(no_deliveryDate)&(data.returnShipment == 0)].index)

data.shape

data[(no_dateOfBirth)&(no_deliveryDate)]



"""Seems like we also got rid of all rows,where dateOfBirth was missing and we had not delivery."""

data.isna().sum()

len(data)

data[no_dateOfBirth]['returnShipment'].value_counts()

"""The only missing values we have left is the dateOfBirth column with about 10% missing data.For the reason that the customers with noBirthDate returned and kept there packages is almost 50/50 i decided to drop these values,to get rid of all missing values.
**Note:** I tried to predict the *Age* of the customers with different methods from sklearn(e.g. Imputer),but couldn't achieve something useful. My thought was that i could use the mean age of all customers with the same salutation and which item they purchased.I also tried something with groupby,but with no valid data.
"""

data = data.drop(data[no_dateOfBirth].index)

data.isna().sum()

data.info()

data.head()

"""**Adding a new feature age at order**"""

data['age'] = (data['orderDate'] - data['dateOfBirth']).astype('timedelta64[Y]')
data['age'] = data['age'].astype('Int64')

"""**Adding a new feature day of the week of orderDate and deliveryDate**"""

data['deliverytime'] = data.deliveryDate - data.orderDate
data['order_weekday']= data.orderDate.dt.dayofweek
data['order_weekday_name'] = data.orderDate.dt.weekday_name
data['delivery_weekday'] = data.deliveryDate.dt.dayofweek
data['delivery_weekday_name'] = data.deliveryDate.dt.weekday_name

data.head()

A = data.describe().transpose()
B = pd.DataFrame(data.isna().sum()).rename(columns={0:"num missing"}, inplace=False)
B["pct missing in data"] = B["num missing"] / len(data) * 100

C = A.join(B, how="left")

display(C[["count", "min", "25%", "mean", "50%", "75%", "max", "std", "pct missing in data"]].round(3).style.applymap(color, subset=["pct missing in data"]))

"""The range for age is from 0 to 112,which seems odd,because how should a born baby order something ? We can ask the same question for customer > 80 years old.It seems unlikley that there will be customer that old ordering prodcuts.
**Distribution of age**
"""

age_plot = sns.distplot(data.age)
age_plot.set_title("Distribution of age")
plt.show()

"""The age has a normal distribution.We can see that the age range is between 18-80 years old.It's unlikley to have a customer younger than 18 and over 80 years old.Therefore i remove all observations less than 18 and greater than 80"""

len(data.age[data.age < 18])

len(data.age[data.age > 80])

data.shape

data = data.drop(data[data.age < 18].index)
data = data.drop(data[data.age > 80].index)

data.shape

age_plot = sns.distplot(data.age)
age_plot.set_title("Distribution of age")
plt.show()

salutation_plot = sns.countplot('salutation',hue='returnShipment',data=data)
salutation_plot.set_xticklabels(salutation_plot.get_xticklabels(), fontsize=12)
salutation_plot.set_title("Distribution of all salutations(subdivided by returnShipment)")
for i in salutation_plot.patches:
    # get_x pulls left or right; get_height pushes up or down
    salutation_plot.text(i.get_x()+.0, i.get_height(), \
            str((i.get_height())), fontsize=10,
                color='black')
plt.tight_layout()
plt.show()

"""Most of the customers are females.They also tend to return the packages they ordered instead of keeping them."""

item_salutation = data.groupby(['salutation','itemID','size','manufacturerID']).size().to_frame("Count")
item_salutation = item_salutation.reset_index()

item_company = item_salutation['salutation'] =="Company"
item_family = item_salutation['salutation'] =="Family"
item_mr = item_salutation['salutation'] =="Mr"
item_mrs = item_salutation['salutation'] =="Mrs"
item_not_reported = item_salutation['salutation'] =="not reported"

top_item_company = item_salutation[item_company].sort_values(by = 'Count', ascending = False)[:10]
top_item_family = item_salutation[item_family].sort_values(by = 'Count', ascending = False)[:10]
top_item_mr = item_salutation[item_mr].sort_values(by = 'Count', ascending = False)[:10]
top_item_mrs = item_salutation[item_mrs].sort_values(by = 'Count', ascending = False)[:10]
top_item_not_reported = item_salutation[item_not_reported].sort_values(by = 'Count', ascending = False)[:10]

"""Below we can see the top ten item and corresponding size the customers purchased for each different salutation.Also added which manufacturer belongs to the item."""

top_item_company

top_item_family

top_item_mr

top_item_mrs

top_item_not_reported

data.info()

for ff in sorted(data.columns):
    if (data[ff].dtype == "float64") | (data[ff].dtype == "int64"):
        display_distribution(data[ff], "Feature Distribution of {0}".format(ff))

"""Orders are almost equally distributed over the week.The most order are on a Tuesday(almost 60000 orders),second highest day is Thursday and right before Saturday.The least orders are placed on a Wednesday(less than 50000).
Deliverys are between Monday and Saturday.The most deliverys are on a Tuesday. Monday and Wednesday are almost equal.
It get's less at the weekend.With zero deliverys at Sunday which is obvious,because delivery companies are only working from Monday to Saturday.
"""

deliverytime = data['deliverytime'].astype('timedelta64[D]')
deliverytime_plot = sns.boxplot(y = deliverytime)
deliverytime_plot.set_title('Distribution of delivery time(boxplot)')
deliverytime_plot.set_ylabel('deliverytime in days')
plt.show()

"""Here we can see the delivery time in days. We have a lot of outliers, with a max delivery duration of 175.These dates are obviously outliers,we need to remove."""

data = data.drop(data[data.deliverytime > '8 days'].index)

data.shape

deliverytime = data['deliverytime'].astype('timedelta64[D]')
deliverytime_plot = sns.boxplot(y = deliverytime)
deliverytime_plot.set_title('Distribution of delivery time(boxplot)')
deliverytime_plot.set_ylabel('deliverytime in days')
plt.show()

"""The delivery time distribution makes more sense now and gives a good insight of 
how long the delivery takes.
"""

data.columns

"""**Heatmap of correlation**"""

sns.heatmap(data.corr(), annot=True)

"""CustomerID and itemID has a slightly positive correlation. The reason for that could be that customer tend to order the same products.We saw before that most of the customers are female and and therefore this correlation seems reasonable.
Order_weekday and delivery_weekday have a slightly negative correlation. 
We saw that we had deliveries on the same day as ordered, but it's rarely common.
"""

plt.figure(figsize=(10,7))
sns.barplot(y='age',x= 'order_weekday_name', hue='salutation', data=data)
plt.title('Age to order behaviour, Colored by salutation')
plt.xlabel('weekday')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.xticks

"""Younger famlies tend to order on a friday. On a saturday customer with the salutation company have a mean age of 55 years old.On a monday customer of the same salutation are over ten years younger.
**Cohort Analysis and clustering**
Analyzing the behavior of a group of customers over time to get a better insight of those customers and later cluster them.
"""

def get_month(x): 
  return dt.datetime(x.year, x.month, 1)

"""Get the first of the month."""

data['orderMonth'] = data['orderDate'].apply(get_month)

grouping = data.groupby('customerID')['orderMonth']

data['CohortMonth'] = grouping.transform('min')

data.head()

"""**Function to extract year, month and day integer values.**"""

def get_date_int(df, column):
  year = df[column].dt.year
  month = df[column].dt.month
  day = df[column].dt.day
  return year, month, day

order_year, order_month, _ = get_date_int(data, 'orderMonth')
cohort_year, cohort_month, _ = get_date_int(data, 'CohortMonth')

years_diff = order_year - cohort_year
months_diff = order_month  - cohort_month

data['CohortIndex'] = years_diff * 12 + months_diff + 1 #first month start at 1 not zero
data.head()

grouping = data.groupby(['CohortMonth', 'CohortIndex'])

cohort_data = grouping['customerID'].apply(pd.Series.nunique)

cohort_data = cohort_data.reset_index()

cohort_counts = cohort_data.pivot(index='CohortMonth',
                                  columns='CohortIndex',
                                  values='customerID')

cohort_counts

cohort_sizes = cohort_counts.iloc[:,0]

retention = cohort_counts.divide(cohort_sizes, axis = 0)

retention.round(3) * 100 # percentage

"""**Visualize cohort**
Tracks the customer activity irrespective of the number of orders.
"""

plt.figure(figsize=(10, 8))
plt.title('Retention rate')

sns.heatmap(data = retention,
            annot = True,
            fmt = '.0%',
            vmin = 0.0,
            vmax = 0.5,
            cmap = 'BuGn')
plt.show()

"""Overall the retantion rate isn't that good,but keeps consistent at a low level.21% customers who purchased in April 2012 where still active in September 2012.
**Cstomer segments(RFM)**
"""

print('Min{};Max{}'.format(min(data.orderDate),
                           max(data.orderDate)))

snapshot_date = max(data.orderDate) + dt.timedelta(days=1)

"""** Im only inspecting now the customer which kept their order.**
Customers who returned there product didn't generate any income.
"""

kept = data[data.returnShipment == 0]

datacs = kept.groupby(['customerID']).agg({'orderDate': lambda x:(snapshot_date - x.max()).days,
                                           'orderItemID' : 'count',
                                           'price':'sum'})

datacs.rename(columns={'orderDate':'Recency',
                         'orderItemID':'Frequency',
                         'price':'MonetaryValue'}, inplace = True)

datacs.head()

"""**Group customers in four segments**"""

r_labels = range(4, 0, -1)
r_quartiles = pd.qcut(datacs['Recency'], 4, labels = r_labels)
datacs = datacs.assign(R = r_quartiles.values)
datacs.head()

f_labels = range(1,5)
m_labels = range(1,5)
f_quartiles = pd.cut(datacs['Frequency'], 4, labels = f_labels)
m_quartiles = pd.cut(datacs['MonetaryValue'], 4, labels = m_labels)

datacs = datacs.assign(F = f_quartiles.values)
datacs = datacs.assign(M = m_quartiles.values)

datacs.head()

def join_rfm(x): 
  return str(x['R']) + str(x['F']) + str(x['M'])
datacs['RFM_Segment'] = datacs.apply(join_rfm, axis=1)
datacs['RFM_Score'] = datacs[['R','F','M']].sum(axis=1)

datacs.head()

datacs.groupby('RFM_Score').agg({
    'Recency': 'mean',
    'Frequency': 'mean',
    'MonetaryValue': ['mean', 'count'] }).round(1)

"""Group customers into Gold, Silver, Bronze segments."""

def segment_creator(df):
    if df['RFM_Score'] >= 9:
        return 'Gold'
    elif (df['RFM_Score'] >= 5) and (df['RFM_Score'] < 9):
        return 'Silver'
    else:
        return 'Bronze'

datacs['General_Segment'] = datacs.apply(segment_me, axis=1)

datacs.groupby('General_Segment').agg({
    'Recency': 'mean',
    'Frequency': 'mean',
    'MonetaryValue': ['mean', 'count']
}).round(1)

sns.distplot(datacs['Frequency'])
plt.show()

sns.distplot(datacs['Recency'])
plt.show()

frequency_log = np.log(datacs['Frequency'])
sns.distplot(frequency_log)
plt.show()

datacs_rfm = datacs[['Recency',	'Frequency', 'MonetaryValue']].copy(deep = True)

datacs_rfm

datacs_rfm.describe()

datacs_rfm.info()

"""**Pre-processing**"""

datacs_log = datacs_rfm.copy(deep= True)

datacs_log['Frequency'] = np.log(datacs_rfm['Frequency'])

scaler = StandardScaler()
scaler.fit(datacs_log)

datacs_normalized = scaler.transform(datacs_log)

print('mean: ', datacs_normalized.mean(axis=0).round(2))
print('std: ', datacs_normalized.std(axis=0).round(2))

"""**Clustering**
**Choosing the number of clusters**
"""

# Fit KMeans and calculate sum-of-squared-errors(SSE) for each *k*
sse = {}
for k in range(1, 11):
    kmeans = KMeans(n_clusters=k, random_state=1)
    kmeans.fit(datacs_normalized)
    sse[k] = kmeans.inertia_

# Plot SSE for each *k*
plt.title('The Elbow Method')
plt.xlabel('k'); plt.ylabel('SSE')
sns.pointplot(x=list(sse.keys()), y=list(sse.values()))
plt.show()

kmeans = KMeans(n_clusters=3, random_state=1)

kmeans.fit(datacs_normalized)

cluster_labels = kmeans.labels_

datacs_rfm_k2 = datacs_rfm.assign(Cluster = cluster_labels)

datacs_rfm_k2.groupby(['Cluster']).agg({
    'Recency': 'mean',
    'Frequency': 'mean',
    'MonetaryValue': ['mean', 'count'],
}).round(0)

"""**visualize**"""

datacs_normalized = pd.DataFrame(datacs_normalized, 
                                   index=datacs_rfm.index, 
                                   columns=datacs_rfm.columns)
datacs_normalized['Cluster'] = datacs_rfm_k2['Cluster']

datacs_melt = pd.melt(datacs_normalized.reset_index(), 
                    id_vars=['customerID', 'Cluster'],
                    value_vars=['Recency', 'Frequency', 'MonetaryValue'], 
                    var_name='Attribute', 
                    value_name='Value')

plt.title('Snake plot of standardized variables')
sns.lineplot(x="Attribute", y="Value", hue='Cluster', data=datacs_melt)

"""Cluster 2 are our golden customers.They are active and purchased in a high frequency.Also they tend to buy pricey.
Cluster 1 are our silver cusomers.They are purchasing in a low frequency and  when they buy products, then only cheaper ones.
Cluster 0 are our bronze customers.They weren't active in a long time, didn't purchased much and mostly cheaper products.These customers are unlikely to return to the shop.
"""

datacs_rfm_k3 = datacs_rfm_k2[['Recency',	'Frequency', 'MonetaryValue','Cluster']].copy(deep = True)
datacs_rfm_k3.head()

cluster_avg = datacs_rfm_k3.groupby(['Cluster']).mean()
 
population_avg = datacs_rfm.mean()
 
relative_imp = cluster_avg / population_avg - 1

relative_imp.round(2)

plt.figure(figsize=(8, 2))
plt.title('Relative importance of attributes')
sns.heatmap(data=relative_imp, annot=True, fmt='.2f', cmap='RdYlGn')
plt.show()

"""The further a ratio is from 0, the more important that attribute is for a segment relative to the total population."""
