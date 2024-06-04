# utils.py
import nltk
from nltk.stem import WordNetLemmatizer
from spellchecker import SpellChecker
import numpy as np
import random
import json

lemmatizer = WordNetLemmatizer()
spell = SpellChecker()

# Load custom words from JSON file and add to spellchecker
with open('custom_words.json', 'r', encoding='utf-8') as file:
    custom_words_data = json.load(file)
    custom_words = custom_words_data.get("words", [])
    spell.word_frequency.load_words(custom_words)

def correct_spelling(sentence):
    words = nltk.word_tokenize(sentence)
    corrected_words = [spell.correction(word) for word in words]
    corrected_sentence = ' '.join(filter(None, corrected_words))
    print(f"Original: {sentence}")
    print(f"Corrected: {corrected_sentence}")
    return corrected_sentence

def clean_up_sentence(sentence):
    sentence = sentence.lower()
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
