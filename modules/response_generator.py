# response_generator.py
import random
import numpy as np
from modules.utils import bag_of_words


def log_interaction(user_input, predicted_intents, response):
    with open('chatbot_interactions.txt', 'a', encoding='utf-8') as f:
        f.write(f"User: {user_input}\n")
        f.write("Predicted Intents:\n")
        for intent in predicted_intents:
            f.write(f"- {intent['intent']}: {intent['probability']}\n")
        f.write(f"Bot: {response}\n\n")

def predict_class(sentence, model, words, classes):
    bow = bag_of_words(sentence, words)
    res = model.predict(np.array([bow]), verbose=0)[0]
    ERROR_THRESHOLD = 0.09  # Probability threshold
    results = [{"intent": classes[i], "probability": str(res[i])} for i in range(len(classes)) if res[i] > ERROR_THRESHOLD]
    results.sort(key=lambda x: float(x['probability']), reverse=True)
    return results[:10]  # Return only the first 10 predicted tags

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
