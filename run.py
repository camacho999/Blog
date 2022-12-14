from flask import Flask, render_template, request, url_for, redirect
from forms import SignupForm, PostForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mikey'

posts = []

@app.route('/')
def index():
    return render_template('index.html', posts = posts)

@app.route('/p/<string:slug>/')
def show_posts(slug):
    return render_template('post_view.html', slug_title = slug)

@app.route('/admin/post/')
@app.route('/admin/post/<int:post_id>/')
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
    form = SignupForm()
    if form.validate_on_submit():
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        next = request.args.get('next',None)
        if next:
            return redirect(next)
        return redirect(url_for('index'))
    return render_template("signup_form.html", form = form)