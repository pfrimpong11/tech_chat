# db_operations.py
from datetime import datetime
import base64
import gridfs
from bson import ObjectId

def save_user_input(user_input_collection, user_input):
    input_doc = {
        "user_input": user_input,
        "timestamp": datetime.now()
    }
    result = user_input_collection.insert_one(input_doc)
    return result.inserted_id

def record_icon_feedback(icon_feedback_collection, feedback_data):
    feedback_doc = {
        "user_message": feedback_data.get("userMessage"),
        "bot_response": feedback_data.get("botResponse"),
        "is_helpful": feedback_data.get("isHelpful"),
        "timestamp": datetime.now()
    }
    result = icon_feedback_collection.insert_one(feedback_doc)
    return result.inserted_id

def record_feedback_with_user_details(feedback_collection, fs, data):
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

    result = feedback_collection.insert_one(feedback_doc)
    return result.inserted_id

def get_feedback_file(feedback_collection, fs, feedback_id):
    feedback_object_id = ObjectId(feedback_id)
    feedback = feedback_collection.find_one({"_id": feedback_object_id})

    if not feedback:
        return None, "Feedback not found"
    if 'file_id' not in feedback or feedback['file_id'] is None:
        return None, "File not found in feedback"

    file_id = feedback['file_id']
    file_data = fs.get(ObjectId(file_id))
    return file_data, None
