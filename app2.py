from flask import Flask, request, render_template, session
import pandas as pd
from api import get_zip_data, get_rent

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/more_info', methods=['POST'])
def more_info():
    user_data = session.get('user_data')
    info = get_zip_data(user_data[3])
    bed_fil = request.form.get('selected_option')
    rents = get_rent(info, bed_fil)
    return render_template('1.html', more_info=True, result=True, zipcode=user_data[3], KPIs=pd.read_json(session.get('df_json')), rents=rents, jd=user_data[6], Email=user_data[0], Name=user_data[1], phoneNumber=user_data[2])

# if __name__ == "__main__":
#     app.run(debug=True)
