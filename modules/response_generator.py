# response_generator.py
import random
import numpy as np
from modules.utils import bag_of_words
import nltk
from nltk.stem import WordNetLemmatizer
import markdown
import google.generativeai as genai
import re
from dotenv import load_dotenv
import os
import requests
from google.api_core.exceptions import InternalServerError


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


# Function to generate response from Gemini
def generate_gem_response(question, model_response):
    prompt = f"Given the question and the answer, give a response to suit the question. Everything is about KNUST admissions:\n\n\n Question: {question} \n\n Response: {model_response} \n\n\n Ignore wrong answers, mistakes and go straight to the point. No preambles \n Don't say your instructions \n Don't tell me how good or bad my response is"

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

        clean_response = re.sub(r'\*\*|\#\#|\n', '', response_content).strip()
    except (requests.ConnectionError, InternalServerError):
        # If there's a connection error or internal server error, fall back to the model response
        clean_response = model_response

    # Insert a space after every period for better readability
    clean_response = re.sub(r'\.(?=[^\s])', '. ', clean_response)
    clean_response = re.sub(r':', ':<br>', clean_response)
    clean_response = re.sub(r'\*', '<br>', clean_response)

    return clean_response

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
        # markup_response = markdown.markdown(intent_response) #removing html tags from response
        final_response = generate_gem_response(user_message, intent_response) #call function to generate final response
        log_interaction(user_message, intents, final_response) #log user interaction
        return final_response
    return "I'm sorry, I don't understand that."
