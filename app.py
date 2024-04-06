from flask import Flask, render_template, request, make_response
from fast_scraper import get_data, get_zip_data
import pandas as pd
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

# capture_data([['Jhu', 'Doe', 'john.doe@example.com']])
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    a=['Population Growth since 2000','Poverty Rate','College Graduates','Crime Index','Median Household Income','Median Household Income Growth since 2000','Landlord Friendly','Median Household Value','Median Household Value Growth since 2000','Owner Occupied Housing Unit Rate','Median Gross Rent','Median Gross Rent vs. Median HH Income','Max Possible Rent','Liveability Score','Vacancy Rate','Job Growth','Unemployment Rate'] 
    ekpi = pd.DataFrame( columns = ['KPI', 'Value', 'Comment'])
    ekpi['KPI'] = a
    ekpi['Value'] = ['']*17
    ekpi['Comment'] = ['']*17
    c=['Studio', '1-BD', '2-BD', '3-BD', '4-BD']
    erent = pd.DataFrame( columns = ['Type', 'min', 'max'])
    erent['Type'] = c
    erent['min'] = ['']*5
    erent['max'] = ['']*5
    return render_template('1.html', result=False, ekpi=ekpi, erent=erent)
    # return render_template('1.html', result=False)

@app.route('/submit', methods=['POST'])
def submit():
    email = request.form.get('Email')
    name = request.form.get('Name')
    phone_number = request.form.get('phoneNumber')
    zipcode = request.form.get('zipcode')
    user_data=[email,name,phone_number,zipcode]
    capture_data([user_data])
    if zipcode and get_zip_data(zipcode):
        KPIs, rents ,jd= get_data(zipcode)
        return render_template('1.html', result=True, zipcode=zipcode, KPIs=KPIs, rents=rents, jd=jd, Email=email, Name=name, phoneNumber=phone_number)
    else:
        return "Please enter a valid zip code!", 400



