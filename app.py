import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from flask import Flask, render_template, request, jsonify, send_file, Response
from spellchecker import SpellChecker
import pymongo
import os
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
import base64
import gridfs
from bson import ObjectId
import io
import tempfile


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


# Function to send email
def send_email(receiver_email, user_name):
    smtp_server = 'smtp-mail.outlook.com'
    port = 587  # For starttls
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_name = "TechChat Team"
    password = os.environ.get("SENDER_PASSWORD")

    if not sender_email or not password:
        print("Error: Environment variables for email are not set properly.")
        return

    # Render the HTML template for the email
    email_html = render_template('email_templates/feedback_email.html', user_name=user_name)

    message = MIMEMultipart()
    message["From"] = f"{sender_name} <{sender_email}>"
    message["To"] = receiver_email
    message["Subject"] = "Thank you for your feedback"


    message.attach(MIMEText(email_html, "html"))

    try:
        smtp = smtplib.SMTP(smtp_server, port)
        smtp.ehlo()
        smtp.starttls(context=ssl.create_default_context())
        smtp.ehlo()
        smtp.login(sender_email, password)
        smtp.sendmail(sender_email, receiver_email, message.as_string())
        smtp.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error: {e}")

# Load trained chatbot model and other necessary data
lemmatizer = WordNetLemmatizer()
spell = SpellChecker()

# Load intents from multiple JSON files
intent_files = [
    'intents.json', 'instruction_prog_list.json', 'cut_off.json',
    'sciences_requirement.json', 'humanities_social_sciences_requirement.json',
    'health_science_requirement.json', 'engineering_requirement.json',
    'art_and_built_requirement.json', 'agric_and_natural_resource_requirement.json',
    'freshers_guide.json'
]

intents = {'intents': []}
for file in intent_files:
    with open(file, 'r', encoding='utf-8') as f:
        intents['intents'].extend(json.load(f)['intents'])

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbot_model.h5')

# Flask routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/pages/feedback.html')
def feedback():
    return render_template('pages/feedback.html')


@app.route("/get_response", methods=["POST"])
def get_response():
    user_message = request.json["message"].lower()
    corrected_message = correct_spelling(user_message)
    bot_response = generate_bot_response(corrected_message)
    return jsonify({"response": bot_response})

@app.route("/save_user_input", methods=["POST"])
def save_user_input():
    user_input = request.json.get("userInput")
    if user_input:
        # Prepare the document to insert into MongoDB
        input_doc = {
            "user_input": user_input,
            "timestamp": datetime.now()
        }
        
        # Insert the document into the collection
        result = user_input_collection.insert_one(input_doc)
        
        if result.inserted_id:
            return {"message": "User input saved successfully."}, 200
        else:
            return {"error": "Failed to save user input."}, 500
    else:
        return {"error": "User input not provided."}, 400


@app.route("/record_icon_feedback", methods=["POST"])
def record_icon_feedback():
    feedback_data = request.json
    if feedback_data:
        # Prepare the document to insert into MongoDB
        feedback_doc = {
            "user_message": feedback_data.get("userMessage"),
            "bot_response": feedback_data.get("botResponse"),
            "is_helpful": feedback_data.get("isHelpful"),
            "timestamp": datetime.now()
        }
        
        # Insert the document into the collection
        result = icon_feedback_collection.insert_one(feedback_doc)
        
        if result.inserted_id:
            return {"message": "Feedback recorded successfully."}, 200
        else:
            return {"error": "Failed to record feedback."}, 500
    else:
        return {"error": "Feedback data not provided."}, 400

@app.route("/record_feedback_with_user_details", methods=["POST"])
def record_feedback_with_user_details():
    data = request.json
    first_name = data.get("firstName")
    last_name = data.get("lastName")
    email = data.get("email")
    feedback = data.get("feedback")
    file = data.get("file")
    file_name = data.get("fileName")


    # Store file in GridFS
    if file:
        file_id = fs.put(base64.b64decode(file), filename=file_name)
    else:
        file_id = None

    feedback_doc = {
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "feedback": feedback,
        "file_id": file_id
    }

    # feedback_doc = {
    #     "firstName": first_name,
    #     "lastName": last_name,
    #     "email": email,
    #     "feedback": feedback
    # }

    # If a file was uploaded, decode it and store it in the document
    # if file:
    #     file_data = base64.b64decode(file)
    #     feedback_doc["file"] = file_data
    #     feedback_doc["fileName"] = file_name

    result = feedback_collection.insert_one(feedback_doc)

    if result.inserted_id:
        send_email(email, first_name)
        return jsonify({"message": "Feedback recorded successfully. Email sent"}), 200
    else:
        return jsonify({"error": "Failed to record feedback."}), 500


@app.route("/get_feedback_file/<feedback_id>", methods=["GET"])
def get_feedback_file(feedback_id):
    try:
        feedback_object_id = ObjectId(feedback_id)
        feedback = feedback_collection.find_one({"_id": feedback_object_id})

        if not feedback:
            return jsonify({"error": "Feedback not found"}), 404
        if 'file_id' not in feedback or feedback['file_id'] is None:
            return jsonify({"error": "File not found in feedback"}), 404
        
        file_id = feedback['file_id']
        file_data = fs.get(ObjectId(file_id))

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





# Helper functions
def correct_spelling(sentence):
    words = nltk.word_tokenize(sentence)
    corrected_words = [spell.correction(word) for word in words]
    corrected_sentence = ' '.join(corrected_words)
    return corrected_sentence

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]), verbose=0)[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

def get_response_from_intent(intent_tag):
    for intent in intents['intents']:
        if intent['tag'] == intent_tag:
            return random.choice(intent['responses'])
    return "I'm sorry, I don't understand that."

def generate_bot_response(user_message):
    intents_list = predict_class(user_message)
    if intents_list:
        for intent in intents_list:
            intent_tag = intent['intent']
            return get_response_from_intent(intent_tag)
    return "I'm sorry, I don't understand that."

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000)