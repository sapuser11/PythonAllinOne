##1. Import flask framework
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

##Import our class from app.py
from app import issue_reporting_app

##Initialize a new app using flask
app = Flask(__name__)
CORS(app)


def get_text_from_request():
    request_data = request.get_json()
    #print(request_data)
    return request_data

@app.route('/', methods=['GET'])
def root():
    return 'Welcome to Citizen Reporting App: Health Check Successfull.', 200

@app.route('/genaihub-api/processPost', methods=['POST'])
def do_analysis():
    input_message = get_text_from_request()
    #print(input_message)
    sequence = issue_reporting_app(input_message)

    analysis_result = sequence.run_workflow()
    #print(analysis_result)
    
    try:
        return analysis_result, 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/testdb', methods=['GET'])
def test():
    sequence = issue_reporting_app("dummy")
    output = sequence.hello()
    return output

def create_app():
    return app

if __name__ == '__main__':
    app.run('0.0.0.0', 8080)