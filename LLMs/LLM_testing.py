import unittest
import json
import subprocess
import time

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
    F7=K2 && F4>=V(Today-60)\n\n\
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
        # Ensure any existing 'ollama' processes are killed
        try:
            subprocess.run(['killall', 'ollama'], check=True)
        except subprocess.CalledProcessError:
            pass  # Ignore the error if no 'ollama' process is found

        # Start the 'ollama' service
        cls.ollama_process = subprocess.Popen(['ollama', 'serve'])

        # Add a delay to give the service time to start
        time.sleep(10)
    
    @classmethod
    def tearDownClass(cls):
        # Terminate the 'ollama' service
        cls.ollama_process.terminate()
        cls.ollama_process.wait()

    def test_getResponseFromLLM(self):
        user_query = "Find critical components with severe corrosion that are unresolved"
        expected_output = 'F2=K1 && F8=K3 && F3=K0'
        
        response = getResponseFromLLM(user_query)
        print(f"Test: {user_query}")
        print(f"Expected: {expected_output}")
        print(f"Actual: {response}")
        self.assertEqual(response, expected_output)

    def test_getResponseFromLLM_pipeline_inspection(self):
        user_query = "List structures of type 'Pipeline' inspected in the last 60 days"
        expected_output = 'F7=K2 && F4>=V(Today-60)'
        
        response = getResponseFromLLM(user_query)
        print(f"Test: {user_query}")
        print(f"Expected: {expected_output}")
        print(f"Actual: {response}")
        self.assertEqual(response, expected_output)

    def test_getResponseFromLLM_protective_coating(self):
        user_query = "Find unresolved components with protective coating"
        expected_output = 'F3=K0 && F10=V1'
        
        response = getResponseFromLLM(user_query)
        print(f"Test: {user_query}")
        print(f"Expected: {expected_output}")
        print(f"Actual: {response}")
        self.assertEqual(response, expected_output)

if __name__ == '__main__':
    unittest.main()