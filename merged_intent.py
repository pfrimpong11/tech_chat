import json
import os

# Function to load a single JSON file
def load_json_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

# List of file paths to your JSON files
filepaths = [
    'intents/intents.json', 'intents/instruction_prog_list.json', 'intents/cut_off.json',
    'intents/sciences_requirement.json', 'intents/humanities_social_sciences_requirement.json',
    'intents/health_science_requirement.json', 'intents/engineering_requirement.json',
    'intents/art_and_built_requirement.json', 'intents/agric_and_natural_resource_requirement.json',
    'intents/freshers_guide.json'
]  # Add as many file paths as needed

# Initialize a list to store the contents of each JSON file
intents = []

# Loop through each file path, load the JSON data, and append it to the list
for filepath in filepaths:
    intents.append(load_json_file(filepath))

# If you want to merge them into a single dictionary (assuming the JSON files contain dictionaries)
merged_intents = {}
for intent in intents:
    merged_intents.update(intent)

# Now 'merged_intents' contains the combined data from all JSON files
print(merged_intents)
