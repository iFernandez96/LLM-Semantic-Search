import openai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = openai.OpenAI(api_key=api_key)



# Define schema mapping in the system prompt
SYSTEM_PROMPT = """
You are an AI assistant that converts natural language database queries into structured CMR query format.
You have access to the following schema:

### **Supported Data Types**
- **Integer**: `F0=V25` (Field 0 must be 25)
- **Float**: `F1=V3.14` (Field 1 must be approximately 3.14)
- **Enumeration (Keyed by Int)**: `F2=K1` (Field 2 must be Enum Key 1)
- **Pointer**: `F3->TEXEL_12` (Field 3 points to texel ID `TEXEL_12`)
- **Flags**: `F6&FLAG_A` (Field 6 contains `FLAG_A`)
- **Timestamp**: `F7>=V2024-02-01T12:00:00Z` (Field 7 timestamp is after Feb 1, 2024)

### **Logical Operators**
- **AND (`&&`)**: `F0=V25 && F1>V50`
- **OR (`||`)**: `F0=V25 || F1>V50`
- **NOT (`!`)**: `!F5=K2` (*Field 5 is **not** Key 2*)

### **Schema-Based Mappings**
| Human Term | Schema Field | Data Type | Example Query Syntax |
|------------|-------------|-----------|----------------------|
| **Corrosion Type** | `F1` (**Corrosion Type**) | K (Enum) | `F1=K2` (Galvanic Corrosion) |
| **Risk Level** | `F2` (**Component Risk Level**) | K (Enum) | `F2=K1` (Critical) |
| **Resolution Status** | `F3` (**Resolution Status**) | K (Enum) | `F3=K0` (Unresolved) |
| **Inspection Date** | `F4` (**Timestamp - Inspection Date**) | V (Date) | `F4>=V(Today-30)` |

### **Example Translations**
- **"Find all unresolved critical areas in the last 30 days."** → `F3=K0 && F2=K1 && F4>=V(Today-30)`
- **"List corrosion reports of type Galvanic Corrosion after Jan 1, 2023."** → `F1=K2 && F4>=V2023-01-01`
- **"Show all areas where Risk Level is NOT Critical."** → `!F2=K1`

---
### **Now, process the following user query:**
"""

def generate_cmr_query(natural_language_query):
    # Ensure API key is found before making a request
    if not api_key:
        raise ValueError("Missing OpenAI API key. Set OPENAI_API_KEY in your .env file.")

    # Initialize OpenAI client with environment variable
    client = openai.OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": natural_language_query}
        ],
        temperature=0,
        max_tokens=200
    )

    return response.choices[0].message.content  # Return the generated CMR query
# Example usage
nl_query = "Find all unresolved critical areas in the last 30 days."
cmr_query = generate_cmr_query(nl_query)

print("Generated CMR Query:")
print(cmr_query)