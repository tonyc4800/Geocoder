from flask import Flask, render_template, request, send_file
import pandas
from geopy import ArcGIS
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Base page
@app.route("/")
def index():
    return render_template("index.html")

# Functionality for submit button. When pressed submits file to be uploaded and processed
@app.route("/table", methods = ['POST'])
def table():  
    if request.method == 'POST':   
        global secure_file_name     
        file = request.files['file']
        secure_file_name = secure_filename(file.filename)
        if secure_file_name.endswith('.csv'):
            arc = ArcGIS()
            df = pandas.read_csv(file)
            try:
                address = get_adrs_col(df) 
                df['Coordinates'] = df[address].apply(arc.geocode)
                df['Latitude'] = df['Coordinates'].apply(lambda x: x.latitude if x != None else 'NaN')
                df['Longitude'] = df['Coordinates'].apply(lambda x: x.longitude if x != None else 'NaN')
                df = df.drop(columns = 'Coordinates')
                df.to_csv("uploads/" + secure_file_name, index = False)
                return render_template('index.html', dl_btn = "dl_btn.html", table = df.to_html())
            except KeyError:
                return render_template("index.html", err_msg = "Please make sure you have an address column in the CSV file!") 
        else:
            return render_template("index.html", err_msg = "Please make sure the file you are trying to upload is a CSV file!")  

def get_adrs_col(df):
    for col_name in df.columns:
        if col_name == 'Address' or col_name == 'address':
            return col_name

# Functionality for submit button. When pressed downloads the a csv file of the updated table
@app.route("/download")
def has_address():   
    return send_file("uploads/" + secure_file_name, download_name="updated_file.csv", as_attachment=True)

if __name__ == '__main__':
    app.debug = False
    app.run() 