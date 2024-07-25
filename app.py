# app.py
from flask import Flask, render_template, request, jsonify, Response
import json
import pickle
from tensorflow.keras.models import load_model
import pymongo
import os
import gridfs
import tempfile
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
import base64

from modules.utils import correct_spelling
from modules.response_generator import generate_bot_response
from modules.db_operations import save_user_input, record_icon_feedback, record_feedback_with_user_details, get_feedback_file
from modules.email_sender import send_email
from modules.calculations import calculate_total_aggregate

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Connect to MongoDB Atlas using the environment variable
# MONGO_URI = os.getenv("MONGO_URI")
# client = pymongo.MongoClient(MONGO_URI)
# db = client["mydatabase"]
# feedback_collection = db["feedback"]
# user_input_collection = db["user_inputs"]
# icon_feedback_collection = db["icon_feedback"]

# connect to localhost mongodb
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
fs = gridfs.GridFS(db)
feedback_collection = db["feedback"]
user_input_collection = db["user_inputs"]
icon_feedback_collection = db["icon_feedback"]

# Load intents from multiple JSON files
intent_files = [
    'intents/intents.json', 'intents/instruction_prog_list.json', 'intents/cut_off.json',
    'intents/sciences_requirement.json', 'intents/humanities_social_sciences_requirement.json',
    'intents/health_science_requirement.json', 'intents/engineering_requirement.json',
    'intents/art_and_built_requirement.json', 'intents/agric_and_natural_resource_requirement.json',
    'intents/freshers_guide.json'
]

all_intents = {'intents': []}
for file_name in intent_files:
        with open(file_name, 'r', encoding='utf-8') as file:
            intents = json.load(file)
            all_intents['intents'].extend(intents['intents'])

# Load trained chatbot model and other necessary data
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
# model = load_model('chatbot_model.h5')
model = load_model('chatbot_functional_model.h5')


# Flask routes
@app.route("/")
def startup():
    return render_template("startup.html")

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/chatbotPop')
def chatbotPop():
    return render_template('pages/chatbotPop.html')

@app.route('/pages/feedback.html')
def feedback():
    return render_template('pages/feedback.html')

@app.route('/pages/aggregate.html')
def aggregate():
    return render_template('pages/aggregate.html')

@app.route('/programmeOptions')
def programme_options():
    return render_template('pages/programmeOptions.html')

@app.route('/calculateAggregate')
def calculateAggregate():
    return app.send_static_file('calculateAggregate.json')

@app.route('/pages/emailSent.html')
def emailSent():
    return render_template('pages/emailSent.html')

@app.route('/calculate-aggregate', methods=['POST'])
def calculate_aggregate():
    data = request.json
    compulsory_data = data.get('compulsory', {})
    optional_data = data.get('optional', {})

    total_aggregate = calculate_total_aggregate(compulsory_data, optional_data)

    return jsonify({'total_aggregate': total_aggregate})

@app.route("/get_response", methods=["POST"])
def get_response():
    user_message = request.json["message"].lower()
    corrected_message = correct_spelling(user_message)
    bot_response = generate_bot_response(user_message, model, words, classes, all_intents)
    return jsonify({"response": bot_response})

@app.route("/save_user_input", methods=["POST"])
def save_user_input_route():
    user_input = request.json.get("userInput")
    if user_input:
        result = save_user_input(user_input_collection, user_input)
        if result:
            return {"message": "User input saved successfully."}, 200
        else:
            return {"error": "Failed to save user input."}, 500
    else:
        return {"error": "User input not provided."}, 400

@app.route("/record_icon_feedback", methods=["POST"])
def record_icon_feedback_route():
    feedback_data = request.json
    if feedback_data:
        result = record_icon_feedback(icon_feedback_collection, feedback_data)
        if result:
            return {"message": "Feedback recorded successfully."}, 200
        else:
            return {"error": "Failed to record feedback."}, 500
    else:
        return {"error": "Feedback data not provided."}, 400

@app.route("/record_feedback_with_user_details", methods=["POST"])
def record_feedback_with_user_details_route():
    data = request.json
    result = record_feedback_with_user_details(feedback_collection, fs, data)
    if result:
        send_email(data.get("email"), data.get("firstName"))
        return jsonify({"message": "Feedback recorded successfully. Email sent"}), 200
    else:
        return jsonify({"error": "Failed to record feedback."}), 500


# Route for downloading feedback file from database
@app.route("/get_feedback_file/<feedback_id>", methods=["GET"])
def get_feedback_file_route(feedback_id):
    try:
        file_data, error = get_feedback_file(feedback_collection, fs, feedback_id)
        if error:
            return jsonify({"error": error}), 404

        # Create a temporary file to write the file data
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(file_data.read())
        temp_file.close()

        # Open the temporary file for reading
        with open(temp_file.name, 'rb') as f:
            file_content = f.read()

        # Set up response headers
        headers = {
            "Content-Disposition": f"attachment; filename={file_data.filename}"
        }

        # Return the file as a response
        return Response(file_content, headers=headers, content_type="application/octet-stream")
    except gridfs.NoFile:
        return jsonify({"error": "File not found in GridFS"}), 404
    except Exception as e:
        print("Exception:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000)
