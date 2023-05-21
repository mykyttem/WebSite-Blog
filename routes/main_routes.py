from flask import Blueprint, render_template, request
import os
import uuid

from flask import render_template, request, redirect, flash, session, current_app
from flask_bcrypt import Bcrypt, check_password_hash
from flask_paginate import Pagination, get_page_args
from sqlalchemy import or_ 

from db import db
from models import Accounts_Users, Posts

""" Main routes, authrization, nav bar, other """

main_routes = Blueprint('main_routes', __name__)

# Main page
@main_routes.route('/', methods=['POST', 'GET'])
def index():

    # search field
    if request.method == 'POST':
        search = request.form['search']
        return redirect(f'/search/{search}')

    return render_template('index.html')


# result search 
@main_routes.route('/search/<string:search>')
def result_posts(search):
    # page arguments
    page, per_page, offset = get_page_args()

    # search context word
    # Apply pagination, and create object paginations
    query  = Posts.query.filter(or_(Posts.title.like(f'%{search}%'), Posts.description.like(f'%{search}%'), Posts.tag.like(f'%{search}%')))
    result_search = query.offset(offset).limit(per_page).all()    

    pagination = Pagination(page=page, per_page=per_page, total=Posts.query.count(), css_framework='bootstrap4')

    return render_template('result_search.html', search=search, result_search=result_search, pagination=pagination)


# Sign up
@main_routes.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    if request.method == "POST":
       # form       
       login = request.form["login"]
       email = request.form["email"]
       avatar = request.files['avatar']
       password = request.form["password"].encode('utf-8') 


       # checking existing account
       search_dublicate_account = db.session.query(Accounts_Users).filter_by(email=email).first()

       if not search_dublicate_account:
    
            bcrypt = Bcrypt()
            password_hash = bcrypt.generate_password_hash(password)


            if avatar:
                # Generate a unique image using UUID and save the avatar
                img = str(uuid.uuid4()) + os.path.splitext(avatar.filename)[1]
                app_config = os.path.join(current_app.config['UPLOAD_FOLDER'] + f'avatars/{img}') 

                avatar.save(app_config)
                avatar_path = os.path.join(app_config)
            else: 
                avatar_path = current_app.config['UPLOAD_FOLDER'] + '/avatars/default_avatar.jpg'


            # save
            save_data = Accounts_Users(img_avatar=avatar_path, login=login, email=email, password=password_hash)
            db.session.add(save_data)
            db.session.commit()
            

            return redirect('/sign-in')
       else:
            flash('Така пошта вже зарегестрована')
            return redirect('/sign-up')


    return render_template('sign_up.html')


# Sign in 
@main_routes.route('/sign-in', methods=['POST', 'GET'])
def sign_in():    
    if request.method == "POST":
       
       # form       
       email = request.form["email"]
       password = request.form["password"].encode('utf-8') 
    
       search_account = db.session.query(Accounts_Users).filter_by(email=email).first()
       if not search_account:
            flash('Такого користувача не існує')
            return redirect('/sign-in')
       
       elif search_account.is_block == True:
           flash(f'Ви були заблоковані, по причині\n "{search_account.reason_block}"')
           return redirect('/sign-in')
       

       if check_password_hash(search_account.password, password):
           # save session
           session['id'] = search_account.id
           session['is_admin'] = search_account.is_admin
           return redirect('/my-profile')
       else:
           flash('Пароль не вірний')
           return redirect('/sign-in')

    return render_template('sign_in.html')