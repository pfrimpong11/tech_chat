import random
import json
import pickle
import numpy as np

import nltk
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import SGD

# nltk.download('punkt')
# nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

# Load all intents from multiple JSON files
intent_files = [
    'intents.json', 'instruction_prog_list.json', 'cut_off.json', 'sciences_requirement.json',
    'humanities_social_sciences_requirement.json', 'health_science_requirement.json', 
    'engineering_requirement.json', 'art_and_built_requirement.json', 
    'agric_and_natural_resource_requirement.json', 'freshers_guide.json'
]

all_intents = {'intents': []}
for file_name in intent_files:
    with open(file_name, 'r', encoding='utf-8') as file:
        intents = json.load(file)
        all_intents['intents'].extend(intents['intents'])
words = []
classes = []
documents = []
ignore_letters = ['?', '!', '.', ',']

for intent in all_intents['intents']:
    for pattern in intent['patterns']:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

words = [lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore_letters]
words = sorted(set(words))

classes = sorted(set(classes))

pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

training = []
output_empty = [0] * len(classes)

for document in documents:
    bag = []
    word_patterns = document[0]
    word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0)

    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    training.append([bag, output_row])

random.shuffle(training)

# Split the training data into features (train_x) and labels (train_y)
train_x = []
train_y = []

for features, label in training:
    train_x.append(features)
    train_y.append(label)

train_x = np.array(train_x)
train_y = np.array(train_y)

model = Sequential()
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(classes), activation='softmax'))

sgd = SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

model.fit(train_x, train_y, epochs=100, batch_size=5, verbose=1)
model.save('chatbot_model.h5')  # Model saved
print("Done")
