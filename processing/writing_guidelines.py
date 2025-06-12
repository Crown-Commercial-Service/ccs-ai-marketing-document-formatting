import re
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
API_VERSION = "2024-02-01"

# Initialize OpenAI client for Azure
client = openai.AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version=API_VERSION
)

def apply_writing_guidelines(chunk):
    """
    Applies writing guidelines to improve clarity, conciseness, and readability.
    """
    system_prompt = """
    You are a professional editor specializing in clarity and readability. Revise the given text according to these guidelines:
   
    **General Writing Rules:**
    - Put the most important information first.
    - Except Heading, use "we" instead of "CCS" respectively
    - "Use simple words—assume the reader has no prior knowledge."
    - "Replace complex phrases with single words where possible."
    - "Avoid jargon, technical language, and metaphors (explain only if necessary)."
    - Write concisely with clear bullet points.
    - Keep sentences between 15–25 words for readability.
    - Use active voice instead of passive.
    - Maintain a friendly, conversational tone.
    - Always the acronyms should be in Capitalized.
   

    **Bullet Point Rules:**
    - Keep bullet points structured and **do not introduce new headings** above them.
    - Preserve existing bullet points exactly—**do not change capitalisation unless necessary**.
    - Only capitalise bullet points if they start with a proper noun, acronym, or name.
    - "Review the entire document and eliminate all Oxford commas. For any list of three or more items, ensure there is no comma before the final 'and' or 'or'."
    - Ensure bullet points are **short and concise**, containing only one sentence per point.
    - Do not end bullet points with punctuation **(no full stops, commas, or semicolons).**

    **Formatting Rules:**
    - Preserve all existing headings and subheadings without adding unnecessary ones.
    - The Acronyms should always be capitalized.
    - Keep bold text **only for section headings and key terms**.
    - Do not restructure sections unless necessary for clarity.
    - Remove unwanted spaces between paragraphs.
    - Do not repeat or duplicate content.

    **Return only the revised text. Do not add explanations.**
    """

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": chunk}
        ],
        temperature=0.2
    )

    processed_text = response.choices[0].message.content.strip()

    # 🔥 **Fix Bullet Point Capitalisation Issue**
    def lowercase_bullets(match):
        word = match.group(1)
        if word[0].isupper():  # Keep acronyms/proper nouns unchanged
            return f"\n- {word}"
        return f"\n- {word.lower()}"

    processed_text = re.sub(r"\n- ([A-Z][a-z]+)", lowercase_bullets, processed_text)

    return processed_text

def process_writing_guidelines(chunks):
    """
    Applies writing guidelines to all chunks.
    """
    processed_chunks = []
   
    for i, chunk in enumerate(chunks):
        print(f"Applying Writing Guidelines to Chunk {i+1}...")
        processed_chunk = apply_writing_guidelines(chunk)
        processed_chunks.append(processed_chunk)

    return processed_chunks