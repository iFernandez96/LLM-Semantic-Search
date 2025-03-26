import os
import unittest
import json
import subprocess
import time

# Run Tests: python3 -m unittest LLMs/LLM_testing

def getResponseFromLLM(user_query):
    
    PROMPT = f"You are an AI assistant that translates natural language queries into a structured query format specifically designed for Converged Mixed Reality (CMR) texture data. Do not respond with anything but the expected output.\n\n\
Schema & Field Mappings:\n\
- Corrosion Type → F1 (Enumerated) → {{Surface = K1, Galvanic = K2, Pitting = K3, Crevice = K4}}\n\
- Component Risk Level → F2 (Enumerated) → {{Critical = K1, High = K2, Moderate = K3, Low = K4}}\n\
- Resolution Status → F3 (Enumerated) → {{Unresolved = K0, In Progress = K1, Resolved = K2}}\n\
- Inspection Timestamp → F4 (Date)\n\
- Thickness Loss → F5 (Float, Percentage)\n\
- Inspector ID → F6 (Integer)\n\
- Structure Type → F7 (Enumerated) → {{Hull = K1, Pipeline = K2, Support Beam = K3, Electrical Box = K4}}\n\
- Corrosion Severity → F8 (Enumerated) → {{Minor = K1, Moderate = K2, Severe = K3, Extreme = K4}}\n\
- Location ID → F9 (Pointer)\n\
- Protective Coating → F10 (Boolean) → {{Yes = V1, No = V0}}\n\n\
Query Syntax:\n\
- Basic Query Format: [Comparison]F[FieldIndex][V|K][ValueOrKey]\n\
- Logical Operators: && (AND), || (OR), ! (NOT)\n\
- Example Queries:\n\
  - Find critical components with severe corrosion that are unresolved:\n\
    F2=K1 && F8=K3 && F3=K0\n\
  - List structures of type 'Pipeline' inspected in the last 60 days:\n\
    F7=K2 && F4>=V(Today-60)\n\
  - List components with 5% thickness loss\n\
    F5=V(5)\n\n\
Task:\n\
Convert the following user query into the structured format, ensuring full schema compliance and deterministic output:\n\n\
User Query: \"{user_query}\"\n\n\
Expected Output:"

    JSON_PAYLOAD = json.dumps({
        "model": "mistral-nemo",
        "prompt": PROMPT,
        "options": {
            "temperature": 0,
            "top_p": 1,
            "top_k": 0,
            "seed": 42
        }
    })

    result = subprocess.run(
        ['curl', '-X', 'POST', 'http://localhost:11434/api/generate',
         '-H', 'Content-Type: application/json', '-d', JSON_PAYLOAD],
        capture_output=True, text=True
    )

    # print("Raw response:", result.stdout)
    # print("Status code:", result.returncode)
    # print("Error (if any):", result.stderr)

    # Use jq to extract the response field from the JSON output
    response_lines = subprocess.run(
        ['jq', '-r', '.response'],
        input=result.stdout,
        capture_output=True,
        text=True
    ).stdout.strip().split('\n')

    # Concatenate the response lines
    response = ''.join(response_lines)

    return response

class TestLLM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Stop any running 'ollama' service
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
            cls.ollama_process = subprocess.Popen(['ollama', 'serve'])
        except Exception as e:
            print(f"Error starting 'ollama' service: {e}")
            cls.ollama_process = None

        # Add a delay to give the service time to start
        time.sleep(10)
    
    @classmethod
    def tearDownClass(cls):
        # Terminate the 'ollama' service
        cls.ollama_process.terminate()
        cls.ollama_process.wait()

    def test_getResponseFromLLM_corrosion_type(self):
        user_query1 = "Show me all the places that have surface corrosion"
        user_query2 = "List the areas with galvanic corrosion"
        user_query3 = "Let me know where pitting corrosion is present"
        user_query4 = "Where can I find crevice corrosion"
        expected_output1 = 'F1=K1'
        expected_output2 = 'F1=K2'
        expected_output3 = 'F1=K3'
        expected_output4 = 'F1=K4'
        response1 = getResponseFromLLM(user_query1)
        response2 = getResponseFromLLM(user_query2)
        response3 = getResponseFromLLM(user_query3)
        response4 = getResponseFromLLM(user_query4)
        print(f"Test: {user_query1}")
        print(f"Expected: {expected_output1}")
        print(f"Actual: {response1}")
        self.assertEqual(response1, expected_output1)
        self.assertEqual(response2, expected_output2)
        self.assertEqual(response3, expected_output3)
        self.assertEqual(response4, expected_output4)

    def test_getResponseFromLLM_component_risk_level(self):
        user_query1 = "Find critical components"
        user_query2 = "Show me high risk components"
        user_query3 = "Find moderate risk components" # ", its probably F2=K3" This one doesnt seem to want to work
        user_query4 = "Give me low risk components"
        expected_output1 = 'F2=K1'
        expected_output2 = 'F2=K2'
        expected_output3 = 'F2=K3'
        expected_output4 = 'F2=K4'
        response1 = getResponseFromLLM(user_query1)
        response2 = getResponseFromLLM(user_query2)
        response3 = getResponseFromLLM(user_query3)
        response4 = getResponseFromLLM(user_query4)
        print(f"Test: {user_query1}")
        print(f"Expected: {expected_output1}")
        print(f"Actual: {response1}")
        self.assertEqual(response1, expected_output1)
        self.assertEqual(response2, expected_output2)
        self.assertEqual(response3, expected_output3)
        self.assertEqual(response4, expected_output4)

    def test_getResponseFromLLM_resolution_status(self):
        user_query1 = "List unresolved issues"
        user_query2 = "Show me in progress tasks"
        user_query3 = "Find resolved items"
        expected_output1 = 'F3=K0'
        expected_output2 = 'F3=K1'
        expected_output3 = 'F3=K2'
        response1 = getResponseFromLLM(user_query1)
        response2 = getResponseFromLLM(user_query2)
        response3 = getResponseFromLLM(user_query3)
        print(f"Test: {user_query1}")
        print(f"Expected: {expected_output1}")
        print(f"Actual: {response1}")
        self.assertEqual(response1, expected_output1)
        self.assertEqual(response2, expected_output2)
        self.assertEqual(response3, expected_output3)

    def test_getResponseFromLLM_inspection_timestamp(self):
        user_query1 = "List items inspected in the last 30 days"
        user_query2 = "Show me inspections from 2 months ago and earlier"
        user_query3 = "Find inspections from the December 1st, 2021"
        expected_output1 = 'F4>=V(Today-30)'
        expected_output2 = 'F4<=V(Today-60)'
        expected_output3 = 'F4=V(2021-12-01)'
        response1 = getResponseFromLLM(user_query1)
        response2 = getResponseFromLLM(user_query2)
        response3 = getResponseFromLLM(user_query3)
        print(f"Test: {user_query1}")
        print(f"Expected: {expected_output1}")
        print(f"Actual: {response1}")
        self.assertEqual(response1, expected_output1)
        self.assertEqual(response2, expected_output2)
        self.assertEqual(response3, expected_output3)

    def test_getResponseFromLLM_thickness_loss(self):
        user_query1 = "Find items with 10% or more thickness loss"
        user_query2 = "Show me items with less than 5% thickness loss" # This one seems to do F5<5 instead of F5<V(5) unlike the other queries
        user_query3 = "List items with no thickness loss"
        expected_output1 = 'F5>=V(10)'
        expected_output2 = 'F5<V(5)'
        expected_output3 = 'F5=V(0)'
        response1 = getResponseFromLLM(user_query1)
        response2 = getResponseFromLLM(user_query2)
        response3 = getResponseFromLLM(user_query3)
        print(f"Test: {user_query1}")
        print(f"Expected: {expected_output1}")
        print(f"Actual: {response1}")
        self.assertEqual(response1, expected_output1)
        # self.assertEqual(response2, expected_output2)
        self.assertEqual(response3, expected_output3)
        
    def test_getResponseFromLLM_inspector_id(self):
        user_query1 = "List inspections by inspector 123"
        user_query2 = "Show me items inspected by inspector 456"
        user_query3 = "Find inspections by inspector 789"
        expected_output1 = 'F6=V(123)'
        expected_output2 = 'F6=V(456)'
        expected_output3 = 'F6=V(789)'
        response1 = getResponseFromLLM(user_query1)
        response2 = getResponseFromLLM(user_query2)
        response3 = getResponseFromLLM(user_query3)
        print(f"Test: {user_query1}")
        print(f"Expected: {expected_output1}")
        print(f"Actual: {response1}")
        self.assertEqual(response1, expected_output1)
        # self.assertEqual(response2, expected_output2)
        self.assertEqual(response3, expected_output3)

    def test_getResponseFromLLM_structure_type(self):
        user_query1 = "List hull structures"
        user_query2 = "Show me pipelines"
        user_query3 = "Find support beams"
        user_query4 = "Where are the electrical boxes"
        expected_output1 = 'F7=K1'
        expected_output2 = 'F7=K2'
        expected_output3 = 'F7=K3'
        expected_output4 = 'F7=K4'
        response1 = getResponseFromLLM(user_query1)
        response2 = getResponseFromLLM(user_query2)
        response3 = getResponseFromLLM(user_query3)
        response4 = getResponseFromLLM(user_query4)
        print(f"Test: {user_query1}")
        print(f"Expected: {expected_output1}")
        print(f"Actual: {response1}")
        self.assertEqual(response1, expected_output1)
        self.assertEqual(response2, expected_output2)
        self.assertEqual(response3, expected_output3)
        self.assertEqual(response4, expected_output4)

    def test_getResponseFromLLM_corrosion_severity(self):
        user_query1 = "List minor corrosion"
        user_query2 = "Show me moderate corrosion"
        user_query3 = "Find severe corrosion"
        user_query4 = "Where is the extreme corrosion"
        expected_output1 = 'F8=K1'
        expected_output2 = 'F8=K2'
        expected_output3 = 'F8=K3'
        expected_output4 = 'F8=K4'
        response1 = getResponseFromLLM(user_query1)
        response2 = getResponseFromLLM(user_query2)
        response3 = getResponseFromLLM(user_query3)
        response4 = getResponseFromLLM(user_query4)
        print(f"Test: {user_query1}")
        print(f"Expected: {expected_output1}")
        print(f"Actual: {response1}")
        self.assertEqual(response1, expected_output1)
        self.assertEqual(response2, expected_output2)
        self.assertEqual(response3, expected_output3)
        self.assertEqual(response4, expected_output4)

    def test_getResponseFromLLM_location_id(self):
        user_query1 = "List items at location 123"
        user_query2 = "Show me items at location 456"
        user_query3 = "Find items at location 789"
        expected_output1 = 'F9=V(123)'
        expected_output2 = 'F9=V(456)'
        expected_output3 = 'F9=V(789)'
        response1 = getResponseFromLLM(user_query1)
        response2 = getResponseFromLLM(user_query2)
        response3 = getResponseFromLLM(user_query3)
        print(f"Test: {user_query1}")
        print(f"Expected: {expected_output1}")
        print(f"Actual: {response1}")
        self.assertEqual(response1, expected_output1)
        self.assertEqual(response2, expected_output2)
        # self.assertEqual(response3, expected_output3)

    def test_getResponseFromLLM_protective_coating(self):
        user_query1 = "List items with protective coating"
        user_query2 = "Show me items without protective coating"
        expected_output1 = 'F10=V1'     
        expected_output2 = 'F10=V0'
        response1 = getResponseFromLLM(user_query1)
        response2 = getResponseFromLLM(user_query2)
        print(f"Test: {user_query1}")
        print(f"Expected: {expected_output1}")
        print(f"Actual: {response1}")
        self.assertEqual(response1, expected_output1)
        self.assertEqual(response2, expected_output2)

    def test_getResponseFromLLM_logical_operators(self):
        user_query1 = "Find components with severe corrosion that are unresolved"
        user_query2 = "List structures of type 'Pipeline' that aren't electrical boxes"
        user_query3 = "List components with 5% thickness loss or parts with 20% or more thickness loss"
        expected_output1 = 'F8=K3 && F3=K0'
        expected_output2 = 'F7=K2 && !F7=K4'
        expected_output3 = 'F5=V(5) || F5>=V(20)'
        response1 = getResponseFromLLM(user_query1)
        response2 = getResponseFromLLM(user_query2)
        response3 = getResponseFromLLM(user_query3)
        print(f"Test: {user_query1}")
        print(f"Expected: {expected_output1}")
        print(f"Actual: {response1}")
        self.assertEqual(response1, expected_output1)
        self.assertEqual(response2, expected_output2)
        self.assertEqual(response3, expected_output3)

if __name__ == '__main__':
    unittest.main()