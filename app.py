from flask import Flask, render_template, request, redirect
import jinja2
import requests
import bs4
from selenium import webdriver
import os

app = Flask(__name__)

@app.route('/')
def hello():
	return render_template("index.html")

@app.route('/change')
def chance():
	return redirect('/')

@app.route('/showC')
def showC(item=None):
	page = requests.get("http://philadelphia.craigslist.org/search/sss?query="+"monitor"+"&sort=rel")
	if item:
		page = requests.get("http://philadelphia.craigslist.org/search/sss?query="+item+"&sort=rel")
	soup = bs4.BeautifulSoup(page.text)
	links = soup.select('a.hdrlnk')
	stringLinks = []
	onlyLinks = []
	for x in range(0,len(links)):
		a = str(links[x]).replace("href=\"/", "href=\"http://philadelphia.craigslist.org/").replace("pic","")
		stringLinks.append(a)
		onlyLinks.append(a[a.find("href")+40:a.find("html")-1])
	length = 20
	if (len(stringLinks) < 20):
		length = len(stringLinks)
	return render_template('display.html', items=stringLinks, links = onlyLinks, length = length)
@app.route('/showC/<item>')
def showItem(item):
	return showC(item)
@app.route('/<shop>/<id>')
def show(shop,id):
	driver = webdriver.PhantomJS(executable_path='phantomjs')
	driver.get("http://philadelphia.craigslist.org/"+shop+"/"+id+".html")
	driver.find_element_by_class_name("reply_button").click()
	a = driver.find_element_by_class_name("anonemail")
	return render_template('get.html', person=a.text)
@app.route('/post', methods=['GET','POST'])
def post():
	if request.method == 'POST':
		return render_template('post.html')
	return render_template('get.html')

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 8000))
	app.run(host='0.0.0.0', port=port,debug=True)