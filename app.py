from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with your own secret key

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Sample data for demonstration purposes
posts = [
    {
        'title': 'First Post',
        'content': 'This is the content of the first post.',
        'author': 'John Doe'
    },
    {
        'title': 'Second Post',
        'content': 'This is the content of the second post.',
        'author': 'Jane Smith'
    }
]





class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])


@app.route('/')
def home():
    return render_template('home.html', posts=posts)

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


@login_manager.user_loader
def load_user(user_id):
    # Load and return the User object based on the user_id
    # Replace with your own logic to retrieve user information from a database or other source
    for user in users:
        if str(user['username']) == user_id:
            return User(user_id, user['username'])
    return None


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])

users = [
    {'username': 'john', 'email': 'john@example.com', 'password': 'password123'},
    {'username': 'jane', 'email': 'jane@example.com', 'password': 'pass456'},
]


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Process the login form data
        username = form.username.data
        password = form.password.data

        # Verify the username and password
        user = None
        for u in users:
            if u['username'] == username and u['password'] == password:
                user = User(username, username)
                break

        if user:
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!', 'danger')

    return render_template('login.html', form=form)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        # Process the form data and create a new post
        title = form.title.data
        content = form.content.data
        author = current_user.username
        # Add the new post to the list of posts
        posts.append({'title': title, 'content': content, 'author': author})
        flash('Post created successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', form=form)





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
        users.append({'username': username, 'email': email, 'password': password})

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
