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
time.sleep(2)

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
            "temperature": 0,
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
            if int(match["relevance"]) >= 7:
                response2.append(int(match["field_number"]))
                # response2.insert(int(match["field_number"]))
        # response2 = json.dumps(response_json)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")

    return response, response2
    
def getResponseStep2(user_query, field_numbers, chunk):

    high_relevance_matches = []
    medium_relevance_matches = []
    low_relevance_matches = []
    response = []

    for field in field_numbers:
        field_data = FIELD_NAMES[f"{field}"]
        field_value = FIELDS[field]['Values']
        length_of_field_value = len(field_value)

        noValue = False
        
        for j in range(0, length_of_field_value, chunk):
            if noValue:
                break
            field_value_chunk = field_value[j:min(j + chunk, length_of_field_value)]
            CONTEXT = f"""
            Your job is to analyze the user's query against the provided field values and return JSON indicating which values are most relevant.
            
            IMPORTANT:
            - If the user is asking for all values of a certain field, return **only the Key where the value is "No Value"** from that field and nothing else.
            - DO NOT return all the values of the field under any circumstances.
            
            INSTRUCTIONS:
            1. Examine the user query carefully.
            2. Understand the field context: {json.dumps(field_data, indent=2)}
            3. Compare against these field values: {json.dumps(field_value_chunk, indent=2)}
            4. Return JSON with field numbers as keys, values, and relevance scores (0-10) as values.
            
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

            JSON_PAYLOAD = json.dumps({
                "model": "mistral-nemo",
                "prompt": CONTEXT,
                "options": {
                    "temperature": 0.05,
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
            
            data = ''.join(response_lines)

            response.append(data)
            try:
                response_json = json.loads(data)
                for match in response_json.get("matches", []): 
                    if int(match["relevance"]) >= 10:
                        high_relevance_matches.append({
                            "field": field_data["name"],
                            "field_number": f"{field}",
                            "key": int(match["key"]),
                            "value": match["value"]
                        })
                    elif int(match["relevance"]) >= 6:
                        medium_relevance_matches.append({
                            "field": field_data["name"],
                            "field_number": f"{field}",
                            "key": int(match["key"]),
                            "value": match["value"]
                        })
                    elif int(match["relevance"]) > 0:
                        low_relevance_matches.append({
                            "field": field_data["name"],
                            "field_number": f"{field}",
                            "key": int(match["key"]),
                            "value": match["value"]
                        })
                    if int(match["key"]) == 0:
                        noValue = True
                        
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response: {e}")
            
    return high_relevance_matches, medium_relevance_matches, low_relevance_matches, response

        # print(f"Field {i}: {field_data}")
        # print(f"Field Value: {field_value}")    
        # print(f"Length of Field Value: {length_of_field_value}")

def getResponseStep3(user_query, gathered_data):
    CONTEXT = f"""
    Your job is to analyze the data received and turn it into a structured logical query as instructed below.
    
    INSTRUCTIONS:
    1. Examine the data and the user query carefully.
    2. If multiple fields are present, use '&&' meaning AND to combine them.
    3. If looking for the inverse of a field, use '!' before the field number.
    4. Return no words other than this structure: F(field_number)=K(key_number) (e.g., !F12=K23, F0=K1, F1=K3 && F2=K21, or !F19=K23 && F11=K27).
    5. If looking for ALL VALUES of a certain field using key 0, do ! in front of the query

    DATA:
    Using this context to create a structed logical query: {json.dumps(gathered_data, indent=2)}
    USER QUERY: {user_query}
    """

    JSON_PAYLOAD = json.dumps({
        "model": "mistral-nemo",
        "prompt": CONTEXT,
        "options": {
            "temperature": 0,
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
    
    data = ''.join(response_lines)

    return data


while True:
    user_query = input("What would you like to search for?: ")
    response, response2 = getResponseStep1(user_query)
    try:
        print(json.dumps(json.loads(response), indent=2))
        print(response2)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        print("Raw response:", response)
        print("Raw response2:", response2)

    rvh, rvm, rvl, raw = getResponseStep2(user_query, response2, 50)
    print(raw)
    print("High Relevance Matches:", rvh)

    structured_query = getResponseStep3(user_query, rvh)
    print("Structured Query:", structured_query)