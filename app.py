from flask import*
import pymysql
import pymysql.cursors
import os
from flask_cors import CORS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'home/mellymarsh/mysite/static/images'

CORS(app)
@app.route("/api/signup", methods= ['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']

        # Connecting to the database
        connection = pymysql.connect(host='mellymarsh.mysql.pythonanywhere-services.com', user='mellymarsh', password='fobbs123', database='mellymarsh$default')

        # Do Insert Querry
        cursor= connection.cursor()
        cursor.execute("INSERT INTO users(username, email, password, phone) VALUES (%s,%s,%s,%s)", (username, email, password, phone))

        # Saving the Data into the Database
        connection.commit()
        return jsonify({"message":"Thanks for Joining😁😁"})


@app.route("/api/signin", methods= ['POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connecting to the database
        connection = pymysql.connect(host='mellymarsh.mysql.pythonanywhere-services.com', user='mellymarsh', password='fobbs123', database='mellymarsh$default')
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        sql = 'SELECT FROM users WHERE username =%s AND password =%s'
        data = (username, password)

        cursor.execute(sql, data)
        count= cursor.rowcount
        if count == 0:
            return jsonify({"message": "Login Error🥺🥺💔"})
        else:
            user = cursor.fetchone()
            return jsonify({"message":"Successful Login" ,"user": user})


@app.route("/api/product_listing", methods= ['GET'])
def product_listing():
    if request.method == 'GET':

        # Connecting to Database
        connection = pymysql.connect(host='mellymarsh.mysql.pythonanywhere-services.com', user='mellymarsh', password='fobbs123', database='mellymarsh$default')
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM products')

        products = cursor.fetchall()
        connection.close()
        return jsonify({'products': products})


@app.route("/api/add_product", methods= ['POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        description = request.form['description']
        product_cost = request.form['product_cost']

        # Extract Image from input
        product_photo = request.files['product_photo']
        filename = product_photo.filename

        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        product_photo.save(photo_path)

        # Connecting to the database
        connection= pymysql.connect(host='mellymarsh.mysql.pythonanywhere-services.com', user='mellymarsh', password='fobbs123', database='mellymarsh$default')

        cursor= connection.cursor()
        sql = 'INSERT INTO products (product_name, description, product_cost, product_photo) VALUES (%s,%s,%s,%s)'
        data = (product_name,description,product_cost,filename)
        cursor.execute(sql,data)

        connection.commit()
        return jsonify({"message":"Product successfully added😁😁"})

@app.route("/api/cart", methods= ['GET'])
def cart():

       # Connecting to Database
        connection = pymysql.connect(host='mellymarsh.mysql.pythonanywhere-services.com', user='mellymarsh', password='fobbs123', database='mellymarsh$default')
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM products')

        product = cursor.fetchone()
        connection.close()
        return jsonify({'products': product})





# Mpesa Payment Route
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
    if request.method == 'POST':
        # Extract POST Values sent
        amount = request.form['amount']
        phone = request.form['phone']

        # Provide consumer_key and consumer_secret provided by safaricom
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        # Authenticate Yourself using above credentials to Safaricom Services, and Bearer Token this is used by safaricom for security identification purposes - Your are given Access
        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        # Provide your consumer_key and consumer_secret
        response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        # Get response as Dictionary
        data = response.json()
        # Retrieve the Provide Token
        # Token allows you to proceed with the transaction
        access_token = "Bearer" + ' ' + data['access_token']

        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')  # Current Time
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  # Passkey(Safaricom Provided)
        business_short_code = "174379"  # Test Paybile (Safaricom Provided)
        # Combine above 3 Strings to get data variable
        data = business_short_code + passkey + timestamp
        # Encode to Base64
        encoded = base64.b64encode(data.encode())
        password = encoded.decode()

        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password":password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://coding.co.ke/api/confirm.php",
            "AccountReference": "SokoGarden Online",
            "TransactionDesc": "Payments for Products"
        }

        # POPULAING THE HTTP HEADER, PROVIDE THE TOKEN ISSUED EARLIER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        # Specify STK Push  Trigger URL
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        # Create a POST Request to above url, providing headers, payload
        # Below triggers an STK Push to the phone number indicated in the payload and the amount.
        response = requests.post(url, json=payload, headers=headers)
        print(response.text) #
        # Give a Response
        return jsonify({"message": "An MPESA Prompt has been sent to Your Phone, Please Check & Complete Payment"})








app.run(debug = True)
