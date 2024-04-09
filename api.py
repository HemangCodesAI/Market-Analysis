from bs4 import BeautifulSoup
import requests
from uszipcode import SearchEngine
import urllib.parse
import pandas as pd
from urllib.request import Request , urlopen
import gzip
import threading
import re
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime
# Load Google Sheets credentials
creds = service_account.Credentials.from_service_account_file('creds.json')
service = build('sheets', 'v4', credentials=creds)
sheet_id = '1Qw3auye81AFt9kezJNy22nLSMW_T240b4eDLbFUg46M'
def capture_data(row,service=service,sheet_id=sheet_id):
    sheet = service.spreadsheets()
    current_datetime=datetime.now()
    current_date = current_datetime.strftime('%Y-%m-%d')
    current_time = current_datetime.strftime('%H:%M:%S')
    row[0].append(current_date)
    row[0].append(current_time)
    sheet.values().append(
    spreadsheetId=sheet_id,
    range='Sheet1!A1',  # Update with your desired range
    valueInputOption='RAW',
    body={'values': row}
    ).execute()
    print("done")


def get_zip_data(zipcode):
    search = SearchEngine(db_file_path='/tmp/simple_db.sqlite')
    return search.by_zipcode(zipcode)

def get_url(obj):
    par = {
        "st": obj.state.lower(),
        "ct": obj.major_city.lower(),
        "hd": "",
        "zip": obj.zipcode,
        "addr": "",
        "ll": f"{round(obj.lat * 100000) / 100000} {round(obj.lng * 100000) / 100000}"
    }
    return "&".join([f"{key}={urllib.parse.quote_plus(str(value))}" for key, value in par.items()])

def get_economy(zip_data,KPIdf): # finalised
    url=f'https://www.bestplaces.net/economy/zip-code/{zip_data.state.lower()}/{zip_data.major_city.lower()}/{zip_data.zipcode}'
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        div = soup.find_all('div', class_='card-body m-3 p-0')
        if div:
            ps = div[0].find_all('p')
            for p in ps:
                if "unemployment rate" in p.text:
                    row_data=["Unemployment Rate [As of 2019]",p.text.split("  ")[0].split(" ")[-1],p.text.split("  ")[1]]
                    KPIdf.loc[len(KPIdf)] = row_data

def get_crime(zip_data, KPIdf): # finalised
    url=f'https://www.bestplaces.net/crime/zip-code/{zip_data.state.lower()}/{zip_data.major_city.lower()}/{zip_data.zipcode}'
    response = requests.get(url)
    try:
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            texts = soup.find_all('h5')
            row_data = ["Crime Rate(/1000) [As of 2019]", f'''{texts[1].text.split(".  (")[0][-4:]}%''',f'''{texts[1].text.split(".  (")[1][:-1]}%''']
    except:
        row_data = ["Crime Rate(/1000)", "No data found", "No data found"]
    KPIdf.loc[len(KPIdf)] = row_data

def get_score(zip_data, KPIdf): # finalised
    url=f'https://www.areavibes.com/search-results/?{get_url(zip_data)}'
    response = requests.get(url)
    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            div = soup.find("a", class_="pri")
            if div:
                i = div.find_all("i")
                if i:
                    score= int(i[1].text.strip())
                    if score<=20 and score>0:
                        grade="Very poor!"
                    elif score<=40 and score>20:
                        grade="Poor!"
                    elif score<=60 and score>40:
                        grade="Average!"
                    elif score<=80 and score>60:
                        grade="Good!"
                    elif score<=100 and score>80:
                        grade="Excellent!"
                    row_data = ["Livability Score [As of 2019]", score, grade]
        except:
            row_data = ["Livability Score", "No data found", "No data found"]
        KPIdf.loc[len(KPIdf)] = row_data

def get_rent(info): # finalised
    bed_fils = [["studios","Studio"],["1-bedrooms","1-BD"],["2-bedrooms","2-BD"], ["3-bedrooms","3-BD"], ["4-bedrooms","4-BD"]]    
    sorts = ["1", "2"]
    DATA = []

    for bed_fil in bed_fils:
        row_data = [bed_fil[1]]
        for sort in sorts:
            try:
                url = f'https://www.apartments.com/{info.major_city.lower().replace(" ", "-")}-{info.state.lower()}-{info.zipcode}/{bed_fil[0]}/?so={sort}'
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1", "DNT": "1", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate"}
                response = Request(url, headers=headers)
                response1 =urlopen(response)
                if response1.info().get('Content-Encoding') == 'gzip':
                    data = gzip.decompress(response1.read())
                else:
                    data = response1.read()
                result = data.decode('utf-8')
                soup = BeautifulSoup(result, "html.parser")
                div = soup.find("div", class_="price-range")
                if div:
                    # print(div)
                    row_data.append(div.text)
                elif soup.find("p", class_="bed-price-range"):
                    div = soup.find("p", class_="bed-price-range")
                    # print(div.find("span", class_="property-rents"))
                    row_data.append(f'''{div.find("span", class_="property-rents").text}/mo''')
                else:
                    row_data.append("No data found")
            except:
                row_data.append("No data found")
        DATA.append(row_data)
    return pd.DataFrame(DATA,columns=["Bedrooms","Max","Min"])

def get_old(KPIdf,info,zipcode):
    get_crime(info,KPIdf)
    get_score(info,KPIdf)
    get_economy(info,KPIdf)
    return KPIdf


def get_population_growth(soup, KPIdf):
    div = soup.find_all("div", class_="stat-subtitle")
    if len(div) > 1:
        try:
            divv = soup.find_all("div", class_="stat-value")
            if "decline" in div[0].text:
                row_data = ['Population Growth since 2000', f'-{div[0].text.split(" ")[0]}', 'Current population is ' + divv[0].text]
            else:
                row_data = ['Population Growth since 2000', f'{div[0].text.split(" ")[0]}', 'Current population is ' + divv[0].text]
            KPIdf.loc[len(KPIdf)] = row_data
        except:
            row_data = ['Population Growth since 2000', 'No data found', 'No data found']
            KPIdf.loc[len(KPIdf)] = row_data

def get_poverty_rate(soup, KPIdf):
    try:
        div = soup.find_all("div", class_="Stat large-text")
        row_data = ["Poverty Rate", div[2].find("div", class_="stat-value").text, div[2].find("div", class_="stat-subtitle").text]
        KPIdf.loc[len(KPIdf)] = row_data
    except:
        row_data = ["Poverty Rate", "No data found", "No data found"]
        KPIdf.loc[len(KPIdf)] = row_data

def get_median_hh_income(soup,KPIdf):
    try:
        div=soup.find_all("div", class_="Stat large-text")
        row_data=["Median Household Income",div[3].find("div", class_="stat-value").text,div[3].find("div", class_="stat-subtitle").text]
        # print(row_data)
        KPIdf.loc[len(KPIdf)] = row_data
    except:
        row_data=["Median Household Income","No data found","No data found"]
        KPIdf.loc[len(KPIdf)] = row_data

def get_hhi_increase(soup,KPIdf,info):
    div=soup.find_all("div", class_="stat-subtitle")
    try:
        div=soup.find_all("div", class_="Stat large-text")
        curr=int(div[3].find("div", class_="stat-value").text.replace("$","").replace(",",""))
        old=int(info.median_household_income)
        growth=((curr-old)/curr)*100
        row_data=["Median Household Income Growth since 2000",f'{round(growth,2)}%',f'In year 2000 it was {old}']
        # print(row_data)
        KPIdf.loc[len(KPIdf)] = row_data
    except:
        row_data=["Median Household Income Growth since 2000","No data found","No data found"]
        KPIdf.loc[len(KPIdf)] = row_data
# Define similar functions for other data points
def get_household_value(soup,KPIdf):
    div=soup.find_all("div", class_="Stat large-text")
    try:
        row_data=["Median Household Value",div[4].find("div", class_="stat-value").text,div[4].find("div", class_="stat-subtitle").text]
        # print(row_data)
        KPIdf.loc[len(KPIdf)] = row_data
    except:
        row_data=["Median Household Value","No data found","No data found"]
        KPIdf.loc[len(KPIdf)] = row_data

def get_value_growth(soup,KPIdf,info):
    div=soup.find_all("div", class_="Stat large-text")
    try:
        curr=int(div[4].find("div", class_="stat-value").text.replace("$","").replace(",",""))
        old=int(info.median_home_value)
        growth=((curr-old)/curr)*100
        row_data=["Median Household Value Growth since 2000",f'{round(growth,2)}%',f'In year 2000 it was {old}']
        print(row_data)
        KPIdf.loc[len(KPIdf)] = row_data
    except:
        row_data=["Median Household Value Growth since 2000","No data found","No data found"]
        KPIdf.loc[len(KPIdf)] = row_data

def get_job_growth(soup,KPIdf):
    try:
        div=soup.find_all("div", class_="StatGroup single")
        row_data=["Job Growth",div[8].find("div", class_="stat-value").text,div[8].find("div", class_="stat-title").text]
        KPIdf.loc[len(KPIdf)] = row_data
    except:
        row_data=["Job Growth","No data found","No data found"]
        KPIdf.loc[len(KPIdf)] = row_data

def get_owner(soup,KPIdf):
    try:
        div=soup.find_all("div", class_="section-description")
        para=div[5].text.split(". ")
        values_with_percentage = re.findall(r'\d+\.\d+%', para[2])
        row_data=["Owner Occupied Housing Unit Rate",values_with_percentage[0],f"The national average is {values_with_percentage[1]}"]
        KPIdf.loc[len(KPIdf)] = row_data
    except:
        row_data=["Owner Occupied Housing Unit Rate","No data found","No data found"]
        print(row_data)
        KPIdf.loc[len(KPIdf)] = row_data

def get_data(info,Rentdf):
    KPIdf = pd.DataFrame(columns=['KPI', 'value', 'comment'])
    url = f'''https://datausa.io/profile/geo/{info.major_city.lower().replace(" ", "-").replace("-national", "")}-{info.state.lower()}'''
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        threads = []

        # Define functions for each data point
        threads.append(threading.Thread(target=get_population_growth, args=(soup, KPIdf)))
        threads.append(threading.Thread(target=get_poverty_rate, args=(soup, KPIdf)))
        threads.append(threading.Thread(target=get_median_hh_income, args=(soup, KPIdf)))
        threads.append(threading.Thread(target=get_hhi_increase, args=(soup, KPIdf,info)))
        threads.append(threading.Thread(target=get_household_value, args=(soup, KPIdf)))
        threads.append(threading.Thread(target=get_value_growth, args=(soup, KPIdf,info)))
        threads.append(threading.Thread(target=get_job_growth, args=(soup, KPIdf)))
        threads.append(threading.Thread(target=get_owner, args=(soup, KPIdf)))
        threads.append(threading.Thread(target=get_crime, args=(info, KPIdf)))
        threads.append(threading.Thread(target=get_score, args=(info, KPIdf)))
        threads.append(threading.Thread(target=get_economy, args=(info, KPIdf)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        try:
            a = Rentdf['Max'].replace('[\$,]', '', regex=True).replace("/mo","",regex=True).astype(int)
            b = Rentdf['Min'].replace('[\$,]', '', regex=True).replace("/mo","",regex=True).astype(int)
            gross_rent = (a.mean()+b.mean())/2
            row_data=["Median Gross Rent",f"${round(gross_rent,2)}/mo",'Source: Apartments.com']
            # print(row_data)
            KPIdf.loc[len(KPIdf)] = row_data
        except:
            row_data=["Median Gross Rent","No data found",'No data found']
            KPIdf.loc[len(KPIdf)] = row_data
        # median gross rent vs median hh income\
        try:
            div=soup.find_all("div", class_="Stat large-text")
            curr=int(div[4].find("div", class_="stat-value").text.replace("$","").replace(",",""))
            row_data=["Median Gross Rent vs. Median HH Income",f"${gross_rent}/${curr}",f"The income is {curr//gross_rent} times the rent"]
            # print(row_data)
            KPIdf.loc[len(KPIdf)] = row_data
        except:
            row_data=["Median Gross Rent vs. Median HH Income","No data found","No data found"]
            KPIdf.loc[len(KPIdf)] = row_data
    # KPIdf = get_old(KPIdf, info, zipcode)
    return KPIdf


def jd(info):
    url=f'''https://datausa.io/profile/geo/{info.major_city.lower().replace(" ","-").replace("-national","")}-{info.state.lower()}/economy/employment_by_industries?viz=true'''
    url1=f'''https://datausa.io/profile/geo/{info.major_city.lower().replace(" ","-").replace("-national","")}-{info.state.lower()}/education/degrees?viz=true'''
    if requests.get(url).status_code==200:
        jd=[url,url1]
    else:
        jd=False
    return jd
