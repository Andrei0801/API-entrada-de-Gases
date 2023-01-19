import os
import json
import requests
import subprocess
import time
import sys
import pandas as pd
import numpy as np
import response



start_time = time.time()
elapsed = 0
token_limit = 3600

#URL for login and get API tokens
url_login = "https://api.modulusone.com/login"
#URL for API telemetry endpoint
url_telemetry = "https://api.modulusone.com/live_telemetry"

#Get API tokens
def GetAPI_Tokens():

    response_token = requests.post(url_login, json={'login':'modulus@randon.com.br', 'password':'nt1675'})

    df_token = pd.DataFrame([response_token.json()])
    access_token = df_token['access_token']
    refresh_token = df_token['refresh_token']

    access_token = str(access_token).replace('\n', '')
    access_token = access_token.replace('\r', '')
    access_token = access_token.replace(' ', '')
    a_token = access_token[1:31]

    refresh_token = str(refresh_token).replace('\n', '')
    refresh_token = refresh_token.replace('\r', '')
    refresh_token = refresh_token.replace(' ', '')
    r_token = refresh_token[1:31]

    print('access token = ' + access_token)
    print('refresh token = ' + refresh_token)
    return a_token,r_token
	
#Process
print ('start')

token,rfsh_token = GetAPI_Tokens()

while (True):

    response = requests.post(url_telemetry, json={'device_serial':'27131', 'network_serial':'1'}, headers={'Authorization': 'Bearer ' + token})
    #print(response.json())

    if response.status_code == 200:

        df_live_telemetry = pd.DataFrame([response.json()])
		
        df_live_telemetry.date = pd.to_datetime(df_live_telemetry.date)

        df_live_telemetry.reset_index(inplace=True)
        data_dict = df_live_telemetry[['date','va','vb','vc','ia','ib','ic','cosphia','cosphib','cosphic','pa','pb','pc','qa','qb','qc','pt','qt','kwh']].to_dict("records")
        data_dictia = df_live_telemetry[['ia']].to_dict("index")
        data_dictib = df_live_telemetry[['ib']].to_dict("index")
        data_dictdate = df_live_telemetry[['date']].to_dict("index")
        		
        dataframe = pd.DataFrame({'date': data_dictdate,
                                  'ia': data_dictia,
                                  'ib': data_dictib})
        tabela_dados2 = pd.read_csv("tabeladados.csv",delimiter=",")
        tabela_dados = pd.concat([tabela_dados2,dataframe],ignore_index= True)
        
        
        tabela_dados.to_csv("tabeladados.csv",index=False)
        print(dataframe)
        #print(tabela_dados)
            
        
    

    else:
	    print('\nStatus = ', response.status_code)

    time.sleep(65) #telemetria ocorre a cada 60 segundos, preveni telemetria repetida
    now_time = time.time()
    elapsed = now_time - start_time

    #Token revalidation
    if elapsed > token_limit:
        start_time = time.time()
        token,rfsh_token = GetAPI_Tokens()
