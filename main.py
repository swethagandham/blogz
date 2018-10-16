from flask  import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://buildablog1:ammananna@localhost:8889/buildablog1'
app.config['SQLALCHEMY_ECHO'] = True 
db = SQLAlchemy(app)

class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(120)) 
    entry = db.Column(db.String(240)) 
    def __init__(self, title, entry):

        self.title= title
        self.entry= entry

tasks = []

@app.route('/validate', methods=['POST','GET'])

def validate_inputs():
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
            newtask=Task(blogtitle,blogentry)
            db.session.add(newtask)
            db.session.commit()
            print("newly created id : " + str(newtask.id))
            return render_template('originalshowblog.html',title="Blog details", task=newtask)
        else:

            return render_template('add.html',title="Build a blog", blogtitle=blogtitle,blogtitleerror=blogtitleerror,blogentryerror=blogentryerror)

@app.route('/blog', methods=['POST', 'GET'])
def showblog():
  
    blog_id = request.args.get('id')
    print("id received from form: " + str(blog_id))
    task = Task.query.get(blog_id)
    return render_template('originalshowblog.html',title="Blog details", task=task)
@app.route('/', methods=['POST', 'GET'])
def frontpage():
    tasks = Task.query.all()
    return render_template('blogpage.html',title="Build a blog", tasks=tasks)
@app.route('/add', methods=['POST', 'GET'])
def addentry():
    return render_template('add.html',title="Build a blog", tasks=tasks)
if __name__ == '__main__':
    app.run()