from flask import Flask, render_template, request, redirect, session
import jinja2
import requests
import bs4
from selenium import webdriver
import os
from utils import *
from pymongo import *
import stripe
import sendgrid

app = Flask(__name__)
app.secret_key = 'not_really_secret'
client = MongoClient("mongodb://admin:slimreaper35@ds031541.mongolab.com:31541/safelist")
db = client.get_default_database()
users = db.users

s  = sendgrid.SendGridClient('parasm', 'bcabooks')

@app.route('/', methods=['GET','POST'])
def hello():
	if request.method == 'POST':
		search = request.form.get('search')
		location = request.form.get('location')
		if not(search):
			return render_template('index.html', error="Cannot leave search blank")
		return redirect('/show/'+search)
	if not logged_in():
		return redirect('/signin')
	return render_template("index.html")

@app.route('/form', methods=['GET', 'POST'])
def form():
	return render_template("form.html")

@app.route('/formdone', methods=['GET', 'POST'])
def formdone():
	return render_template("formdone.html")
	
@app.route('/show')
def showC(item=None):
	page = requests.get("http://philadelphia.craigslist.org/search/sss?query="+"monitor"+"&sort=rel")
	if item:
		page = requests.get("http://philadelphia.craigslist.org/search/sss?query="+item+"&sort=rel")
	soup = bs4.BeautifulSoup(page.text)
	links = soup.select('a.hdrlnk')
	prices = soup.select('span.price')
	images = soup.select('img')
	print images
	stringLinks = []
	onlyLinks = []
	for x in range(0,len(links)):
		a = str(links[x]).replace("href=\"/", "target=\"_tab\"href=\"http://philadelphia.craigslist.org/").replace("pic","")
		stringLinks.append(a)
		onlyLinks.append(a[a.find("href")+40:a.find("html")-1])
	length = 20
	if (len(stringLinks) < 20):
		length = len(stringLinks)
	return render_template('display.html', prices=prices, items=stringLinks, links = onlyLinks, length = length)
@app.route('/show/<item>')
def showItem(item):
	return showC(item)
@app.route('/<shop>/<id>')
def show(shop,id):
	# driver = webdriver.PhantomJS(executable_path="vendor/phantomjs/bin/phantomjs")
	# driver.get("http://philadelphia.craigslist.org/"+shop+"/"+id+".html")
	# driver.find_element_by_class_name("reply_button").click()
	# a = driver.find_element_by_class_name("anonemail")
	a = "teamsafelist1@gmail.com"
	message = sendgrid.Mail()
	message.add_to("teamsafelist1@gmail.com")
	message.set_from("test@safelist.com")
	email_str = '''
	<style>


	</style>
	<div class="container">
		<div class="row">
			<div class="col-md-4"></div>
			<div class="col-md-4">
				<h1>Safelist</h1>
			</div>
			<div class="col-md-4"></div>
		</div>
		<form action="/" method="POST">
		<div class="center"><h3>Safelist is a way for people to purchase off Craigslist in a safe way. This is a request for a purchase. If you accept, the transaction will be handled by us and the pickup will be handles by postmates (a delivery service). To accept the offer, fill out this form with the pickup and payment information. You may contact the buyer at: </h3></div>
		<br>
		<div class="row">
			<div class="col-md-4"></div>
			<div class="col-md-4">
				<input class="form-control circle" placeholder="Address" name="address">
			</div>
			<div class="col-md-4"></div>
		</div>
		<br>
		<div class="row">
			<div class="col-md-4"></div>
			<div class="col-md-4">
				<input class="form-control circle" placeholder="Time" name="time">
			</div>
			<div class="col-md-4"></div>
		</div>
		<br>
		<div class="center">
			<h3>Price: </h3>
			<br>
			<button class="btn btn-lg btn-primary" id="accept">Accept</button>
			<button class="btn btn-lg btn-primary" style="background-color:red"id="decline">Decline</button>
		</div>
		</form>
	</div>
	'''
	message.set_subject("Interested In Buying")
	message.set_html(email_str)
	print s.send(message)
	return render_template('get.html', person=a)
@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
	if request.method == 'POST':
		username = request.form.get('username').lower()
		password = request.form.get('password')
		if not(username):
			return render_template('signin.html', username_error="No username found.")
		if not(password):
			return render_template('signin.html', password_error="No password found.", username=username)
		user = users.find_one({'username':username})
		if user is None:
			return render_template('signin.html', username_error="No account found!", username=username)
		if not(valid_pw(username,password,user.get('password'))):
			return render_template('signin.html', error="Invalid username and password.", username=username)
		session_login(username, user.get('name'))
		return redirect('/')
	if logged_in():
		return redirect('/')
	return render_template('signin.html',signed_in=logged_in())
@app.route('/signup', methods=['GET','POST'])
def signup():
	if request.method == 'POST':
		full_name = request.form.get('full_name')
		username = request.form.get('username').lower()
		email = request.form.get('email')
		phone = request.form.get('phone')
		password = request.form.get('password')
		password_confirm = request.form.get('password_confirm')
		if not full_name:
			return render_template('signup.html', full_name_error="Please enter a name.")
		if not username:
			return render_template('signup.html', username_error="Please enter a username.")
		if not email:
			return render_template('signup.html', email_error="Please enter a email.")
		if not phone:
			return render_template('signup.html', phone_error="Please enter a phone number.")
		if not valid_number(phone):
			return render_template('signup.html', phone_error="Please enter a valid phone number.")
		if not valid_email(email):
			return render_template('signup.html', email_error="Please enter a valid email.")
		if not password:
			return render_template('signup.html', password_error="Please enter a password.")
		if not password_confirm:
			return render_template('signup.html', password_confirm_error="Please re-type your password.")
		if not valid_username(username):
			return render_template('signup.html', username_error="Enter a valid username.")
		if not valid_password(password):
			return render_template('signup.html', password_error="Enter a valid password.")
		if password != password_confirm:
			return render_template('signup.html', password_confirm_error="Passwords must match")
		result = users.find_one({"username":username})
		if not result is None:
			if valid_pw(username, password, result.get('password')):
				session['username'] = username
				session['name'] = result.get('name')
				return redirect('/')
			else:
				return render_template('signup_tutor.html', username_error="Username taken.")
		password = make_pw_hash(username,password)
		user_id = users.insert({"username": username,"password": password,"name":full_name,'email':email,"phone":phone,'old_purchases':[]})
		session_login(username, full_name)
		return redirect('/')
	return render_template('signup.html')
# @app.route('/response', methods=['GET','POST'])
# def signup():
# 	pass
if __name__ == '__main__':
	port = int(os.environ.get('PORT', 8000))
	app.run(host='0.0.0.0', port=port,debug=True)