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
    email = request.form.get('Email')
    name = request.form.get('Name')
    phone_number = request.form.get('phoneNumber')
    zipcode = request.form.get('zipcode')
    bed_fil=request.form.get("selected_option")
    user_data=[email,name,phone_number,zipcode]
    capture_data([user_data])
    info=get_zip_data(zipcode)
    print("0")
    if zipcode and info:
        rents=get_rent(info,bed_fil)
        print("1")
        KPIs=get_data(info)
        print("2")
        url=f'''https://datausa.io/profile/geo/{info.major_city.lower().replace(" ","-").replace("-national","")}-{info.state.lower()}/economy/employment_by_industries?viz=true'''
        url1=f'''https://datausa.io/profile/geo/{info.major_city.lower().replace(" ","-").replace("-national","")}-{info.state.lower()}/education/degrees?viz=true'''
        if requests.get(url).status_code==200:
            jd=[url,url1]
        else:
            jd=False
        print("3")

        return render_template('1.html', result=True, zipcode=zipcode, KPIs=KPIs, rents=rents, jd=jd, Email=email, Name=name, phoneNumber=phone_number)
    else:
        return "Please enter a valid zip code!", 400

# if __name__=="__main__":
#     app.run(debug=True)