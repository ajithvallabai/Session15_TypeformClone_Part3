import re
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from forms import SigUpForm, IDNumber
from werkzeug import secure_filename
import smtplib 
from datetime import datetime
import random
import uuid
import time 
import os 
app = Flask(__name__)
app.config['SECRET_KEY'] = uuid.uuid4().hex
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///friends.db'
#random.seed(0)

#init
db = SQLAlchemy(app)
# create db model
class Friends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # Create a function to return a string
    def __repr__(self):
        return '<Name %r>' % self.id 


subscribers = []

class UserAccountDatabase(db.Model):
    accountID = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(200), nullable = False)
    password = db.Column(db.String(200), nullable = False)
    
    def __repr__(self) -> str:
        return "<User %r>" % self.accountID


def create_tsai_account():

    """
    Creating tsai account
    """
    #tsai_account = UserAccountDatabase(accountID=1113,username="ajith",password="pass123!")
    #if not UserAccountDatabase.query.get_or_404(1111):
    #db.session.add(tsai_account)
    #db.session.commit()
    #print(UserAccountDatabase.query.get_or_404(username="ajith").password)
    obj = UserAccountDatabase.query.filter_by(username="tsai").first()
    print(obj.username, obj.password)
    return 0

class QuizCurrentDatabase(db.Model):
    sessionid = db.Column(db.Integer, primary_key = True)
    qcount = db.Column(db.Integer)
    currentuser = db.Column(db.String(200))
    currentquizid = db.Column(db.Integer)
    currentquizquestions = db.Column(db.String(500))
    currentanswerid = db.Column(db.Integer)
    
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self) -> str:
        return "<Current Notations>"
    

# class QuizCreatedQuestions(db.Model):
#     userid = db.Column(db.String(200), primary_key = True)
#     databaseuserinput = db.Column(db.String(500), nullable = False)
#     createdquestions = db.Column(db.String(500), nullable = False)
#     def __repr__(self) -> str:
#         return "<Created questions>"

class QuizUserInput(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    uanswerid = db.Column(db.Integer)
    uquizid = db.Column(db.Integer)
    userid = db.Column(db.String(200))
    questions = db.Column(db.String(200))
    answer = db.Column(db.String(200))

class QuizCreatedQuestions(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    cquizid =  db.Column(db.Integer)
    userid = db.Column(db.String(200))
    questions = db.Column(db.String(200))



@app.route('/about')
def about():
    title = "About Typeforms"
    details = "This is a TSAI Assignment."
    return render_template("about.html", detail=details, title=title)


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/selectquiz')
def selectquiz():
    form_id = IDNumber()
    # if request.method == "POST":
    #     result = request.form 
    #     print(result["number"])
    #     return render_template('selectedquiz.html')

    
    #if request.method == "POST":
    #result = request.form 
    #print(result["number"])
    #quiz_data.data_quiz_1 = quiz_data.created_questions[result["number"]]
    createdsession = QuizCurrentDatabase.query.order_by(QuizCurrentDatabase.date_created.desc()).first()
    dataforshow = QuizCreatedQuestions.query.filter_by(userid=createdsession.currentuser).all()
    print(dataforshow)
    createdquestion_byuser = {}
    for each in dataforshow:
        print(each.userid,each.sno, each.questions, each.cquizid)
        if each.cquizid not in createdquestion_byuser:
            createdquestion_byuser[each.cquizid] = [each.questions]
        else:    
            createdquestion_byuser[each.cquizid].append(each.questions)
    time.sleep(2)
    print("created quest by user",createdquestion_byuser)
    return render_template('selectedquiz.html',form=form_id, created_quesitons = createdquestion_byuser)

def get_data():
    createdsession = QuizCurrentDatabase.query.order_by(QuizCurrentDatabase.date_created.desc()).first()
    dataforshow = QuizCreatedQuestions.query.filter_by(userid=createdsession.currentuser).all()
    print(dataforshow)
    createdquestion_byuser = {}
    for each in dataforshow:
        print(each.userid,each.sno, each.questions, each.cquizid)
        if each.cquizid not in createdquestion_byuser:
            createdquestion_byuser[each.cquizid] = [each.questions]
        else:    
            createdquestion_byuser[each.cquizid].append(each.questions)
    return createdquestion_byuser

@app.route('/goforquiz' ,methods=['POST','GET'])
def goforquiz():
    if request.method == "POST":        
        result = request.form
        createdquestion_byuser = get_data()
        if int(result["quiznumber"]) in createdquestion_byuser:
            createdsession = QuizCurrentDatabase.query.order_by(QuizCurrentDatabase.date_created.desc()).first()
            createdsession.currentquizid = result["quiznumber"]
            stringfiedquestion = ""
            for ele in createdquestion_byuser[int(result["quiznumber"])]:
                stringfiedquestion +=  ele + ","
            stringfiedquestion = stringfiedquestion[:len(stringfiedquestion)-1]
            createdsession.currentquizquestions = stringfiedquestion
            print("stringified quiz",stringfiedquestion)
            print("qcount-",createdsession.qcount)
            db.session.commit()
            return render_template('goforquiz.html',detail = "Quiz ID is present",status = "success")
        else:
            return render_template('goforquiz.html',detail = "Quiz ID is not present",status = "failure")
        # if its not there then wrong quiz no
    return render_template('goforquiz.html',detail = "Quiz ID is not present",status = "failure")

@app.route('/quiz' ,methods=['POST','GET'])
def quiz():
    try:
        createdsession = QuizCurrentDatabase.query.order_by(QuizCurrentDatabase.date_created.desc()).first()         
        data_quiz_questions= createdsession.currentquizquestions.split(",")        
    except:
        return render_template('failed.html')
    
    if request.method == "POST":
        if createdsession.qcount == 0:
            createdsession.currentanswerid = int(random.random()*1e7)
        
        result = request.form        
        #quiz_data.user_input.append([data_quiz_questions[createdsession.qcount],result.to_dict(flat=False)["answer"][0]])
        u_input = QuizUserInput(sno=int(random.random()*1e9),uanswerid=createdsession.currentanswerid,uquizid=createdsession.currentquizid,
            userid=createdsession.currentuser,questions=data_quiz_questions[createdsession.qcount],answer=result.to_dict(flat=False)["answer"][0])
        createdsession.qcount += 1
        db.session.add(u_input)
        db.session.commit()
        
    button_name = "Next"
    if createdsession.qcount == len(data_quiz_questions)-1:
        button_name = "submit"
    return render_template('quiz.html', data_quiz=data_quiz_questions[createdsession.qcount], button_name=button_name)

@app.route('/thanks',methods=['POST','GET'])
def thanks():   
    try:
        createdsession = QuizCurrentDatabase.query.order_by(QuizCurrentDatabase.date_created.desc()).first() 
        
        data_quiz_questions= createdsession.currentquizquestions.split(",")
        
    except:
        return render_template('failed.html')
    print("thanks page=",createdsession.currentanswerid)
    if request.method == "POST":
        result = request.form        
        #quiz_data.user_input.append([data_quiz_questions[createdsession.qcount],result.to_dict(flat=False)["answer"][0]])
        #print(quiz_data.user_input)
        
        #quiz_data.database_user_input.update({int(random.random()*1e8):quiz_data.user_input})
        
        u_input = QuizUserInput(sno=int(random.random()*1e9),uanswerid=createdsession.currentanswerid,uquizid=createdsession.currentquizid,
            userid=createdsession.currentuser,questions=data_quiz_questions[createdsession.qcount],answer=result.to_dict(flat=False)["answer"][0])
        db.session.add(u_input)
        
        createdsession.currentanswerid = -1
        createdsession.qcount = 0
        createdsession.currentquizquestions = ""
        createdsession.currentquizid = -1
        db.session.commit()
    return render_template('thanksyou.html')

@app.route('/archives',methods=['POST','GET'])
def display_all_user_inputs():
    
    userinputlist = QuizUserInput.query.all()
    db_user_input = {}
    for each in userinputlist:
        if each.uanswerid not in db_user_input:
            db_user_input[each.uanswerid] = [[each.questions, each.answer]]
        else:
            db_user_input[each.uanswerid].append([each.questions, each.answer])
        #each.uanswerid ,each.questions, each.answer
        print(each.uanswerid,each.questions, each.answer)
    return render_template('displayall.html', user_datas = db_user_input)


@app.route('/home',methods=['POST','GET'])
def home():
    createdsession = QuizCurrentDatabase.query.order_by(QuizCurrentDatabase.date_created.desc()).first()
    return render_template('accountpage.html', username=createdsession.currentuser)



@app.route('/', methods=['POST', 'GET'])
def index():    
    form = SigUpForm()
    
    if form.is_submitted():
        result = request.form        
        try:
            user_detail_db = UserAccountDatabase.query.filter_by(username=result["username"]).first()
            print("inputsign",user_detail_db.username,user_detail_db.password)
            if user_detail_db.password == result["password"]:
                
                new_session = QuizCurrentDatabase(sessionid=int(random.random()*1e4), currentuser=user_detail_db.username,
                        currentquizquestions="",qcount=0,currentquizid=-1)
                db.session.add(new_session)
                db.session.commit()
                return  render_template('accountpage.html', username=result["username"])
            else:
                print("failure 1")
                return render_template('signup.html', form=form, failure = "true")
        except:
            print("failure 2")
            return render_template('signup.html', form=form, failure = "true")
    print("failure 3")
    return render_template('signup.html', form=form, failure = "false")


@app.route('/createquiz', methods=['POST','GET'])
def createquiz():
    #QuizCreatedQuestions
    createdsession = QuizCurrentDatabase.query.order_by(QuizCurrentDatabase.date_created.desc()).first()
    #obj = db.session.query(QuizCurrentDatabase).order_by(QuizCurrentDatabase.date_created.desc()).first()
    question = 0
    print("session id-",createdsession.sessionid,createdsession.currentquizid )
    
    if createdsession.currentquizid == -1:
        
        createdsession.currentquizid =int(random.random()*1e8)
        quiz_id = createdsession.currentquizid
        print("new session id created ",quiz_id)
    else:
        quiz_id = createdsession.currentquizid

    if request.method == "POST":
        result = request.form
        print(result)
        
        cq = QuizCreatedQuestions(sno=int(random.random()*1e5)  ,cquizid=createdsession.currentquizid, userid=createdsession.currentuser ,
                    questions=result["answer"])
        db.session.add(cq)
        db.session.commit()
        
    return render_template('creatingquiz.html', quiz_id = quiz_id )

@app.route('/createdquizes/<int:id>', methods=['POST','GET'])
def createdquizes(id):
    quiz_id = id
    if request.method == "POST":
        result = request.form
        createdsession = QuizCurrentDatabase.query.order_by(QuizCurrentDatabase.date_created.desc()).first()
        cq = QuizCreatedQuestions(sno=int(random.random()*1e5)  ,cquizid=quiz_id, userid=createdsession.currentuser ,
                    questions=result["answer"])
        db.session.add(cq)
        db.session.commit()
        createdsession.currentquizid = -1
        print("current quiz id-",createdsession.currentquizid)
        print(QuizCreatedQuestions.query.all())
        print("session id-",createdsession.sessionid)
    return render_template('thanksyou.html')

@app.route('/showallquiztypes', methods=['POST','GET'])
def showallquiztypes():
    createdsession = QuizCurrentDatabase.query.order_by(QuizCurrentDatabase.date_created.desc()).first()
    dataforshow = QuizCreatedQuestions.query.filter_by(userid=createdsession.currentuser).all()
    createdquestion_byuser = {}
    for each in dataforshow:
        print(each.userid,each.sno, each.questions, each.cquizid)
        if each.cquizid not in createdquestion_byuser:
            createdquestion_byuser[each.cquizid] = [each.questions]
        else:    
            createdquestion_byuser[each.cquizid].append(each.questions)

    # UserAccountDatabase.query.filter_by(username="ajith").first())
    return render_template("displayquiztypes.html", created_quesitons = createdquestion_byuser)

### share feature 

class ShareCurrentDatabase(db.Model):
    sessionid = db.Column(db.Integer, primary_key = True)
    qcount = db.Column(db.Integer)
    currentuser = db.Column(db.String(200))
    currentquizid = db.Column(db.Integer)
    currentquizquestions = db.Column(db.String(500))
    currentanswerid = db.Column(db.Integer)
    
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self) -> str:
        return "<Share DB>"

@app.route('/sharequizfront', methods=['POST','GET'])
def sharequizfront():
    if request.method == "POST":
        result = request.form
        print(result["quizno"])
        return render_template("sharequizfront.html",sharingurl="true",quizid=result["quizno"])
    return render_template("sharequizfront.html",sharingurl="false")

@app.route('/sharequiz/<int:id>/<int:startid>', methods=['POST','GET'])
def sharequiz(id,startid):
    try:
        createdquestion_byuser = get_data()
        if startid == 0:
            new_session = ShareCurrentDatabase(sessionid=int(random.random()*1e4), currentuser=int(random.random()*1e5),
                            currentquizquestions="", qcount=0, currentquizid=id)
            db.session.add(new_session)
            db.session.commit()
        createdsession = ShareCurrentDatabase.query.order_by(ShareCurrentDatabase.date_created.desc()).first()
        createdsession.currentquizid = id
        stringfiedquestion = ""
        for ele in createdquestion_byuser[int(id)]:
            stringfiedquestion +=  ele + ","
        stringfiedquestion = stringfiedquestion[:len(stringfiedquestion)-1]
        createdsession.currentquizquestions = stringfiedquestion
        print("stringified quiz",stringfiedquestion)
        print("qcount-",createdsession.qcount)
        db.session.commit()
        #createdsession = ShareCurrentDatabase.query.order_by(ShareCurrentDatabase.date_created.desc()).first()         
        data_quiz_questions= createdsession.currentquizquestions.split(",")
                
    except:
        return render_template('failed.html')
    
    if request.method == "POST":
        if createdsession.qcount == 0:
            createdsession.currentanswerid = int(random.random()*1e7)
        
        result = request.form        
        #quiz_data.user_input.append([data_quiz_questions[createdsession.qcount],result.to_dict(flat=False)["answer"][0]])
        u_input = QuizUserInput(sno=int(random.random()*1e9),uanswerid=createdsession.currentanswerid,uquizid=createdsession.currentquizid,
            userid=createdsession.currentuser,questions=data_quiz_questions[createdsession.qcount],answer=result.to_dict(flat=False)["answer"][0])
        createdsession.qcount += 1
        db.session.add(u_input)
        db.session.commit()
        
    button_name = "Next"
    print(createdsession.qcount , len(data_quiz_questions)-1)
    if createdsession.qcount == len(data_quiz_questions)-1:
        button_name = "submit"
    print("button name",button_name)
    return render_template('sharequiz.html', qid = id, start = startid,
         data_quiz = data_quiz_questions[createdsession.qcount], button_name=button_name)

@app.route('/sharethanks',methods=['POST','GET'])
def sharethanks():   
    try:
        createdsession = ShareCurrentDatabase.query.order_by(ShareCurrentDatabase.date_created.desc()).first() 
        
        data_quiz_questions= createdsession.currentquizquestions.split(",")
        
    except:
        return render_template('failed.html')
    print("thanks page=",createdsession.currentanswerid)
    if request.method == "POST":
        result = request.form        
        #quiz_data.user_input.append([data_quiz_questions[createdsession.qcount],result.to_dict(flat=False)["answer"][0]])
        #print(quiz_data.user_input)
        
        #quiz_data.database_user_input.update({int(random.random()*1e8):quiz_data.user_input})
        
        u_input = QuizUserInput(sno=int(random.random()*1e9),uanswerid=createdsession.currentanswerid,uquizid=createdsession.currentquizid,
            userid=createdsession.currentuser,questions=data_quiz_questions[createdsession.qcount],answer=result.to_dict(flat=False)["answer"][0])
        db.session.add(u_input)
        
        createdsession.currentanswerid = -1
        createdsession.qcount = 0
        createdsession.currentquizquestions = ""
        createdsession.currentquizid = -1
        db.session.commit()
    return render_template('thanksyou.html')

## Upload feature 
@app.route('/uploadpage', methods = ['POST','GET'])
def uploadpage():
    if request.method == "POST":
        print(request.files)
        file = request.files['file']
        filename = secure_filename(file.filename) 
        file.save(os.path.join("files",filename))
        usergiven_question = []

        # with open(os.path.join("files",filename)) as f:
        #     file_content = f.read()
        #     print(file_content)
        #     usergiven_question.append(file_content)

        with open(os.path.join("files",filename)) as file:
            lines = file.readlines()
            lines = [line.rstrip() for line in lines]
        
        print(usergiven_question)
        newquizid = int(random.random()*1e8)
        createdsession = QuizCurrentDatabase.query.order_by(QuizCurrentDatabase.date_created.desc()).first()
        for each in lines:
            cq = QuizCreatedQuestions(sno=int(random.random()*1e5)  ,cquizid=newquizid, 
                userid=createdsession.currentuser , questions=each)
            db.session.add(cq)
            db.session.commit()
            time.sleep(0.5)
        return render_template('thanksyou.html',uploaded="true",createdquizid = newquizid)
    return render_template('upload.html')




if __name__ == '__main__':
    
    db.create_all()
    create_tsai_account()

    print(UserAccountDatabase.query.all())
    app.run(debug=True)
