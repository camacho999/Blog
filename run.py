from flask import Flask, render_template, request, url_for, redirect, abort
from forms import SignupForm, PostForm, LoginForm
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from models import users, get_user, User, Post
from werkzeug.urls import url_parse
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mikey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://scott:@localhost/blogdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

login_manager = LoginManager(app)
login_manager.login_view = "login"
db = SQLAlchemy(app)

from models import User


posts = []

@app.route('/')
def index():
    posts = Post.get_all()
    return render_template('index.html', posts = posts)

@app.route('/p/<string:slug>/')
def show_posts(slug):
    post = Post.get_by_slug(slug)
    if post is None:
        abort(404)
    return render_template('post_view.html', post = post)

@app.route('/admin/post/', methods = ['GET', 'POST'], defaults = {'post_id': None})
@app.route('/admin/post/<int:post_id>/', methods = ['GET', 'POST'])
@login_required
def post_form(post_id):
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        title_slug = form.title_slug.data
        content = form.content.data 

        post = {'title': title, 'title_slug': title_slug, 'content': content}
        posts.append(post)

        return redirect(url_for('index'))
    return render_template('admin/post_form.html', form = form)


@app.route('/signup/', methods=['GET', 'POST'])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignupForm()
    error = None
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        #Comprobando si ya existe el Usuario
        user = User.get_by_email(email)
        if user is not None:
            error = f'El email {email} ya está esta siendo utilizado por otro usuario'
        else:
            #se crea el nuevo usuario
            user = User(name = name, email = email)
            user. set_password(password)
            user.save()
            #se deja al usuario logeado
            login_user(user, remember=True)
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template('signup_form.html', form = form, error = error)
    
    
    
    # if form.validate_on_submit():
    #     name = form.name.data
    #     email = form.email.data
    #     password = form.password.data
    #     #crea usuario y se guardan
    #     user = User(len(users) + 1, name, email, password)
    #     users.append(user)
    #     # se deja usuario logeado
    #     login_user(user, remember = True)
    #     next_page = request.args.get('next', None)
    #     if not next_page or url_parse(next_page).netloc != '':
    #         next_page = url_for('index')
    #     return redirect(next_page)
    # return render_template('signup_form.html', form = form)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc !='':
                next_page = url_for('index')
    return render_template('login_form.html', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
    


@login_manager.user_loader
def load_user(user_id):
    for user in users:
        return User.get_by_id(int(user_id))  