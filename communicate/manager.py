# -*- coding: utf-8 -*-

import os
import time
import pymysql
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash


app = Flask(__name__)

app.config.update(dict(
	DEBUG=True,
	SECRET_KEY='development key',
	USERNAME='admin',
	PASSWORD='1234'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
	conn = pymysql.connect(host='localhost', user='root', password='1234', db='testdb', charset='utf8')
	return conn

	
def get_db(conn):
	curs = conn.cursor(pymysql.cursors.DictCursor)
	return curs

	
def close_db(conn):
	conn.close()
	
@app.teardown_appcontext
def destroy_session():
	session.pop('logged_in', None)
	
def now():
	now = time.localtime()
	#nowTime = "%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
	nowTime = "%04d-%02d-%02d" % (now.tm_year, now.tm_mon, now.tm_mday)
	return nowTime

@app.route('/')
def show_keyword():
	conn = connect_db()
	curs = get_db(conn)
	sql = "select * from keyword_research"
	curs.execute(sql)
	keywords = curs.fetchall()
	sql = "select * from site_research"
	curs.execute(sql)
	sites = curs.fetchall()
	#config 파일에서 스케쥴 인터벌 값 가져오기
	schedule={"time":1} # 스케쥴
	return render_template('show_entries.html', keywords=keywords, sites=sites, schedule=schedule)


@app.route('/keyword/add', methods=['POST'])
def add_keyword():
	if not session.get('logged_in'):
		abort(401)
	conn = connect_db()
	curs = get_db(conn)
	keyword = request.form['keyword']
	sql = 'insert into keyword_research (keyword, count, recentDate) values (%s, %s, %s)'
	curs.execute(sql, (keyword, 0, now()))
	conn.commit()
	close_db(conn)
	flash('New keyword was successfully saved')
	return redirect(url_for('show_keyword'))

@app.route('/keyword/delete', methods=['POST'])
def delete_keyword():
	if not session.get('logged_in'):
		abort(401)
	conn = connect_db()
	curs = get_db(conn)
	idx = request.form['idx']
	sql = "delete from keyword_research where idx=%s"
	curs.execute(sql, (idx))
	conn.commit()
	close_db(conn)
	flash('Selected keyword was successfully Deleted')
	return redirect(url_for('show_keyword'))
	
	
@app.route('/schedule/edit', methods=['POST'])
def edit_schedule():
	if not session.get('logged_in'):
		abort(401)
	time = request.form['time']
	# Edit schedule source
	flash('Entered Interval was successfully Saved')
	return redirect(url_for('show_keyword'))
	
	
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_keyword'))
	return render_template('login.html', error=error)


@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_keyword'))
	
if __name__ == '__main__':
	app.run()