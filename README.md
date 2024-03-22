# Project Scenario 🎩
This project requires you to compile the list of the top 10 largest banks in the world ranked by market capitalization in billion USD. Further, you need to transform the data and store it in USD, GBP, EUR, and INR per the exchange rate information made available to you as a CSV file. You should save the processed information table locally in a CSV format and as a database table. Managers from different countries will query the database table to extract the list and note the market capitalization value in their own currency.

# Reach/Follow me on <br>
<p align="left">
  <a href="https://www.linkedin.com/in/gia-do-hoang/" target="_blank" rel="noreferrer"> <img src="https://img.icons8.com/fluency/2x/linkedin.png" alt="linkedIn" width="50" height="50"/> </a>&nbsp&nbsp
  <a href="mailto:dohoanggia20020@gmail.com" target="_blank" rel="noreferrer"> <img src="https://img.icons8.com/fluency/2x/google-logo.png" alt="googleEmail" width="50" height="50"/> </a>&nbsp&nbsp
  <a href="https://www.facebook.com/gia021102" target="_blank" rel="noreferrer"> <img src="https://cdn.iconscout.com/icon/free/png-256/facebook-262-721949.png" alt="facebook" width="50" height="50"/> </a>
</p>
<br>

# Project task📝
* You have to complete the following tasks for this project
  - Write a function log_progress() to log the progress of the code at different stages in a file code_log.txt.
  - Write the code for a function extract() to perform the required data extraction.
  - Transform the available GDP information into 'Billion USD' from 'Million USD', Write the code for a function transform() to perform this task.
  - Load the transformed information to the required CSV file and as a database file.
  - Run queries on the database table.
  - Verify that the log entries have been completed at all stages by checking the contents of the file code_log.txt

## 📦 Install

- First of all, install the required Libraries for ETL:

```bash
pip3 install pandas
```

```bash
pip3 install beautifulsoup4
```

## Implementation
- After installation, we go through the code to discuss the progress briefly

- then, we need to initialize our libraries:
```python
import pandas as pd 
import numpy as np 
import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime
```  

## Directions 🗺

1.This function logs the mentioned message of a given stage of the code execution to a log file. Function returns nothing
```python
def log_progress(message):
    timestamp_format = '%Y-%h-%d-%H:%M:%S' # Year-Monthname-Day-Hour-Minute-Second 
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    with open(path_log, 'a') as f:
        f.write(timestamp + ':' + message + '\n')
```

2. This function aims to extract the required information from the website and save it to a data frame. The function returns the data frame for further processing.
```python
def extract(url, table_attribs):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    df = pd.DataFrame(columns = table_attribs)
    tables = soup.find_all('tbody')
    rows = tables[0].find_all('tr')
    for row in rows:
        if row.find('td') is not None:
            col = row.find_all('td')
            bank_name = col[1].find_all('a')[1]['title']
            market_cap = col[2].contents[0][:-1]
            data_dict = {'Name' : bank_name,
                         'MC_USD_Billion': float(market_cap)}
            df1 = pd.DataFrame(data_dict, index = [0])
            df = pd.concat([df, df1], ignore_index= True)        
    
    return df
```

3. This function accesses the CSV file for exchange rate information, and adds three columns to the data frame, each containing the transformed version of Market Cap column to respective currencies
```python
def transform(df, csv_path):
    USD_list = df["MC_USD_Billion"].tolist()
    USD_list = [float(''.join(str(x).split(','))) for x in USD_list]
    csv_file = pd.read_csv(csv_path)
    dict = csv_file.set_index('Currency').to_dict()['Rate']
    df['MC_GBP_Billion'] = [np.round(x * dict['GBP'],2) for x in df['MC_USD_Billion']]
    df['MC_INR_Billion'] = [np.round(x * dict['INR'],2) for x in df['MC_USD_Billion']]
    df['MC_EUR_Billion'] = [np.round(x * dict['EUR'],2) for x in df['MC_USD_Billion']]
    return df
```

4. This function saves the final data frame as a CSV file in the provided path. Function returns nothing.
```python
def load_to_csv(df, output_path):
    df.to_csv(output_path)
```

5. This function saves the final data frame to a database table with the provided name. Function returns nothing.
```python
def load_to_db(df, sql_connection, table_name):
    df.to_sql(table_name, sql_connection, if_exists = 'replace', index = False)
```

6. This function runs the stated query on the database table and prints the output on the terminal. Function returns nothing.
```python
def run_query(query_statements, sql_connection):
    for query in query_statements:
        print(query)
        print(pd.read_sql(query, sql_connection), '\n')
```

7. Here, you define the required entities and call the relevant functions in the correct order to complete the project. Note that this portion is not inside any function.
```python
url = 'https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks'  
table_attribs = ['Name', 'MC_USD_Billion']
output_path = './Largest_banks_data.csv'
db_name = 'Banks.db'
table_name = 'Largest_banks'
path_log = 'code_log.txt'
csv_path = 'exchange_rate.csv'
query_statements = [
        'SELECT * FROM Largest_banks',
        'SELECT AVG(MC_GBP_Billion) FROM Largest_banks',
        'SELECT Name from Largest_banks LIMIT 5'
    ]

log_progress('Preliminaries complete. Initiating ETL process')
df = extract(url, table_attribs)
log_progress('Data extraction complete. Initiating Transformation process')
transform(df, csv_path)
print(df)
log_progress('Data transformation complete. Initiating Loading process')
load_to_csv(df, output_path)
log_progress('Data saved to CSV file')
sql_connection = sqlite3.connect('Banks.db')
log_progress('SQL Connection initiated.')

load_to_db(df, sql_connection, table_name)

log_progress('Data loaded to Database as table. Running the query')

run_query(query_statements, sql_connection)

log_progress('Process Complete.')

sql_connection.close()
log_progress('Server Connection closed')
```

















