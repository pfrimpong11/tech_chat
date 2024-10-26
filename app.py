# app.py
from flask import Flask, render_template, request, jsonify, Response, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
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
import nltk
import datetime
from datetime import timedelta
from flask_session import Session

from modules.utils import correct_spelling, check_internet
from modules.response_generator import generate_bot_response
from modules.db_operations import save_user_input, record_icon_feedback, record_feedback_with_user_details, get_feedback_file
from modules.email_sender import send_email, forgot_password_email
from modules.calculations import calculate_total_aggregate

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt_tab')

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'  # You can also use 'redis' or 'sqlalchemy' for DB-based sessions
app.config['SESSION_PERMANENT'] = False  # Sessions will last until the browser closes
app.config['SESSION_USE_SIGNER'] = True  # Encrypt session cookies
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")  # Required for signing the session
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

Session(app)

# Connect to MongoDB Atlas using the environment variable
MONGO_URI = os.getenv("MONGO_URI")
client = pymongo.MongoClient(MONGO_URI)
db = client.TechChat
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
    'intents/freshers_guide.json', 'intents/shs_programmes.json', 'intents/bot_interaction.json'
]

all_intents = {'intents': []}
for file_name in intent_files:
        with open(file_name, 'r', encoding='utf-8') as file:
            intents = json.load(file)
            all_intents['intents'].extend(intents['intents'])

# Load trained chatbot model and other necessary data
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbot_functional_model.h5')


# Flask routes
@app.route("/")
def startup():
    return render_template("startup.html")

@app.route('/index')
def index():
    return render_template('new-index.html')

@app.route('/chat')
def indexChat():
    if 'user_id' not in session:
        flash('Please log in.', 'danger')
        return redirect(url_for('login'))
    return render_template('new-index-login.html')

@app.route('/chat-history')
def chatHistory():
    return render_template('pages/chat-history.html')

@app.route('/knustPortal')
def knustPortal():
    return render_template('pages/knustPortal.html')

@app.route('/feedback')
def feedback():
    return render_template('pages/feedback.html')

@app.route('/aggregate')
def aggregate():
    return render_template('pages/aggregate.html')

@app.route('/programmeOptions')
def programme_options():
    return render_template('pages/programmeOptions.html')

@app.route('/calculateAggregate')
def calculateAggregate():
    return app.send_static_file('calculateAggregate.json')

@app.route('/emailSent')
def emailSent():
    return render_template('pages/emailSent.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        # Check if the email is already registered
        existing_user = db.users.find_one({'email': email})
        
        if existing_user:
            return jsonify({
                'status': 'error',
                'message': 'Email is already registered'
            }), 409

        if len(password) < 8:
            return jsonify({
                'status': 'error',
                'message': 'Password must be at least 8 characters long'
            }), 401
        
        hashed_password = generate_password_hash(password)
        
        # Save new user to the database
        db.users.insert_one({
            'name': name,
            'email': email,
            'password': hashed_password
        })
        
        return jsonify({
                'status': 'success',
                'message': 'Registration successful!'
            }), 200
    
    return render_template('pages/register.html')

# login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        # Find the user in the database
        user = db.users.find_one({'email': email})
        
        if user and check_password_hash(user['password'], password):
            # Store user_id and email in session
            session['user_id'] = str(user['_id'])  # Convert ObjectId to string for session
            session['user_email'] = user['email']
            
            # Return the user_id to the frontend
            return jsonify({
                'status': 'success',
                'user_id': str(user['_id']),
                'message': 'Logged in successfully!'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid email or password'
            }), 401

    return render_template('pages/login.html')


# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('startup'))

# Forgot password route
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        # Check if user exists
        user = db.users.find_one({'email': email})
        if user:
            # Generate a token
            token = str(ObjectId())
            db.password_resets.insert_one({'email': email, 'token': token})
            
            # Create password reset URL
            reset_url = url_for('reset_password', token=token, _external=True)
            
            # Send the password reset email
            forgot_password_email(email, reset_url)
            
            return jsonify({'status': 'success', 'message': 'Password reset link sent to your email'})
        else:
            return jsonify({'status': 'error', 'message': 'Email not found!'})
    
    return render_template('pages/forgot_password.html')

# Reset password route
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Check if token exists in the database
    reset_record = db.password_resets.find_one({'token': token})
    
    if not reset_record:
        return jsonify({'status': 'error', 'message': 'Invalid or expired token'})


    if request.method == 'POST':
        new_password = request.form['password']
        # confirm_password = request.form['confirm_password']

        if len(new_password) < 8 :
            return jsonify({'status': 'error', 'message': 'Password must be at least 8 characters long'})
        
        # if new_password != confirm_password:
        #     return jsonify({'status': 'error', 'message': 'Passwords do not match'})
        
        # Hash the new password
        hashed_password = generate_password_hash(new_password)

        # Update the user's password in the database
        db.users.update_one(
            {'email': reset_record['email']},
            {'$set': {'password': hashed_password}}
        )
        
        # Remove the password reset token after successful reset
        db.password_resets.delete_one({'token': token})
        
        return jsonify({'status': 'success', 'message': 'Password has been reset successfully'})
    
    return render_template('pages/reset_password.html', token=token)


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
    if check_internet(): # function to check internet connection
        # Proceed with input processing
        print("User connected to the internet")
        bot_response = generate_bot_response(user_message, model, words, classes, all_intents)

        chat_data = {
            'messages': [{
                'user': user_message,
                'TechChat': bot_response,
            }],
            'timestamp': datetime.datetime.now(datetime.timezone.utc)
        }
        db.chats.insert_one(chat_data)   # save chat in database

        return jsonify({"response": bot_response})
    else:
        # Handle no connection scenario
        print("No internet connection. Please check your connection.")
        bot_response = "Please check your internet connection."
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



@app.route('/start-chat', methods=['POST'])
def start_chat():
    data = request.json
    user_id = session.get('user_id')  # Assuming the user is logged in

    if not user_id:
        return jsonify({'error': 'User not authenticated'}), 401

    # Create a new chat session with the first user message as the session name
    message = data['message'] # Use the first message as the session name
    session_name = correct_spelling(message)
    chat_session = {
        'user_id': ObjectId(user_id),
        'session_name': session_name,
        'messages': [{
            'message': data['message'],
            'sender': 'user',
            'timestamp': datetime.datetime.now(datetime.timezone.utc)
        }],
        'created_at': datetime.datetime.now(datetime.timezone.utc)
    }

    # Insert the new chat session into the database
    session_id = db.chat_sessions.insert_one(chat_session).inserted_id

    return jsonify({'status': 'Chat session started', 'session_id': str(session_id)}), 200



@app.route('/add-message/<session_id>', methods=['POST'])
def add_message(session_id):
    data = request.json
    user_id = session.get('user_id')  # Ensure user is logged in

    if not user_id:
        return jsonify({'error': 'User not authenticated'}), 401

    # Add message to the existing session
    new_message = {
        'message': data['message'],
        'sender': data['sender'],  # 'user' or 'bot'
        'timestamp': datetime.datetime.utcnow()
    }

    db.chat_sessions.update_one(
        {'_id': ObjectId(session_id), 'user_id': ObjectId(user_id)},
        {'$push': {'messages': new_message}}
    )

    return jsonify({'status': 'Message added to chat session'}), 200


# route to fetch all the chat history
@app.route('/get-chat-sessions', methods=['GET'])
def get_chat_sessions():
    user_id = request.args.get('user_id')  # Get user_id from query parameters

    if not user_id:
        return jsonify({'error': 'User not authenticated'}), 401

    # Retrieve all chat sessions for the user
    sessions = list(db.chat_sessions.find({'user_id': ObjectId(user_id)}).sort('created_at', -1))

    session_list = []
    for session in sessions:
        session_list.append({
            'session_id': str(session['_id']),
            'session_name': session['session_name'],
            'created_at': session['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify({'chat_sessions': session_list}), 200


# route to get messages from a chat session
@app.route('/get-session-messages/<session_id>', methods=['POST'])
def get_session_messages(session_id):
    data = request.json
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'User not authenticated'}), 401

    # Retrieve the messages for the selected session
    session = db.chat_sessions.find_one({'_id': ObjectId(session_id), 'user_id': ObjectId(user_id)})

    if not session:
        return jsonify({'error': 'Chat session not found'}), 404

    messages = session['messages']
    message_list = []
    for message in messages:
        message_list.append({
            'message': message['message'],
            'sender': message['sender'],
            'timestamp': message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify({'messages': message_list}), 200


# Route to delete chat history
@app.route('/delete-chat-session/<session_id>', methods=['DELETE'])
def delete_chat_session(session_id):
    user_id = request.args.get('user_id')  # Get user_id from query parameters

    if not user_id:
        return jsonify({'error': 'User not authenticated'}), 401

    # Check if the session belongs to the user
    chat_session = db.chat_sessions.find_one({'_id': ObjectId(session_id), 'user_id': ObjectId(user_id)})

    if not chat_session:
        return jsonify({'error': 'Chat session not found or not authorized'}), 404

    # Delete the session
    db.chat_sessions.delete_one({'_id': ObjectId(session_id), 'user_id': ObjectId(user_id)})

    return jsonify({'status': 'Chat session deleted successfully'}), 200



if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)
