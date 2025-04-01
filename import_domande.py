import pandas as pd
import requests
import json
df1= pd.read_csv('/home/francesco/Desktop/merged.csv')
for _, rows in df1.iterrows():
    print(rows['corpo_x'], rows['corpo_y'])
    print(rows['rispostaEsatta'])

data = []
for _, rows in df1.iterrows():
    data.append({
        'corpo': str(rows['corpo_x']) + " " + str(rows['corpo_y']), #ensure they are strings
        'tipo': str(rows['tipo']), #ensure they are strings
        'risposta_esatta': str(rows['rispostaEsatta']), #ensure they are strings
    })

response = requests.post('http://localhost:8000/domande/create_basic_import', json=data) #use json=data

if response.status_code == 200:
    print("Data sent successfully!")
    print(response.json()) # Print the response from the server
else:
    print(f"Error sending data: {response.status_code}")
    print(response.text) #print the error response.