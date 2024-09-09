import json
import os

def update_intent(tag, patterns, responses, file_path='intents/bot_interaction.json'):
    # Check if the file exists
    if os.path.exists(file_path):
        try:
            # Open the file and load the existing data
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
        except json.JSONDecodeError:
            # If the file is empty or contains invalid JSON, initialize with empty intents
            print(f"Warning: {file_path} is empty or invalid, initializing with empty intents.")
            data = {"intents": []}
    else:
        # If the file does not exist, create an empty structure
        data = {"intents": []}

    # Continue with the rest of your logic for updating intents...
    tag_found = False

    for intent in data["intents"]:
        if intent["tag"] == tag:
            intent["patterns"].extend(patterns)
            intent["responses"].extend(responses)
            intent["patterns"] = list(set(intent["patterns"]))  # Remove duplicates
            intent["responses"] = list(set(intent["responses"]))
            tag_found = True
            break

    if not tag_found:
        new_intent = {"tag": tag, "patterns": patterns, "responses": responses}
        data["intents"].append(new_intent)

    # Write the updated data back to the JSON file
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Intent with tag '{tag}' updated successfully in {file_path}")
