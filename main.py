from flask import Flask, request, redirect, render_template,session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['DEBUG'] = True
#create connection string which connects to db
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:ammananna27@localhost:8889/blogz'

app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app) 

app.secret_key = os.urandom(24)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_post = db.Column(db.String(120))
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self, blog_title,blog_post, owner):
        self.blog_title = blog_title
        self.blog_post = blog_post
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username =  db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog',backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    #list of routes that users dont have to log in to see
    allowed_routes = ['login', 'signup','index','mainblog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST','GET'])
def login():
    #check for request type
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #verify users password
        
        #allows us to select only the first result in a result set
        user = User.query.filter_by(username=username).first()
        # if checks does the user exsits
        #if the user is not none from the query i.e if user exsists then compare the password
        #then log in
        if user and user.password == password:
            #TODO - "remember" that the user has logged in
            session['username'] = username #next time the user log in the session object looks for that 
            flash("Logged in")#flash messages use the sesion object to store the message for the next time the user comes back

            return redirect('/newpost')
        else:

            #TODO - explain why login failed
            flash('User password incorrect, or user doesnot exsits','error')
            #return '<h1>Error! </h1>'

    return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        
        #TODO - validate users data
        error = validate_user(username,password,verify)
        #find the user exsists in the database with same username
        existing_user = User.query.filter_by(username=username).first()       
            #if user doesnot exsits create a new user
        if not existing_user and not error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            # TODO - "remember" the user
            session['username'] = username
            return redirect('/newpost')
        elif existing_user:
            #TODO - user better response messaging
            flash("user already exists","error")
            #return render_template('signup.html')
            # return "<h1> User already exists</h1>"
            

    return render_template('signup.html')

def validate_user(username,password,verify):
    error_msg = ""
    if username == "" or password == "" or verify == "":
        error_msg = "one or more fields are invalid"
        flash(error_msg,"error")
    elif password != verify:
        error_msg = "passwords doesnot match"
        flash(error_msg,"error")
    elif len(username)<3 or len(username)>20 or username ==" ":
        error_msg = "invalid username"
        flash(error_msg,"error")
    elif len(password)<3 or len(password)>20 or password ==" ":
        error_msg ="invalid password"
        flash(error_msg,"error")
    
    return error_msg

@app.route('/blog', methods=['GET'])
def mainblog():
    id = request.args.get('id')

    user = request.args.get('user')
    print("user is : ",user)
    
        
    if id:
        id=request.args.get('id')
        print("our id = " , id)
        indi_post = Blog.query.filter_by(id=id).first()
        print("individual = " ,indi_post.blog_title,indi_post.blog_post)
        return render_template('individualpost.html',indi_post=indi_post)
    
    if user:
        print("single user ")
        owner = User.query.filter_by(username=user).first()
        print("user owner = ",owner)
        blogs = Blog.query.filter_by(owner=owner).all()
        print("blogs query = ",blogs)
                
        return render_template("singleuser.html", blogs = blogs,owner=owner)
    else:
        blogs = Blog.query.all()
        user = User.query.all()
        return render_template("mainblog.html", blogs=blogs, user=user)

#@app.route('/blog/<user>',) 


@app.route('/newpost', methods=['POST','GET'])
def new_post():
    #get the owner of the blog
    owner = User.query.filter_by(username=session['username']).first()
    print("owner = ",owner)
    if request.method == 'POST':
        new_blogtitle = request.form['newblogtitle']
        new_blog = request.form['newblog']
        blogtitle_error = ""
        blogbody_error = ""
        
        
        if new_blogtitle == "" or new_blog == "":
            blogtitle_error = "Please fill in the title"
            blogbody_error = "Please fill in the body"
                       
            return render_template('post_newblog.html',title_error=blogtitle_error,body_error=blogbody_error)

        else:      
            new_blogs = Blog(new_blogtitle, new_blog, owner)
            #db.session.add(new_blogs)
            print("constructor=",new_blogs)
            db.session.add(new_blogs)
            db.session.commit()
            user = owner.username
            print("username value = ", user)
            return redirect('/blog?user='+ user)

               
    return render_template('post_newblog.html')

@app.route('/logout')
def logout():
    del session['username'] # when logout deletes the email from the session
    return redirect('/blog')


@app.route('/')
def index():
    
    #display a list of all the usernames
    users = User.query.all()

    return render_template('index.html', users=users)    
if __name__ == '__main__':
    app.run()
