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

def adjust_tone(chunk):
    """
    Sends a text chunk to Azure OpenAI GPT-4o for tone adjustment while preserving structure.
    Ensures bullet points and section headings are not broken.
    """
    system_prompt = system_prompt = """You are a professional editor. Adjust the tone of the given text while following these rules :

    IMPORTANT - *Rephrase or rewrite all ideas instead of deleting them. Keep all original content meaningful — even if tone needs significant adjustment.*
    **Content integrity rule (new):**
    - **Do NOT remove or skip any sentence or idea. Instead, rewrite or rephrase every part of the input to match the correct tone, even if the original is exaggerated, vague, arrogant, or informal. Every sentence must be preserved in meaning.**

    **Tone requirements:**
    - Be supportive, empowering, knowledgeable, and efficient.
    - Be approachable, friendly, empathetic, encouraging, inspiring, authoritative, understanding, invaluable, clear, and courteous.
    - Sound confident, evidence-based, solution-oriented, human, positive, and forward-looking.

    **Avoid:**
    - Sounding overly technical, overly complex, excessively enthusiastic, or unrealistic.
    - Sounding overly familiar, patronising, arrogant, inflexible, stubborn, or exaggerated.
    - Using non-English words (e.g. "au fait", "via", "per se", "ad hoc", "per annum").
    - Using old English words (e.g. "thus", "therefore", "hence").

    **Important formatting rules:**
    - **Preserve bullet points and numbered lists exactly as they are.**
    - **Ensure bullet points are never split across chunks.** If a bullet point is incomplete, move it entirely to the next chunk.
    - **Headings should never be broken across chunks.**
    - **Ensure bullet points start with a lowercase letter, unless they begin with a proper noun or acronym.**
    - **Avoid repeating or truncating sentences across chunks.**

    **Return ONLY the adjusted text. Do NOT add explanations.**
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
    processed_text = re.sub(r'\n•\s+([A-Z])', lambda m: f'\n• {m.group(1).lower()}', processed_text)
    processed_text = re.sub(r'\n-\s+([A-Z])', lambda m: f'\n- {m.group(1).lower()}', processed_text)

    return processed_text
def process_chunks(chunks):
    """
    Processes all chunks through the Tone Adjustment Agent.
    Ensures bullet points, headings, and sentence integrity across chunks.
    Includes fallback and logging for failed or truncated chunks.
    """
    processed_chunks = []

    for i, chunk in enumerate(chunks):
        print(f"\n🔧 Processing Chunk {i+1}...")
        try:
            processed_chunk = adjust_tone(chunk)
            if not processed_chunk or len(processed_chunk.split()) < 20:
                print(f"⚠️ Chunk {i+1} is empty or suspiciously short. Falling back to original.")
                processed_chunk = chunk
            else:
                print(f"✅ Chunk {i+1} processed. Length: {len(processed_chunk)}")

        except Exception as e:
            print(f"❌ Error in Chunk {i+1}: {e}")
            processed_chunk = chunk

        # Handle split bullets from previous chunk
        if i > 0:
            previous_chunk = processed_chunks[-1]
            if previous_chunk.strip().endswith("•") or previous_chunk.strip().endswith("-"):
                processed_chunks[-1] = previous_chunk.strip() + " " + processed_chunk
            else:
                processed_chunks.append(processed_chunk)
        else:
            processed_chunks.append(processed_chunk)

    return processed_chunks

