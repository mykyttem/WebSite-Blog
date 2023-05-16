import os
import uuid
from functools import wraps

from flask import Blueprint, render_template, session, redirect, request, current_app

from models import Posts, Accounts_Users
from db import db


# This file, for urls /admin, or /admin/settings other
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# decorator, checking of admin user or not, and authorization
def is_admin(f):
    @wraps(f)
    def decorated_is_admin(*args, **kwargs):
        session_is_admin = session.get('is_admin')
        if session_is_admin == False or not 'is_admin' in session:
            return redirect('/my-profile')
        return f(*args, **kwargs)
    return decorated_is_admin


@admin_bp.route('/')
@is_admin
def admin():
    return render_template('admin_panel.html')


# create post
@admin_bp.route('/add-post', methods=['POST', 'GET'])
@is_admin
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        tag = request.form['tags']
        image = request.files['image-post']
        type = request.form['type']

        if image:
            # Generate a unique image using UUID and save the avatar
            img = str(uuid.uuid4()) + os.path.splitext(image.filename)[1]
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'] + f'posts/{img}')

            image.save(image_path)
        else: 
            image_path = current_app.config['UPLOAD_FOLDER'] + 'posts/default_post.jpeg'


        # save
        tags = tag.split()
        edit_tags = ""

        for i in tags:
            edit_tags += f'#{i} '


        save_data = Posts(title=title, description=description, tag=edit_tags, image=image_path, type=type)
        db.session.add(save_data)
        db.session.commit()

      
        return redirect('./list-posts')

    return render_template('add_post.html')


# list posts
@admin_bp.route('/list-posts', methods=['POST', 'GET'])
@is_admin
def list_posts():
    posts = db.session.query(Posts).all()

    if 'post-delete' in request.form:
        id_post = request.form['post-delete']

        db.session.query(Posts).filter_by(id=id_post).delete()
        db.session.commit()

        return redirect('./list-posts')
    

    return render_template('list_posts.html', posts=posts)


# edit post
@admin_bp.route('/list-posts/editor-post/<string:title>/<int:id>', methods=['POST', 'GET'])
@is_admin
def editor_posts(title, id):
    edit_post = db.session.query(Posts).filter_by(id=id).all()
    
    if request.method == 'POST':
        edit_title = request.form['title']
        description = request.form['description']
        tag = request.form['tags']
        image = request.files['image-post']
        type = request.form['type']


        if image:
            # Generate a unique image using UUID and save the avatar
            img = str(uuid.uuid4()) + os.path.splitext(image.filename)[1]
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'] + f'posts/{img}')

            image.save(image_path)
        else: 
            image_path = current_app.config['UPLOAD_FOLDER'] + 'posts/default_post.jpeg'

        # save
        tags = tag.split()
        edit_tags = ""

        for i in tags:
            edit_tags += f'#{i} '


        db.session.query(Posts).filter_by(id=id).update(
            {
                'title': edit_title,
                'description': description,
                'tag': edit_tags,
                'image': image_path,
                'type': type
            }   
        )

        db.session.commit()
        return redirect('/admin/list-posts')


    return render_template('editor_post.html', edit_post=edit_post)


# list users
@admin_bp.route('/list-users', methods=['POST', 'GET'])
@is_admin
def list_users():
    users = db.session.query(Accounts_Users).all()

    # block user
    if 'reason-block' in request.form:
        reason_block = request.form['reason-block']
        id_block_user = request.form['id-block-user']
        

        db.session.query(Accounts_Users).filter_by(id=id_block_user).update(
            {'is_block': True, 'reason_block': reason_block}
        )


        db.session.commit()
        return redirect('/admin/list-users')


    # unblock
    if 'unblock-user' in request.form:
        unblock_user = request.form['unblock-user']
        
        db.session.query(Accounts_Users).filter_by(id=unblock_user).update(
            {'is_block': False}
        )

        db.session.commit()
        return redirect('/admin/list-users')


    return render_template('list_users.html', users=users)