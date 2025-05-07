import spacy
from spacy.matcher import Matcher

'''
I want to see the first five parts that are rusting but have no acidic corrosion, on high priority areas.
I want to see the first five parts that have rusting but no galvanic corrosion, on high priority areas.
Show me all of the areas that have galvanic corrosion on critical areas that have not been resolved in the last 30 days.
Show me all the places that have cracks
Show me all of the sections that have perishable items expiring within the next 30 days and have not been restocked recently.
I want to see the first five items that are running low but not out of stock, in high-demand sections.
I want to see the first five products that are low in stock but not out of stock, in high-demand categories.
'''


nlp = spacy.load("en_core_web_md")
matcher = Matcher(nlp.vocab)

# pattern to catch things like "panel 41 L"
matcher.add("OBJECT_ID_PATTERN", [[
    {"POS": "NOUN"},
    {"LIKE_NUM": True},
    {"IS_ALPHA": True}
]])

matcher.add("OBJECT_NUM_PATTERN", [[
    {"POS": "NOUN"},
    {"LIKE_NUM": True}
]])

query = input("> ")

while query.lower() != "quit":
    doc = nlp(query)

    filtered_noun_chunks = {chunk.text.replace("the ", "").strip() for chunk in doc.noun_chunks if chunk.root.pos_ not in ["PRON", "DET"]}

    noun_lemmas = {token.lemma_ for token in doc if token.pos_ == "NOUN"}
    verb_lemmas = {token.lemma_ for token in doc if token.pos_ == "VERB"}

    doc2 = nlp(" ".join(verb_lemmas))
    for token in doc2:
        if token.pos_ == "NOUN":
            noun_lemmas.add(token.text)

    extra_terms = {token.text for token in doc if token.pos_ == "VERB" and token.lemma_ in noun_lemmas}

    negated_verbs = {f"not {token.text}" for token in doc if token.pos_ == "VERB" and any(child.dep_ == "neg" for child in token.children)}

    extra_terms = {term for term in extra_terms if f"not {term}" not in negated_verbs}

    matched_phrases = {
        doc[start:end].text.lower() for _, start, end in matcher(doc)
    }

    all_terms = filtered_noun_chunks.union(extra_terms).union(negated_verbs).union(matched_phrases)


    EXCLUDED_WORDS = {"show", "list", "want", "see", "find"}

    normalized_terms = {term: term.lower().strip() for term in all_terms}

    normalized_to_original = {}
    for term, norm in normalized_terms.items():
        if norm not in normalized_to_original or len(term) > len(normalized_to_original[norm]):
            normalized_to_original[norm] = term

    final_results = sorted({
        original for norm, original in normalized_to_original.items()
        if not any(
            norm != other_norm and norm in other_norm
            for other_norm in normalized_to_original.keys()
        )
        and norm not in EXCLUDED_WORDS
    })

    if final_results:
        print("\n*** Key Information ***")
        print("-" * 40)
        for term in final_results:
            print(f"\t * {term.capitalize()}")
        print("-" * 40, "\n")
    else:
        print("\nNo relevant terms found\n")

    query = input("> ")

