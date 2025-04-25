import json
import subprocess
import os
import time

# Load data from data.json
with open('data.json', 'r') as file:
    data = json.load(file)
    FIELD_NAMES = data["FieldNames"]
    FIELDS = data["Fields"]

# print(json.dumps(FIELD_NAMES, indent=2))

try:
    subprocess.run(['sudo', 'systemctl', 'stop', 'ollama'], check=True)
except subprocess.CalledProcessError:
    pass  # Ignore the error if the service is not running

# Ensure any existing 'ollama' processes are killed
try:
    subprocess.run(['killall', 'ollama'], check=True)
except subprocess.CalledProcessError:
    pass  # Ignore the error if no 'ollama' process is found

# Check if the port is in use and kill the process using it
try:
    result = subprocess.run(['lsof', '-i', ':11434'], capture_output=True, text=True)
    if result.stdout:
        pid = result.stdout.split('\n')[1].split()[1]
        os.kill(int(pid), 9)
        time.sleep(2)  # Give some time for the process to be killed
except Exception as e:
    print(f"Error checking/killing process on port 11434: {e}")

# Start the 'ollama' service
try:
    ollama_process = subprocess.Popen(['ollama', 'serve'])
except Exception as e:
    print(f"Error starting 'ollama' service: {e}")
    ollama_process = None

# Add a delay to give the service time to start
time.sleep(10)

def getResponseStep1(user_query):
    CONTEXT = f"""
    Your job is to analyze the user's query against the provided field names and return JSON indicating which fields are most relevant.

    INSTRUCTIONS:
    1. Examine the user query carefully.
    2. Compare against these field names: {json.dumps(FIELD_NAMES, indent=2)}
    3. Return JSON with field numbers as keys and relevance scores (0-10) as values.

    RESPONSE FORMAT:
    {{
    "matches": [
        {{ "field_number": n, "relevance": 8, "reason": "This field directly addresses the user's query about X" }},
        {{ "field_number": m, "relevance": 5, "reason": "This field partially addresses the query through Y" }}
    ],
    "no_matches": false
    }}
 
    If no matches are found, return:
    {{
    "matches": [],
    "no_matches": true,
    "explanation": "No relevant fields were found because..."
    }}

    USER QUERY: {user_query}
    """

    JSON_PAYLOAD = json.dumps({
        "model": "mistral-nemo",
        "prompt": CONTEXT,
        "options": {
            "temperature": 1,
            "top_p": 1,
            "top_k": 0,
            "seed": 0
        }
    })

    result = subprocess.run(
        ['curl', '-X', 'POST', 'http://localhost:11434/api/generate',
            '-H', 'Content-Type: application/json', '-d', JSON_PAYLOAD],
        capture_output=True, text=True
    )

    # Use jq to extract the response field from the JSON output
    response_lines = subprocess.run(
        ['jq', '-r', '.response'],
        input=result.stdout,
        capture_output=True,
        text=True
    ).stdout.strip().split('\n')

    # Concatenate the response lines
    response = ''.join(response_lines)

    try:
        response_json = json.loads(response)
        response2 = []
        for match in response_json.get("matches", []):
            response2.append(int(match["field_number"]))
            # response2.insert(int(match["field_number"]))
        # response2 = json.dumps(response_json)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")

    return response, response2
    
def getResponseStep2(user_query, field_numbers, chunk):
    CONTEXT = f"""
    Your job is to analyze the user's query against the provided field keys and return JSON indicating which keys♦ are most relevant.

    INSTRUCTIONS:
    1. Examine the user query carefully.
    2. Compare against these field keys: {json.dumps(FIELD_NAMES, indent=2)}
    3. Return JSON with field numbers as keys and relevance scores (0-10) as values.

    RESPONSE FORMAT:
    {{
    "matches": [
        {{ "key": n,  "value": "value for n", "relevance": 8, "reason": "This field directly addresses the user's query about X" }},
        {{ "key": m,  "value": "value for m", "relevance": 5, "reason": "This field partially addresses the query through Y" }}
    ],
    "no_matches": false
    }}
 
    If no matches are found, return:
    {{
    "matches": [],
    "no_matches": true,
    "explanation": "No relevant keys and values were found because..."
    }}

    USER QUERY: {user_query}
    """

while True:
    user_query = input("What would you like to search for?: ")
    respone,  response2 = getResponseStep1(user_query)
    try:
        print(json.dumps(json.loads(respone), indent=2))
        print(response2)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        print("Raw response:", respone)
        print("Raw response2:", response2)