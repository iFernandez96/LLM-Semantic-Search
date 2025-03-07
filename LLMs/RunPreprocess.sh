#!/bin/bash

# Function to send a query to the LLM
send_query() {
    local user_query="$1"

    # Define the prompt with the query inserted dynamically
    PROMPT="You are an AI assistant that translates natural language queries into a structured query format specifically designed for preprocessing natural language into a logical format. This format needs to be easily parsed in order to programmatically and logically parsed and dissected into its component parts. Do not respond with anything but the expected output.\n\n\
Schema: \n\n\
Split the given query into easily 
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

