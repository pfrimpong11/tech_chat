import random
import json
import pickle
import numpy as np
import matplotlib.pyplot as plt

import nltk
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import SGD
from sklearn.model_selection import train_test_split

# nltk.download('punkt')
# nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

# Load all intents from multiple JSON files
intent_files = [
    'intents/intents.json', 'intents/instruction_prog_list.json', 'intents/cut_off.json',
    'intents/sciences_requirement.json', 'intents/humanities_social_sciences_requirement.json',
    'intents/health_science_requirement.json', 'intents/engineering_requirement.json',
    'intents/art_and_built_requirement.json', 'intents/agric_and_natural_resource_requirement.json',
    'intents/freshers_guide.json', 'intents/shs_programmes'
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

# Split the data into training and validation sets
train_x, val_x, train_y, val_y = train_test_split(train_x, train_y, test_size=0.2, random_state=42)

# Define the model
model = Sequential()
model.add(Dense(128, activation='relu', input_shape=(len(train_x[0]),)))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))  # Adding an extra dense layer
model.add(Dense(len(classes), activation='softmax'))

# Experiment with different learning rates and momentum values
learning_rate = 0.001
momentum = 0.9
sgd = SGD(learning_rate=learning_rate, momentum=momentum, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

# Train the model
history = model.fit(train_x, train_y, validation_data=(val_x, val_y), epochs=100, batch_size=5, verbose=1)

# Evaluate the model
loss, accuracy = model.evaluate(val_x, val_y)
print("Validation Loss:", loss)
print("Validation Accuracy:", accuracy)

model.save('chatbot_model.h5')  # Model saved
print("Done")

# Print the model summary
model.summary()

# Plot the accuracy and loss
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(loc='upper left')

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(loc='upper left')

plt.tight_layout()
plt.show()
