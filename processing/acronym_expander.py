import os
import re
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
API_VERSION = "2024-02-01"

client = openai.AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version=API_VERSION
)

# Static list of acronyms expected to appear only once in full form
STATIC_ACRONYMS = {
    "Attorney General’s Office": "AGO",
    "Cabinet Office": "CO",
    "Department for Business and Trade": "DBT",
    "Department for Culture, Media and Sport": "DCMS",
    "Department for Education": "DfE",
    "Department for Energy Security and Net Zero": "DESNZ",
    "Department for Environment, Food and Rural Affairs": "Defra",
    "Department for Science, Innovation and Technology": "DSIT",
    "Department for Transport": "DfT",
    "Department for Work and Pensions": "DWP",
    "Department of Health and Social Care": "DHSC",
    "Foreign, Commonwealth and Development Office": "FCDO",
    "HM Treasury": "HMT",
    "Home Office": "HO",
    "Ministry of Defence": "MOD",
    "Ministry of Justice": "MOJ",
    "Invitation to Tender": "ITT",
    "Dynamic Purchasing System": "DPS",
    "Crown Commercial Service": "CCS"
}

def fetch_additional_acronyms(text):
    prompt = """
    You are a UK government Crown Commercial Service writing assistant.

    Extract any acronyms that appear in the following text and are relevant to the Crown Commercial Service or public sector procurement.

    Return them as 'Full Form (ACRONYM)' — one per line. Only output valid acronym pairs. Do not explain or add anything else.
    ⚠️ IMPORTANT INSTRUCTIONS:
- Do not alter, rephrase, or modify the text in any way.
- Do not change punctuation, grammar, structure, or formatting.
- Preserve the original text exactly as it is, except for capitalizing acronyms.
- Return the processed text without explanations, metadata, or additional notes.
    """

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": prompt.strip()},
            {"role": "user", "content": text}
        ],
        temperature=0.2
    )

    result = response.choices[0].message.content.strip()
    dynamic_acronyms = {}
    for line in result.split("\n"):
        match = re.match(r"(.+?)\s+\(([^)]+)\)", line.strip())
        if match:
            full_form, acronym = match.groups()
            dynamic_acronyms[full_form.strip()] = acronym.strip()

    print("🔍 Fetched dynamic acronyms from OpenAI:", dynamic_acronyms)
    return dynamic_acronyms

# Global dictionary to track which acronyms have been expanded
used = {}
# Global dictionary to track which acronyms have been expanded
used = {}

def apply_acronym_logic(text, dynamic_acronyms=None):
    global used
    used.clear()  # Clear before processing
    print("\n=== 🔍 Starting Acronym Replacement Process ===\n")
    print(f"📝 Original Text: {text[:500]}...")  # Displaying a preview of the input text

    # Combine static and dynamic acronyms
    all_acronyms = {k: v for k, v in STATIC_ACRONYMS.items()}
    if dynamic_acronyms:
        all_acronyms.update(dynamic_acronyms)

    print(f"\n📂 Total Acronyms Available for Replacement: {len(all_acronyms)}")
    print(f"📂 All Acronyms Dictionary: {all_acronyms}")

    # Prepare a case-insensitive dictionary for lookup
    lowercase_acronyms = {k.lower(): v for k, v in all_acronyms.items()}
    lowercase_full_forms = {v.lower(): k for k, v in all_acronyms.items()}
   
    print("\n📂 Lowercase Acronyms Dictionary:", lowercase_acronyms)
    print("📂 Lowercase Full Forms Dictionary:", lowercase_full_forms)

    def replacer(match):
        match_text = match.group(0)
        lower_text = match_text.lower()

        print(f"\n🔎 Found Match: '{match_text}' (lowercased: '{lower_text}')")

        # Check if the match is already used (i.e., processed before)
        if lower_text in used:
            print(f"⚠️ Skipping already processed term: '{match_text}'")
            return match_text

        if lower_text in lowercase_acronyms:
            acronym = lowercase_acronyms[lower_text]
            if lower_text not in used:
                used[lower_text] = True
                print(f"📌 First occurrence of full form '{match_text}'. Expanding to: '{match_text} ({acronym})'")
                return f"{match_text} ({acronym})"
            else:
                print(f"⚠️ Subsequent occurrence of full form '{match_text}'. Using acronym only: '{acronym}'")
                return acronym

        elif lower_text in lowercase_full_forms:
            full_form = lowercase_full_forms[lower_text]
            if lower_text not in used:
                used[lower_text] = True
                print(f"📌 First occurrence of acronym '{match_text}'. Expanding to: '{full_form} ({match_text})'")
                return f"{full_form} ({match_text})"
            else:
                print(f"⚠️ Subsequent occurrence of acronym '{match_text}'. Using acronym only: '{match_text}'")
                return match_text

        print(f"❓ Unmatched term '{match_text}', leaving as is.")
        return match_text

    # Generate regex pattern to match all acronyms and their full forms
    pattern = r'\b(?:' + '|'.join(re.escape(k) for k in lowercase_acronyms.keys()) + r'|' + '|'.join(re.escape(v) for v in lowercase_acronyms.values()) + r')\b'
    print(f"\n🔍 Generated Regex Pattern for Matching: {pattern}\n")

    # Process the text using re.sub()
    processed_text = re.sub(pattern, replacer, text, flags=re.IGNORECASE)

    print("\n✅ Processed Text After Acronym Replacement:\n", processed_text[:500], "...\n")
    print("\n📂 Used Acronyms Log (Used Dictionary):", used)
    print("\n=== ✅ Acronym Replacement Process Completed ===\n")

    return post_process_acronyms(processed_text)

    # Generate regex pattern to match all acronyms and their full forms
    pattern = r'\b(?:' + '|'.join(re.escape(k) for k in all_acronyms.keys()) + r'|' + '|'.join(re.escape(v) for v in all_acronyms.values()) + r')\b'
    print(f"\n🔍 Generated Regex Pattern for Matching: {pattern}\n")

    # Process the text using re.sub()
    processed_text = re.sub(pattern, replacer, text, flags=re.IGNORECASE)

    print("\n✅ Processed Text After Acronym Replacement:\n", processed_text[:500], "...\n")
    print("\n📂 Used Acronyms Log (Used Dictionary):", used)
    print("\n=== ✅ Acronym Replacement Process Completed ===\n")

    return processed_text
def post_process_acronyms(text):
    """
    After acronym replacement, ensure acronyms are capitalized correctly by calling OpenAI again.
    """
    prompt = f"""
You are a UK government Crown Commercial Service writing assistant.

Your task is to ensure that all acronyms in the following text are capitalized correctly.

⚠️ IMPORTANT INSTRUCTIONS:
- Do not include the acronym in the headings, Include th
- Only capitalize acronyms that should be in uppercase (e.g., CCS, SMEs, DPS, etc.).
- Do not alter, rephrase, or modify the text in any way.
- Do not change punctuation, grammar, structure, or formatting.
- Preserve the original text exactly as it is, except for capitalizing acronyms.
- Return the processed text without explanations, metadata, or additional notes.

Text to process:
    {text}
    """

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": prompt.strip()},
                {"role": "user", "content": text}
            ],
            temperature=0.2
        )

        result = response.choices[0].message.content.strip()
        print("✅ Processed text from OpenAI for capitalization correction:\n", result[:500])
        return result
    except Exception as e:
        print(f"❌ Error during post-processing: {str(e)}")
        return text

def apply_acronym_expansion(full_text: str) -> str:
    dynamic_acronyms = fetch_additional_acronyms(full_text)
    all_acronyms = {k.casefold(): v for k, v in STATIC_ACRONYMS.items()}
    all_acronyms.update({k.casefold(): v for k, v in dynamic_acronyms.items()})

    print("🧠 Applying acronym logic for", len(all_acronyms), "total acronyms.")

    processed_text = apply_acronym_logic(full_text, all_acronyms)
    return processed_text