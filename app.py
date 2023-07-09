import sqlite3
from flask import Flask, render_template, redirect, url_for, flash, g
from flask_wtf import FlaskForm
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with your own secret key
app.config['DATABASE'] = 'blog.db'  # SQLite database file path

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    # Load and return the User object based on the user_id
    # Replace with your own logic to retrieve user information from a database or other source
    cursor = get_db().execute("SELECT username FROM users WHERE username=?", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    if row:
        return User(user_id, row[0])
    return None


def get_db():
    # Connect to the SQLite database
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    # Close the SQLite database connection
    db = g.pop('db', None)
    if db is not None:
        db.close()


class User:
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    author = TextAreaField('author', validators=[DataRequired()])


@app.route('/')
def home():
    cursor = get_db().execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    cursor.close()
    return render_template('home.html', posts=posts)


@app.route('/post/<int:post_id>')
def view_post(post_id):
    cursor = get_db().execute("SELECT * FROM posts WHERE id=?", (post_id,))
    post = cursor.fetchone()
    cursor.close()
    if post:
        return render_template('post.html', post=post)
    flash('Post not found!', 'danger')
    return redirect(url_for('home'))


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        # Process the form data and create a new post
        title = form.title.data
        content = form.content.data
        author = current_user.username
        cursor = get_db().execute("INSERT INTO posts (title, content, author) VALUES (?, ?, ?)",
                                  (title, content, author))
        get_db().commit()
        cursor.close()
        flash('Post created successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', form=form)


@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    cursor = get_db().execute("SELECT * FROM posts WHERE id=?", (post_id,))
    post = cursor.fetchone()
    cursor.close()
    if post:
        if post['author'] == current_user.username:
            form = CreatePostForm()
            if form.validate_on_submit():
                # Process the form data and update the post
                title = form.title.data
                content = form.content.data
                author = form.author.data
                cursor = get_db().execute("UPDATE posts SET title=?, content=?, author=? WHERE id=?",
                                          (title, content,author, post_id))
                get_db().commit()
                cursor.close()
                flash('Post updated successfully!', 'success')
                return redirect(url_for('view_post', post_id=post_id))
            else:
                form.title.data = post['title']
                form.content.data = post['content']
            return render_template('edit_post.html', form=form, post=post)
        flash('You are not authorized to edit this post!', 'danger')
        return redirect(url_for('view_post', post_id=post_id))
    flash('Post not found!', 'danger')
    return redirect(url_for('home'))





class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Process the login form data
        username = form.username.data
        password = form.password.data

        # Verify the username and password
        user = None
        # for u in users:
        #     if u['username'] == username and u['password'] == password:
        #         user = User(username, username)
        #         break
        cursor = get_db().execute("SELECT username, password FROM users  WHERE username=? and password=?",
                                   (username,password))
        entry = cursor.fetchone()
        if entry[0] and entry[1]:
            user = User(username, password)
        cursor.close()
        if user:
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!', 'danger')

    return render_template('login.html', form=form)








@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Process the registration form data
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Add the new user to the list of users (for demonstration purposes)
        cursor = get_db().execute('''INSERT INTO users (username, email, password)
                                   VALUES (?, ? , ?)''',
                                          (username, email, password))
        get_db().commit()
        cursor.close()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
