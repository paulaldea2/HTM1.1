from flask import Flask, jsonify, request, redirect, session, render_template, make_response
from flask_restful import Api, Resource
import pymongo
import dns
import bcrypt
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.trainers import ListTrainer

app = Flask(__name__)
api = Api(app)

bot = ChatBot("Bright");
trainer = ListTrainer(bot)
trainer.train(['what is your name?', 'My name is Python-BOT'])
trainer.train(['who are you?', 'I am a BOT'])
trainer.train(['Happy', 'I’m always happy when you’re happy.'])
trainer.train(['Content', 'That’s good to hear!'])
trainer.train(['Angry', 'youtube'])
trainer.train(['Sad', 'youtube'])
trainer.train(['Surprised', 'What surprised you?'])
trainer.train(['Stressed', 'youtube'])
trainer = ChatterBotCorpusTrainer(bot)
trainer.train("chatterbot.corpus.english")


client = pymongo.MongoClient("mongodb+srv://root:root@cluster0.lt0oz.mongodb.net/Flask?retryWrites=true&w=majority")
db = client.test
users = db["Users"]

def UserExist(email):
    if users.find({"Email": email}).count() == 0:
        return False
    else:
        return True

def Verifypassmatch(password, passverif):
    if password == passverif:
        return False
    else:
        return True

def verifyPw(email, password):
    if not UserExist(email):
        return False

    hashed_pw = users.find({
        "Email":email
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def verifyCredentials(email, password):
    if not UserExist(email):
        return generateReturnDictionary(301, "Invalid Username"), True

    correct_pw = verifyPw(email, password)

    if not correct_pw:
        return generateReturnDictionary(302, "Incorrect Password"), True

    return None, False

def generateReturnDictionary(status, msg):
    retJson = {
        "status":status,
        "msg":msg
    }
    return retJson

class Register(Resource):
    def get(self):
        return make_response(render_template('auth/SignUp.html'))
    def post(self):

        #Get the posted data
        # postedData = request.form

        #user data
        fullname = request.form['fullname']
        email    = request.form['email']
        password = request.form['password']
        passverif= request.form['passwordverif']

        #Verify if the password match
        if Verifypassmatch(password, passverif):
            return jsonify(generateMessage(302, "Passwords don't match!"))
        
        #Verify if the user exist
        if UserExist(email):
            return jsonify(generateMessage(301, "This user exist!"))
        
        #Hashed the password
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        #Store the user detailes
        users.insert({
            "FullName": fullname,
            "Email": email,
            "Password": hashed_pw,
            "Admin": False
        })
        session['email'] = email
        
        #Return
        return make_response(render_template('index.html'))
        return jsonify(generateMessage(200, 'You signed in successfuly!'))

class Login(Resource):
    def get(self):
        return make_response(render_template('auth/SignIn.html'))
    def post(self):

        #Get the data

        #userdata
        email    = request.form['email']
        password = request.form['password']

        #Verify user data
        retJson, error = verifyCredentials(email, password)
        if error:
            return jsonify(retJson)
        
        session['email'] = email
        #Return
        return make_response(render_template('index.html'))
        return jsonify(generateMessage(200, 'You signed in successfuly!'))
        
class MainPage(Resource):
    def get(self):
        return make_response(render_template('index.html'))

class Aboutpage(Resource):
    def get(self):
        return make_response(render_template('about.html'))

class Choosepage(Resource):
    def get(self):
        return make_response(render_template('Choose.html'))


# class IndexPage(Resource):
#     def get(self):
#         if 'email' in session:
#             return jsonify(generateMessage(200, 'You signed in successfully as ' + session['email']))
#         else: 
#             return jsonify(generateMessage(301, 'You need to log in your account!'))

@app.route("/bot")
def index():    
    return render_template("boot.html") 

@app.route("/get")
def get_bot_response():    
    userText = request.args.get('msg')    
    return str(bot.get_response(userText)) 
    
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(MainPage, '/home')
api.add_resource(Aboutpage, '/about')
api.add_resource(Choosepage, '/choose')


if __name__ == "__main__":
    app.secret_key='mysecretkeytrytdecode'
    app.run(host='0.0.0.0')
