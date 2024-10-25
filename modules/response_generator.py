# response_generator.py
import random
import numpy as np
from modules.utils import bag_of_words
from modules.retrain_intents import update_intent
import nltk
from nltk.stem import WordNetLemmatizer
import markdown
import google.generativeai as genai
import re
from dotenv import load_dotenv
import os
import requests
from google.api_core.exceptions import InternalServerError


nltk.download('punkt_tab')
nltk.download('wordnet')



load_dotenv()

# Set your Gemini API key
api_key = os.getenv('API_KEY')

genai.configure(api_key=api_key)


# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()


def log_interaction(user_input, predicted_intents, response):
    with open('chatbot_interactions.txt', 'a', encoding='utf-8') as f:
        f.write(f"User: {user_input}\n")
        f.write("Predicted Intents:\n")
        for intent in predicted_intents:
            f.write(f"- {intent['intent']}: {intent['probability']}\n")
        f.write(f"Bot: {response}\n\n")


    # update the json for model retrain
    tag = tag = predicted_intents[0]['intent']
    pattern = []
    bot_response = []

    pattern.append(user_input)
    bot_response.append(response)

    update_intent(tag, pattern, bot_response)


# Function to generate response from Gemini
def generate_gem_response(question, predicted_intent, model_response):
    prompt = f"""
    Hey! Act as a highly professional admissions counselor or admissions advisor at Kwame Nkrumah University of Science and Technology.
    Your name will be TechChat.
    First if all I will try and predict the user's questions and provide a response to it. 
    Your job is to analyse the the question, the predicted intent and response. Whether the response suits the question. 
    If the response suits the question, write it well for the user, if not, provide the most suitable response.

    No preambles i.e telling them how their provided response sounds. Provide only the suitable response for the applicant.

    Everything is about KNUST admission.
    
    Question: {question}
    Predicted Intent: {predicted_intent}
    Response: {model_response}
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)

        # Extracting the text from the response
        response_content = ""
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    response_content += part.text

        # Clean and format the response content
        clean_response = format_response(response_content)
    except (requests.ConnectionError, InternalServerError):
        # Fall back to the model response in case of an error
        clean_response = model_response

    return clean_response


def format_response(response_content):
    if '|' in response_content:  # Checking for table structure
        response_content = format_table(response_content)
    
    response_content = re.sub(r'\n', ' <br>', response_content)
    
    # Format URLs and email addresses properly (basic regex for example purposes)
    response_content = re.sub(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', r'<a href="mailto:\1">\1</a>', response_content)  # Email links
    response_content = re.sub(r'(https?://[^\s]+)', r'<a href="\1">\1</a>', response_content)  # URL links
    response_content = re.sub(r'\b(www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}[^\s]*)', r'<a href="http://\1">\1</a>', response_content) #url starting www
    
    # Remove any unwanted markdown symbols (**, ##)
    clean_response = re.sub(r'\*\*|\#\#|\_', '', response_content).strip()

    return clean_response


def format_table(response_content):
    # Split the content into rows
    rows = response_content.split('\n')
    
    # Start building the HTML table
    table_html = '<table border="1" cellpadding="5" cellspacing="0">'
    
    for row in rows:
        if '|' in row:  # Only format rows that appear to have table columns
            # Split the row by '|' to get individual cells
            cells = row.split('|')
            # Clean up whitespace from each cell
            cells = [cell.strip() for cell in cells if cell.strip()]
            
            if cells:
                table_html += '<tr>'
                for cell in cells:
                    table_html += f'<td>{cell}</td>'
                table_html += '</tr>'
    
    table_html += '</table>'
    
    return table_html




def clean_up_sentence(sentence):
    sentence = sentence.lower()  # Convert the sentence to lowercase
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence, words):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence, model, words, classes):
    bow = bag_of_words(sentence, words)
    res = model.predict(np.array([bow]), verbose=0)[0]
    ERROR_THRESHOLD = 0.25  # Probability threshold
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list[:10] # Return only the first 10 predicted tags

def get_response_from_intent(intents_list, all_intents):
    for intent in intents_list:
        tag = intent['intent']
        for intent_data in all_intents['intents']:
            if intent_data['tag'] == tag:
                print(f"Using tag: {tag}")  # Print the tag used to generate the response
                return random.choice(intent_data['responses'])
    return "I'm sorry, I don't have a response for that."

def generate_bot_response(user_message, model, words, classes, all_intents):
    intents = predict_class(user_message, model, words, classes)
    print("Predicted Tags:")
    for intent in intents:
        print(f"- {intent['intent']}: {intent['probability']}")
        intent_response = get_response_from_intent(intents, all_intents)
        final_response = generate_gem_response(user_message, intents[0], intent_response) #call function to generate final response
        log_interaction(user_message, intents, final_response) #log user interaction
        return final_response
    return "I'm sorry, I don't understand that."
