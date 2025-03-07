import openai
import os
from dotenv import load_dotenv
import re


# Load environment variables from .env file
load_dotenv()

# Retrieve API key securely from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Ensure the API key is set before making requests
if not api_key:
    raise ValueError("Missing OpenAI API key. Set OPENAI_API_KEY in your .env file.")

# Define the updated schema prompt (same as before)
SYSTEM_PROMPT = """
You are an AI assistant that translates natural language queries into a structured query format specifically designed for Converged Mixed Reality (CMR) texture data.
Do not respond with anything but the expected output.

### **Schema & Field Mappings:**
- **Corrosion Type** → `F1` (Enumerated) → {Surface = K1, Galvanic = K2, Pitting = K3, Crevice = K4}
- **Component Risk Level** → `F2` (Enumerated) → {Critical = K1, High = K2, Moderate = K3, Low = K4}
- **Resolution Status** → `F3` (Enumerated) → {Unresolved = K0, In Progress = K1, Resolved = K2}
- **Inspection Timestamp** → `F4` (Date) → {YYYY-MM-DD}
- **Thickness Loss** → `F5` (Float, Percentage)
- **Inspector ID** → `F6` (Integer)
- **Structure Type** → `F7` (Enumerated) → {Hull = K1, Pipeline = K2, Support Beam = K3, Electrical Box = K4}
- **Corrosion Severity** → `F8` (Enumerated) → {Minor = K1, Moderate = K2, Severe = K3, Extreme = K4}
- **Location ID** → `F9` (Pointer)
- **Protective Coating** → `F10` (Boolean) → {Yes = V1, No = V0}

### **Query Syntax Rules:**
- **Basic Query Format:** `[Comparison]F[FieldIndex][V|K][ValueOrKey]`
- **Logical Operators:** `&&` (AND), `||` (OR), `!` (NOT)

### **Example Queries:**
- **Find critical components with severe corrosion that are unresolved:**
  `F2=K1 && F8=K3 && F3=K0`
- **List structures of type 'Pipeline' inspected in the last 60 days:**
  `F7=K2 && F4>=V(Today-60)`
- **List components with 5% thickness loss:**
  `F5=V(5)`

### **Task:**
Convert each user query below into the structured format, ensuring full schema compliance and deterministic output.
"""

nl_queries = [
    # Corrosion Type
    "Show me all the places that have surface corrosion",
    "List the areas with galvanic corrosion",
    "Let me know where pitting corrosion is present",
    "Where can I find crevice corrosion",

    # Component Risk Level
    "Find critical components",
    "Show me high risk components",
    "Find moderate risk components",
    "Give me low risk components",

    # Resolution Status
    "List unresolved issues",
    "Show me in progress tasks",
    "Find resolved items",

    # Inspection Timestamp
    "List items inspected in the last 30 days",
    "Show me inspections from 2 months ago and earlier",
    "Find inspections from the December 1st, 2021",

    # Thickness Loss
    "Find items with 10% or more thickness loss",
    "Show me items with less than 5% thickness loss",
    "List items with no thickness loss",

    # Inspector ID
    "List inspections by inspector 123",
    "Show me items inspected by inspector 456",
    "Find inspections by inspector 789",

    # Structure Type
    "List hull structures",
    "Show me pipelines",
    "Find support beams",
    "Where are the electrical boxes",

    # Corrosion Severity
    "List minor corrosion",
    "Show me moderate corrosion",
    "Find severe corrosion",
    "Where is the extreme corrosion",

    # Location ID
    "List items at location 123",
    "Show me items at location 456",
    "Find items at location 789",

    # Protective Coating
    "List items with protective coating",
    "Show me items without protective coating",

    # Logical Operators
    "Find components with severe corrosion that are unresolved",
    "List structures of type 'Pipeline' that aren't electrical boxes",
    "List components with 5% thickness loss or parts with 20% or more thickness loss"
]

expected_outputs = {
    "Show me all the places that have surface corrosion": "F1=K1",
    "List the areas with galvanic corrosion": "F1=K2",
    "Let me know where pitting corrosion is present": "F1=K3",
    "Where can I find crevice corrosion": "F1=K4",

    "Find critical components": "F2=K1",
    "Show me high risk components": "F2=K2",
    "Find moderate risk components": "F2=K3",
    "Give me low risk components": "F2=K4",

    "List unresolved issues": "F3=K0",
    "Show me in progress tasks": "F3=K1",
    "Find resolved items": "F3=K2",

    "List items inspected in the last 30 days": "F4>=V(Today-30)",
    "Show me inspections from 2 months ago and earlier": "F4<=V(Today-60)",
    "Find inspections from the December 1st, 2021": "F4=V(2021-12-01)",

    "Find items with 10% or more thickness loss": "F5>=V(10)",
    "Show me items with less than 5% thickness loss": "F5<V(5)",
    "List items with no thickness loss": "F5=V(0)",

    "List inspections by inspector 123": "F6=V(123)",
    "Show me items inspected by inspector 456": "F6=V(456)",
    "Find inspections by inspector 789": "F6=V(789)",

    "List hull structures": "F7=K1",
    "Show me pipelines": "F7=K2",
    "Find support beams": "F7=K3",
    "Where are the electrical boxes": "F7=K4",

    "List minor corrosion": "F8=K1",
    "Show me moderate corrosion": "F8=K2",
    "Find severe corrosion": "F8=K3",
    "Where is the extreme corrosion": "F8=K4",

    "List items at location 123": "F9=V(123)",
    "Show me items at location 456": "F9=V(456)",
    "Find items at location 789": "F9=V(789)",

    "List items with protective coating": "F10=V1",
    "Show me items without protective coating": "F10=V0",

    "Find components with severe corrosion that are unresolved": "F8=K3 && F3=K0",
    "List structures of type 'Pipeline' that aren't electrical boxes": "F7=K2 && F7!=K4",
    "List components with 5% thickness loss or parts with 20% or more thickness loss": "F5=V(5) || F5>=V(20)"
}

def generate_cmr_queries(natural_language_queries):
    """Generates structured CMR queries for multiple natural language queries."""
    
    # Initialize OpenAI client
    client = openai.OpenAI(api_key=api_key)

    # Format all queries into one request
    queries_text = "\n".join([f"{i+1}. {query}" for i, query in enumerate(natural_language_queries)])

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Convert the following queries:\n{queries_text}"}
        ],
        temperature=0,
        max_tokens=500
    )

    # Split response into a list (assuming OpenAI returns one query per line)
    structured_queries = response.choices[0].message.content.strip().split("\n")

    return structured_queries  # Return structured CMR queries as a list

#Clean up query results for testing piurposes    
def normalize_query(query):
    """
    Cleans up the generated query by:
    - Removing backticks, quotes, or extra spaces
    - Ensuring consistent formatting
    """
    query = query.strip()  # Remove leading/trailing spaces
    query = re.sub(r"[`']", "", query)  # Remove backticks and single quotes
    query = re.sub(r"^\d+\.\s*", "", query)  # Remove leading number + period (e.g., '28. ')
    return query


if __name__ == "__main__":
    cmr_queries = generate_cmr_queries(nl_queries)

    print("\n **Verification Results:**\n")
    for i, (nl_query, cmr_query) in enumerate(zip(nl_queries, cmr_queries), 1):
        expected = expected_outputs.get(nl_query, "UNKNOWN")

        # Normalize queries before comparison
        normalized_generated = normalize_query(cmr_query)
        normalized_expected = normalize_query(expected)

        is_correct = "MATCH" if normalized_generated == normalized_expected else "MISMATCH"

        print(f"Query {i}: {nl_query}")
        print(f"🔹 Generated CMR Query: {normalized_generated}")
        print(f"🔹 Expected Query: {normalized_expected}")
        print(f"🔹 Result: {is_correct}\n")