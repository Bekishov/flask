
from flask import Flask, render_template, request, redirect, flash, url_for,session
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
import os
from models import db,Post, MyUser,Resume
import re
from werkzeug.security import generate_password_hash, check_password_hash
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from werkzeug.utils import secure_filename



app = Flask(__name__, static_url_path='/static/')

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
app.secret_key = os.urandom(24)

@login_manager.user_loader
def load_user(user_id):
    return MyUser.select().where(MyUser.id==int(user_id)).first()



@app.before_request
def before_request():
    db.connect()

@app.after_request
def after_request(response):
    db.close()
    return response



@app.route("/")
def index():
    if 'login_in' in session and session['login_in']:
        all_posts = Post.select()
        return render_template("index.html", posts=all_posts)
    else:
        return redirect('/register/')




@app.route('/profile/<int:id>/')
@login_required
def profile(id):
    user = MyUser.select().where(MyUser.id==id).first()
    posts = Post.select().where(Post.author_id==id)
    return render_template('profile.html', user=user, posts=posts)

@app.route('/create/', methods =('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
            address = request.form['address']
            phone = request.form['phone']
            email = request.form['email']
            education = request.form['education']
            experience = request.form['experience']




            Resume.create(
            name = current_user,
            address = address,
            phone = phone,
            email = email,
            education = education,
            experience = experience

            )
            return redirect('/')
    return render_template('create.html')

@app.route('/<int:id>/')
def retrive_post(id):
    post = Post.select().where(Post.id==id).first()
    
    if post:
        return render_template('post_detail.html', post=post)
    return f'Post with id = {id} does not exist'

@app.route('/<int:id>/update', methods = ('GET', "POST"))
@login_required
def update(id):
    post = Post.select().where(Post.id==id).first()
    if request.method == 'POST':
        if current_user == Post.author:
            if post:
                title = request.form['title']
                description = request.form['description']
                obj = Post.update({
                    Post.title: title,
                    Post.description:description
                }).where(Post.id==id)
                obj.execute()
                return redirect(f'/{id}/')
            return f'Post with id = {id} does not exist'
        return f'You dont have permission to update this post'
    return render_template('update.html', post=post)

def validate_password(password):  
    if len(password) < 8:  
        return False  
    if not re.search("[a-z]", password):  
        return False  
    if not re.search("[A-Z]", password):  
        return False  
    if not re.search("[0-9]", password):  
        return False  
    return True 

@app.route('/<int:id>/delete', methods = ('GET', "POST"))
def delete(id):
    post = Post.select().where(Post.id==id).first()
    if request.method == 'POST':
        if current_user == Post.author:
            if post:
                post.delete_instance()
                return redirect('/')
            return f'Post with id = {id} does not exist'
        return f'You dont have permission to delete this post'
    return render_template('delete.html', post=post)



@app.route('/register/', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'] 
        name = request.form['name'] 
        second_name = request.form['second_name'] 
        password = request.form['password'] 
        age = request.form['age'] 
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'
        user = MyUser.select().where(MyUser.email==email).first()
        if user:
            flash('Email address already exists')
            return redirect('/register/')
        else:
            t1 = len(email)
            t2 = len(name)
            t3 = len(second_name)
            t4 = len(password)
            t5 = len(age)
            if t4 < 8:
                p4 = 'Ваш пароль меньше 8 символов'
            elif re.match(pattern, password) is None:
                MyUser.create(
                    email=email,
                    name=name,
                    second_name=second_name,
                    password = generate_password_hash(password, method = 'sha256'),
                    age=age
                )
                flash('Registration successful. Please login to continue.')
                return redirect('/login/')
            return render_template('register.html')
    return render_template('register.html')




@app.route('/login/', methods = ['GET', 'POST'])
def login():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = MyUser.select().where(MyUser.email==email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect('/login/')
        else: 
            login_user(user)
            return redirect(f'/profile/{user.id}/')
        
    return render_template('login.html')


@app.route('/current_profile/')
@login_required
def current_profile():
    posts = Post.select().where(Post.author_id==current_user.id)
    return render_template('profile.html', user=current_user, posts=posts)

    
    
@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/login/')

@app.route('/resume', methods=['POST'])
def resume():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    education = request.form.get('education')
    experience = request.form.get('experience')




    resume = Resume.create(name=current_user, email=email, phone=phone, address=address, education=education, experience=experience)


    return render_template('resume.html', name=name, email=email, phone=phone, address=address, education=education, experience=experience, user=current_user)


@app.route('/check/', methods = ('GET', "POST"))
def chek():
    all_resume = Resume.select().where(Resume.id==current_user).first()
    
    return render_template('check.html', resumes=all_resume)








if __name__ == "__main__":
    app.run(debug=True)