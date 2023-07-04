from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import re
import sqlite3
import blockChain
import os
import cv2
import qrcode
app = Flask(__name__)
 
 
app.secret_key = 'your secret key'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your password'
app.config['MYSQL_DB'] = 'geeklogin'
b=blockChain.blockchain()

with sqlite3.connect('users1.db') as db:
    c = db.cursor()

c.execute('CREATE TABLE IF NOT EXISTS users1 (id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE NOT NULL,password TEXT NOT NULL,role TEXT NOT NULL,level TEXT NOT NULL,loc TEXT NOT NULL);')
db.commit()
db.close()

@app.route('/home', methods =['GET', 'POST'])
@app.route('/', methods =['GET', 'POST'])
def home():
    msg=""
    if request.method == 'POST':
        prod_id = request.form['pid']
        check_list=b.check_id(prod_id)
        if len(check_list)==0:
            msg="Fake product!!!!"
        else:
            return render_template('product_detals.html',p_id=check_list[0]["product_id"],p_name=check_list[0]["dis"],p_cat=check_list[0]["cat"],m_date=check_list[0]["mfdate"],mrp=check_list[0]["mrp"],des=check_list[0]["pname"],loc=check_list[-1]["role"],hash_value=check_list[0]["hash"])


    return render_template('check_prod.html', msg = msg)
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users1.db')
        c = conn.cursor()

        c.execute('SELECT * FROM users1 WHERE username=?', (username,))
        user = c.fetchone()

        if not user:
            return render_template('login1.html', msg='Invalid username or password')

        if not check_password_hash(user[2], password):
            return render_template('login1.html', msg='Invalid username or password')

        session['username'] = username
        #print(user[3])
        if user[3]=="seller":
            print(user[4])
            if user[4]=="Level0":
                level="primary"
            if user[4]=="Level1":
                level="secondry"
            if user[4]=="Level2":
                level="Teritiary"
            loc=user[5]
            return redirect(url_for('seller_profile', username=username, level=level,loc=loc))
            # return render_template('sellr_profile.html', name=username)
        else:
            return redirect(url_for('manufacturer_profile',username=username))
            # return render_template('manu_profile.html', name=username)

    return render_template('login1.html', msg = msg)
  
 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login1'))

@app.route('/seller_profile', methods =['GET', 'POST'])
def seller_profile():
    username = request.args.get('username')
    level = request.args.get('level')
    loc = request.args.get('loc')
    msg=""
    if request.method == 'POST':
        product_id = request.form['pid']
        b.create_block(prod_id=product_id,role=loc)
        msg="Product state updated"
        return render_template('sellr_profile.html',username=username,msg=msg,level=level)
    return render_template('sellr_profile.html',username=username,level=level,msg=msg)
 
@app.route('/manufacturer_profile', methods =['GET', 'POST'])
def manufacturer_profile():
    username = request.args.get('username')
    if request.method == 'POST':
        return redirect(url_for('add_product',username=username))
    return render_template('manu_profile.html', username=username )

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        role = request.form['role']
        level = request.form['level']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        loc = request.form['loc']


        if password != confirm_password:
           return render_template('register1.html', msg='Passwords do not match')

        conn = sqlite3.connect('users1.db')
        c = conn.cursor()

        hashed_password = generate_password_hash(password)

        c.execute('SELECT * FROM users1 WHERE username=?', (username,))
        if c.fetchone():
            return render_template('register1.html', msg='Username already exists')

        c.execute('INSERT INTO users1 (role, username, password, level, loc) VALUES (?, ?, ?, ?, ?)', (role, username, hashed_password, level, loc))
        conn.commit()

        session['username'] = username
        return redirect('/login')

    return render_template('register1.html')
@app.route('/add_product', methods =['GET', 'POST'])
def add_product():
    msg = ''
    username = request.args.get('username')
    if request.method == 'POST':
        product_id = request.form['product-id']
        manufacturing_date= request.form['manufacturing-date']
        mrp = request.form['mrp']
        description = request.form['description']
        product_category = request.form['product-category']
        product_name = request.form['product-name']
        qr = qrcode.make(str(product_id))
        qr.save('static/test/'+str(product_id)+'.png')
        b.create_block(prod_id=product_id,role="manufacturer",mfdate=manufacturing_date,mrp=mrp,pname=description,cat=product_category,dis=product_name)
        return redirect(url_for('manufacturer_profile',username=username))

    return render_template('add_product.html')
if __name__ == '__main__':
    app.run(debug=True)
