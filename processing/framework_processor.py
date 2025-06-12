import csv
import logging
import re

class FrameworkProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.frameworks = self.read_frameworks()

    def read_frameworks(self):
        """Reads the framework CSV file and returns a dictionary of framework names and numbers."""
        frameworks = {}
        try:
            with open(self.file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter='\t')  # Use tab as the delimiter
                logging.info(f"CSV Columns: {reader.fieldnames}")  # Log column names for debugging

                if 'framework name' not in reader.fieldnames or 'framework number' not in reader.fieldnames:
                    logging.error("❌ Required columns ('framework name' or 'framework number') not found in the CSV file.")
                    return frameworks

                for row in reader:
                    if row['framework name'].strip() and row['framework number'].strip():
                        framework_name = row['framework name'].strip().lower()
                        framework_number = row['framework number'].strip()
                        frameworks[framework_name] = framework_number

                logging.info(f"✅ Frameworks loaded: {len(frameworks)} frameworks found.")
                logging.debug(f"Sample frameworks: {list(frameworks.items())[:5]}...")  # Log first few frameworks
               
                return frameworks
        except Exception as e:
            logging.error(f"❌ Error reading file: {e}")
            return {}

    def replace_frameworks(self, text):
        """
        Replaces framework names with their numbers **before chunking**.
        Ensures first occurrence keeps the name, while subsequent uses replace it.
        """
        logging.info(f"🔄 Replacing frameworks before chunking...")

        text_lower = text.lower()
        first_occurrence = {framework: True for framework in self.frameworks}
        sorted_frameworks = sorted(self.frameworks.keys(), key=len, reverse=True)  # Sort longest first

        def replace_match(match):
            """Handles replacement logic while preserving case sensitivity."""
            matched_text = match.group(0)
            framework_name = matched_text.lower()

            if framework_name in self.frameworks:
                framework_number = self.frameworks[framework_name]
                if first_occurrence[framework_name]:
                    first_occurrence[framework_name] = False
                    return f"{matched_text} [{framework_number}]"  # Keep original name + number
                else:
                    return f"[{framework_number}]"  # Replace with number only

            return matched_text  # No change if not found

        # Use regex to replace full words only (avoids partial matches)
        pattern = r'\b(' + '|'.join(re.escape(name) for name in sorted_frameworks) + r')\b'
        processed_text = re.sub(pattern, replace_match, text, flags=re.IGNORECASE)

        logging.info(f"✅ Framework replacement complete.")
        return processed_text