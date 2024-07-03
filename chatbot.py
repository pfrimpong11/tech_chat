import random
import json
import pickle
import numpy as np
import logging

import nltk
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import load_model

# Set up logging
logging.basicConfig(filename='chatbot.log', level=logging.INFO)

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Load intents from multiple JSON files
intent_files = [
    'intents/intents.json', 'intents/instruction_prog_list.json', 'intents/cut_off.json',
    'intents/sciences_requirement.json', 'intents/humanities_social_sciences_requirement.json',
    'intents/health_science_requirement.json', 'intents/engineering_requirement.json',
    'intents/art_and_built_requirement.json', 'intents/agric_and_natural_resource_requirement.json',
    'intents/freshers_guide.json'
]

all_intents = {'intents': []}

try:
    for file_name in intent_files:
        with open(file_name, 'r', encoding='utf-8') as file:
            intents = json.load(file)
            all_intents['intents'].extend(intents['intents'])

    words = pickle.load(open('words.pkl', 'rb'))
    classes = pickle.load(open('classes.pkl', 'rb'))
    # model = load_model('chatbot_model.h5')
    model = load_model('chatbot_functional_model.h5')


except FileNotFoundError as e:
    print(f"Error: {e}")
    exit()

except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit()

def clean_up_sentence(sentence):
    sentence = sentence.lower()  # Convert the sentence to lowercase
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
    ERROR_THRESHOLD = 0.09  # Probability threshold
    results = [{"intent": classes[i], "probability": str(res[i])} for i in range(len(classes)) if res[i] > ERROR_THRESHOLD]
    results.sort(key=lambda x: float(x['probability']), reverse=True)
    return results[:10]  # Return only the first 10 predicted tags

def get_response(intents_list, all_intents):
    for intent in intents_list:
        tag = intent['intent']
        for intent_data in all_intents['intents']:
            if intent_data['tag'] == tag:
                print(f"Using tag: {tag}")  # Print the tag used to generate the response
                return random.choice(intent_data['responses'])
    return "I'm sorry, I don't have a response for that."

def log_interaction(user_input, predicted_intents, response):
    logging.info(f"User: {user_input}")
    logging.info(f"Predicted Intents: {predicted_intents}")
    logging.info(f"Bot: {response}")

    # Write to text file
    with open('chatbot_interactions.txt', 'a', encoding='utf-8') as f:
        f.write(f"User: {user_input}\n")
        f.write("Predicted Intents:\n")
        for intent in predicted_intents:
            f.write(f"- {intent['intent']}: {intent['probability']}\n")
        f.write(f"Bot: {response}\n\n")

print("GO! BOT IS RUNNING (type 'exit' to stop)")

while True:
    message = input("You: ").lower()  # Convert the user input to lowercase
    if message == 'exit':
        print("Bot: Goodbye!")
        break
    intents = predict_class(message)
    print("Predicted Tags:")
    for intent in intents:
        print(f"- {intent['intent']}: {intent['probability']}")
    
    response = get_response(intents, all_intents)
    print("Bot:", response)
    
    log_interaction(message, intents, response)
