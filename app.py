from flask import Flask, render_template, request, redirect
import jinja2
import requests
import bs4
from selenium import webdriver
import os
from utils import *
from pymongo import *

app = Flask(__name__)
app.secret_key = 'not_really_secret'
client = MongoClient("mongodb://admin:slimreaper35@ds031541.mongolab.com:31541/safelist")
db = client.get_default_database()
users = db.users

@app.route('/', methods=['GET','POST'])
def hello():
	if request.method == 'POST':
		search = request.form.get('search')
		location = request.form.get('location')
		if not(search):
			return render_template('index.html', error="Cannot leave search blank")
		return redirect('/show/'+search)
	return render_template("index.html")

@app.route('/form', methods=['GET', 'POST'])
def form():
	return render_template("form.html")
	
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
	a="teamsafelist1@gmail.com"
	return render_template('get.html', person=a)
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
		return redirect('/')
	return render_template('signup.html')

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 8000))
	app.run(host='0.0.0.0', port=port,debug=True)