from flask import Flask,request

app = Flask(__name__)

@app.route('/v1/user/<name>')
def index():
    return "hello %" % userid

@app.route('/admin',methods=['POST','GET'])
def checkDate():
    return 'From Date is'+request.args.get('from_date')+ ' To Date is '+ request.args.get('to_date')


if __name__=="__main__":
    app.run(port=5000,debug=True)