#!/bin/bash

# Function to send a query to the LLM
send_query() {
    local user_query="$1"

    # Define the prompt with the query inserted dynamically
    PROMPT="Translate natural spoken language into formal logic using axiomatic structures, enabling mathematical reasoning that can be easily parsed by a program.\n\
\"Show me all of the areas that have galvanic corrosion on critical areas that have not
been resolved in the last 30 days.\""

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

