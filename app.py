from flask import Flask, render_template, request ,session
from api import get_data, get_zip_data,get_rent,capture_data
import pandas as pd
import requests
# capture_data([['Jhu', 'Doe', 'john.doe@example.com']])
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
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
@app.route('/', methods=['GET'])
def index():
    
    return render_template('1.html', result=False, ekpi=ekpi, erent=erent)
    # return render_template('1.html', result=False)

@app.route('/submit', methods=['POST'])
def submit():
    global zipcode, jd ,info,email,name,phone_number
    email = request.form.get('Email')
    name = request.form.get('Name')
    phone_number = request.form.get('phoneNumber')
    zipcode = request.form.get('zipcode')
    session['email'] = email
    session['name'] = name
    session['phone_number'] = phone_number
    session['zipcode'] = zipcode

    user_data=[email,name,phone_number,zipcode]
    capture_data([user_data])
    info=get_zip_data(zipcode)
    session['info']=info
    print("0")
    if zipcode and info:
        # rents=get_rent(info)
        print("1")
        KPIs=get_data(info)
        print("2")
        url=f'''https://datausa.io/profile/geo/{info.major_city.lower().replace(" ","-").replace("-national","")}-{info.state.lower()}/economy/employment_by_industries?viz=true'''
        url1=f'''https://datausa.io/profile/geo/{info.major_city.lower().replace(" ","-").replace("-national","")}-{info.state.lower()}/education/degrees?viz=true'''
        if requests.get(url).status_code==200:
            jd=[url,url1]
            session['url']=url
            session['url1']=url1
        else:
            jd=False
        print("3")

        return render_template('1.html', result=True, zipcode=zipcode, KPIs=KPIs, rents=erent, jd=jd, Email=email, Name=name, phoneNumber=phone_number)
    else:
        return "Please enter a valid zip code!", 400

@app.route('/more_info',methods=['POST'])
def more_info():
    email = session.get('email')
    name = session.get('name')
    phone_number = session.get('phone_number')
    zipcode = session.get('zipcode')
    info=session.get('info')
    jd=[session.get('url'),session.get('url1')]
    KPIs=pd.read_csv("temp/data.csv")
    rents=get_rent(info)
    return render_template('1.html',more_info=True, result=True, zipcode=zipcode, KPIs=KPIs, rents=rents, jd=jd, Email=email, Name=name, phoneNumber=phone_number)
