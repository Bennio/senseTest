from flask import Flask,request

app = Flask(__name__)

@app.route('/v1/user/<userid>')
def index(userid):

    return ' "user_id ":' + userid + '"app": "Airbnb","timestamp": "2018-10-29T00:30:12.984Z" '

@app.route('/v1/app',methods=['POST','GET'])
def information():

	return 'user_id:'+request.args.get('user_id')+ ' app :'+ request.args.get('app')+' timestamp :' + request.args.get('timestamp')



if __name__=="__main__":
    app.run(port=5000,debug=True)