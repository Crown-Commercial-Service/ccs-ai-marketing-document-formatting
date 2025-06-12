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

def apply_formatting_rules(chunk):
    """
    Applies strict formatting rules to maintain consistency and readability.
    """
    system_prompt = """
    You are an expert in UK English formatting. Apply the following **strict** formatting rules **without changing the original meaning**:

    **Headings and Capitalisation:**
    - Make headings and subheadings **concise and easy to scan**.
    - Capitalise **only the first word** in headings and subheadings, unless they contain proper nouns (e.g., "Crown Commercial Service").
    - Never use **uppercase for emphasis**.
   
    **Bullet Points:**
    - **Remove redundant headings before bullet points**.
    - **Start bullet points with a lowercase letter**, unless they begin with a proper noun or acronym.
    - **Do not end bullet points with a full stop, comma, or semicolon**.
    - **Use only one sentence per bullet point**.
    - **If a bullet point contains multiple ideas, split it into separate points**.

    **Numbers, Money, and Dates:**
    - Use **this date format**: "Thursday 7 November 2017", "Thursday 7 November", "7 November 2017", or "7 November".
    - Use **"to" instead of a dash** in number and date ranges (e.g., "10 to 20" instead of "10–20").
    - Use **the UK pound sign (£) when denoting money**.
    - Never shorten "thousand", "million", or "billion".
    - Write all **numbers in numerals**, except when they start a sentence.
    - For numerals **over 999, use commas** (e.g., "1,100" instead of "1100").
    - Spell out **"first" to "ninth"**, then use numerals for 10th, 11th, etc.
    - Use **the % symbol** instead of writing "percent".

    **General Formatting:**
    - Avoid exclamation marks entirely.
    - Do not use ampersands (&); always spell out "and".
    - Use the time format **"5:30pm" or "5:30am"**, instead of 24-hour format.

    **Output Guidelines:**
    - **Preserve original paragraph breaks, structure, and bullet points**.
    - **Do not reword the text unnecessarily**; only apply formatting.
    - **Return only the formatted text, without explanations**.
    """

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": chunk}
        ],
        temperature=0.2  # Lower temperature for strict formatting
    )

    return response.choices[0].message.content.strip()

def process_formatting(chunks):
    """
    Applies formatting rules to all chunks while maintaining consistency.
    """
    processed_chunks = []
   
    for i, chunk in enumerate(chunks):
        print(f"Applying Formatting Rules to Chunk {i+1}...")
        formatted_chunk = apply_formatting_rules(chunk)
        processed_chunks.append(formatted_chunk)

    return processed_chunks
