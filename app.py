
from datetime import datetime,timedelta
import calendar
from flask import Flask, render_template, request, redirect, url_for,send_from_directory, Response, abort
from werkzeug.utils import secure_filename
import os
from flask_login import LoginManager , login_required , UserMixin , login_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self , username , password , id , active=True):
        self.id = id
        self.username = username
        self.password = password
        self.active = active

    def get_id(self):
        return self.id

    def is_active(self):
        return self.active

    def get_auth_token(self):
        return make_secure_token(self.username , key='secret_key')

class UsersRepository:

    def __init__(self):
        self.users = dict()
        self.users_id_dict = dict()
        self.identifier = 0

    def save_user(self, user):
        self.users_id_dict.setdefault(user.id, user)
        self.users.setdefault(user.username, user)

    def get_user(self, username):
        return self.users.get(username)

    def get_user_by_id(self, userid):
        return self.users_id_dict.get(userid)

    def next_index(self):
        self.identifier +=1
        return self.identifier

users_repository = UsersRepository()

@login_required
def home():
    return "<h1>User Home</h1>"

@app.route('/' , methods=['GET' , 'POST'])
def login():
    authentication = ['hoang','hoang']
    new_user = User(authentication[0], authentication[1], users_repository.next_index())
    users_repository.save_user(new_user)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username,password)
        if username == authentication[0]:
            registeredUser = users_repository.get_user(username)
            print('Users '+ str(users_repository.users))
            print('Register user %s , password %s' % (registeredUser.username, registeredUser.password))
            if registeredUser != None and registeredUser.password == password:
                print('Logged in..')
                login_user(registeredUser)
                return render_template('choose.html')
            else:
                return abort(401)
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return render_template('login.html')

# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    return users_repository.get_user_by_id(userid)


app.config['UPLOAD_PATH'] = 'static/download'

@app.route('/upload', methods=['GET' , 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file_obj = request.files.getlist("file")
        print(file_obj)
        for file in file_obj:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

        return redirect('/file')

    return render_template('index.html')

@app.route('/file')
@login_required
def all_file():
    BASE_DIR = 'static/download/'
    # Joining the base and the requested path
    abs_path = os.path.join(BASE_DIR)
    # Show directory contents
    files = os.listdir(abs_path)
    for f in files:
        ext = os.path.splitext(f)[-1].lower()
        print(ext)
    return render_template('every_file.html', files=files)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    print("Starting app on port %d" % port)
app.run(debug=False, port=port, host='0.0.0.0')

