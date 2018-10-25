from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:ammananna27@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True 
db = SQLAlchemy(app)

app.secret_key = 'y337kGcys&zP3B'

class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(120)) 
    entry = db.Column(db.String(240))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    def __init__(self, title, entry, owner):

        self.title= title
        self.entry= entry
        self.owner = owner

tasks = []        

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    tasks = db.relationship('Task', backref='owner')
    

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    #allowed_routes = ['login', 'signup', 'frontpage', 'validate_inputs']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')        


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
            #return redirect('/validate')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html') 


@app.route('/logout')
def logout():
    del session['username'] # when logout deletes the email from the session
    return redirect('/')



@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('signup.html')


#tasks = []

@app.route('/validate', methods=['POST','GET'])
def validate_inputs():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blogtitle = request.form['blogtitle']
        blogtitleerror = '' 
        if (blogtitle==''):
            blogtitleerror = ' Enter Blog title '
             
        blogentry = request.form['blogentry']
        blogentryerror = ''

        if (blogentry==''):
            blogentryerror = ' Enter Blog description '
        if (not blogtitleerror) and (not blogentryerror) :
            newtask=Task(blogtitle,blogentry,owner)
            db.session.add(newtask)
            db.session.commit()
            print("newly created id : " + str(newtask.id))
            return render_template('originalshowblog.html',title="Blogz", task=newtask)
        else:

            return render_template('add.html',title="Blogz", blogtitle=blogtitle,blogtitleerror=blogtitleerror,blogentryerror=blogentryerror)





@app.route('/blog', methods=['POST', 'GET'])
def showblog():
  
    blog_id = request.args.get('id')
    print("id received from form: " + str(blog_id))
    task = Task.query.get(blog_id)
    return render_template('originalshowblog.html',title="Blogz", task=task)

@app.route('/blogz', methods=['POST', 'GET'])
def blogzpage():
    user_id = request.args.get('userid')
    if user_id:
        user = User.query.get(user_id)
        tasks = user.tasks
    else:
        tasks = Task.query.all()
    return render_template('blogpage.html',title="Build a blog", tasks=tasks)    


@app.route('/', methods=['POST', 'GET'])
def frontpage():
    users = User.query.all()
    return render_template('index.html',title="Blogz", users=users)


@app.route('/add', methods=['POST', 'GET'])
def addentry():
    return render_template('add.html',title="Blogz", tasks=tasks)

if __name__ == '__main__':
    app.run()