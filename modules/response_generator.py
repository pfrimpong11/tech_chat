# response_generator.py
import random
import numpy as np
from modules.utils import bag_of_words
import nltk
from nltk.stem import WordNetLemmatizer

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()


def log_interaction(user_input, predicted_intents, response):
    with open('chatbot_interactions.txt', 'a', encoding='utf-8') as f:
        f.write(f"User: {user_input}\n")
        f.write("Predicted Intents:\n")
        for intent in predicted_intents:
            f.write(f"- {intent['intent']}: {intent['probability']}\n")
        f.write(f"Bot: {response}\n\n")

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
        response = get_response_from_intent(intents, all_intents)
        log_interaction(user_message, intents, response) #log user interaction
        return response
    return "I'm sorry, I don't understand that."
