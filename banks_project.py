from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime 

url = 'https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks'  
table_attribs = ['Name', 'MC_USD_Billion']
output_path = './Largest_banks_data.csv'
db_name = 'Banks.db'
table_name = 'Largest_banks'
path_log = 'code_log.txt'
csv_path = 'exchange_rate.csv'
def log_progress(message):
    ''' This function logs the mentioned message of a given stage of the
    code execution to a log file. Function returns nothing'''
    timestamp_format = '%Y-%h-%d-%H:%M:%S' # Year-Monthname-Day-Hour-Minute-Second 
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    with open(path_log, 'a') as f:
        f.write(timestamp + ':' + message + '\n')
def extract(url, table_attribs):
    ''' This function aims to extract the required
    information from the website and save it to a data frame. The
    function returns the data frame for further processing. '''
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
def transform(df, csv_path):
    ''' This function accesses the CSV file for exchange rate
    information, and adds three columns to the data frame, each
    containing the transformed version of Market Cap column to
    respective currencies'''
    USD_list = df["MC_USD_Billion"].tolist()
    USD_list = [float(''.join(str(x).split(','))) for x in USD_list]
    csv_file = pd.read_csv(csv_path)
    dict = csv_file.set_index('Currency').to_dict()['Rate']
    df['MC_GBP_Billion'] = [np.round(x * dict['GBP'],2) for x in df['MC_USD_Billion']]
    df['MC_INR_Billion'] = [np.round(x * dict['INR'],2) for x in df['MC_USD_Billion']]
    df['MC_EUR_Billion'] = [np.round(x * dict['EUR'],2) for x in df['MC_USD_Billion']]
    return df
def load_to_csv(df, output_path):
    ''' This function saves the final data frame as a CSV file in
    the provided path. Function returns nothing.'''
    df.to_csv(output_path)


def load_to_db(df, sql_connection, table_name):
    ''' This function saves the final data frame to a database
    table with the provided name. Function returns nothing.'''
    df.to_sql(table_name, sql_connection, if_exists = 'replace', index = False)
def run_query(query_statements, sql_connection):
    ''' This function runs the stated query on the database table and
    prints the output on the terminal. Function returns nothing. '''
    for query in query_statements:
        print(query)
        print(pd.read_sql(query, sql_connection), '\n')

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

