from fuzzywuzzy import fuzz
import pprint

def chunk_of_schema(query):
    with open("../front_end/user_selected_file_contents.txt", "r") as schemaFile:
        lines = schemaFile.readlines()

    max_similarity = 0
    best_line = ""
    best_word = ""
    best_lines = []

    max_index = 0
    chunk = []
    chunk_size = 100
    
    for word in query.split("\n"):
        for i, line in enumerate(lines):
            line = line.strip().replace('"', '')
            # print(f"Comparing:\n  word: '{word.lower()}'\n  line: '{line.lower()}'")
            similarity = fuzz.ratio(word.lower(), line.lower())
            # print(f"Line {i}: {line!r}, Similarity: {similarity}")
            if similarity >= max_similarity:
                max_similarity = similarity
                best_line = line
                best_lines = lines
                max_index = i
                best_word = word
    
    print(best_word)
    print(best_line)
    print(max_similarity)
    
    if max_index - chunk_size > 0:
        chunk = best_lines[max_index - chunk_size: max_index + chunk_size]
    else:
        chunk = best_lines[0 : max_index + chunk_size]

    pprint.pprint(chunk)

search_in_schema = input("Enter Word(s): ")
chunk_of_schema(search_in_schema)


