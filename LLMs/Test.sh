#!/bin/bash

send_query() {
    local user_query="$1"

    echo -e "User Query: \"$user_query\""

}

read query

send_query "$query"