#!/bin/bash

# Function to send a query to the LLM
send_query() {
    local user_query="$1"

    # killall ollama
    # ollama serve & > /dev/null
    # Define the prompt with the query inserted dynamically
    PROMPT="You are an AI assistant that translates natural language queries into a structured query format specifically designed for Converged Mixed Reality (CMR) texture data. Do not respond with anything but the expected output.\n\n\
Schema & Field Mappings:\n\
- Corrosion Type → F1 (Enumerated) → {Surface = K1, Galvanic = K2, Pitting = K3, Crevice = K4}\n\
- Component Risk Level → F2 (Enumerated) → {Critical = K1, High = K2, Moderate = K3, Low = K4}\n\
- Resolution Status → F3 (Enumerated) → {Unresolved = K0, In Progress = K1, Resolved = K2}\n\
- Inspection Timestamp → F4 (Date)\n\
- Thickness Loss → F5 (Float, Percentage)\n\
- Inspector ID → F6 (Integer)\n\
- Structure Type → F7 (Enumerated) → {Hull = K1, Pipeline = K2, Support Beam = K3, Electrical Box = K4}\n\
- Corrosion Severity → F8 (Enumerated) → {Minor = K1, Moderate = K2, Severe = K3, Extreme = K4}\n\
- Location ID → F9 (Pointer)\n\
- Protective Coating → F10 (Boolean) → {Yes = V1, No = V0}\n\n\
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
User Query: \"$user_query\"\n\n\
Expected Output:"

    # Use jq to format JSON correctly
    JSON_PAYLOAD=$(jq -n --arg model "mistral-nemo" \
                          --arg prompt "$PROMPT" \
                          --argjson options '{"temperature":0, "top_p":1, "top_k":0, "seed":42}' \
                          '{model: $model, prompt: $prompt, stream: false, options: $options}')

    # Send the request to the local LLM API
    curl -X POST http://localhost:11434/api/generate \
         -H "Content-Type: application/json" \
         -d "$JSON_PAYLOAD" | jq '.response' >> response.txt 
}

# Interactive query loop
while true; do
    echo ""
    read -p "Enter a query (or type 'exit' to quit): " query
    if [[ "$query" == "exit" ]]; then
        echo "Exiting query system."
        break
    fi
    send_query "$query"
done

