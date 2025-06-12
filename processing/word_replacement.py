# processing/word_replacement.py

import re

# Words that should not be used and their replacements
WORDS_NOT_TO_USE = {
    "assist": "help",
    "commence": "start",
    "deliver": "provide",
    "deploy": "build",
    "dialogue": "discussion",
    "disincentivise": "discourage",
    "documentation": "document",
    "e.g.": "for example",
    "empower": "allow",
    "etc": "including",
    "facilitate": "help",
    "foster": "encourage",
    "garnered": "gathered",
    "guidance": "guide",
    "i.e.": "that is",
    "impact": "affect",
    "incentivise": "motivate",
    "initiate": "begin",
    "key": "important",
    "leverage": "use",
    "liaise": "work with",
    "robust": "well thought out",
    "streamline": "simplify",
    "tackle": "solve",
    "utilise": "use",
    "via": "through",
    "procurement" : "buying",
    "procure" : "buy",
    "aid" : "help",
    "utilise" : "use",
    "requirement" : "need"
   
}

# Words to watch and suggested replacements
WORDS_TO_WATCH = {
    "advance": "improve",
    "agenda": "plan",
    "collaborate": "work with",
    "combat": "solve",
    "just": "",  # Remove filler word
    "savings": "commercial benefits",
    "simple": "",  # Remove subjective word
    "transformation": "change",
    "web page": "webpage"
}

def replace_restricted_words(text):
    """
    Replaces restricted words and phrases with their approved alternatives.
    """
    for word, replacement in {**WORDS_NOT_TO_USE, **WORDS_TO_WATCH}.items():
        pattern = r"\b" + re.escape(word) + r"\b"  # Match whole words only
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text