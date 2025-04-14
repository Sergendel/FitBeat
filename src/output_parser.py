import re
import json

class OutputParser:
    def parse_response(self, llm_response):
        try:
            numeric_ranges = llm_response.get("numeric_ranges", {})
            summary = llm_response.get("summary", "default_folder")

            params = {}

            for key, value in numeric_ranges.items():
                # single-value parameters
                if key in ["explicit", "mode", "time_signature"]:
                    params[key] = value
                # numeric range parameters
                elif isinstance(value, list) and len(value) == 2:
                    params[key] = [value[0], value[1]]
                else:
                    params[key] = None  # Fallback for any unexpected format

            folder_name = re.sub(r'[\\/*?:"<>|]', "_", summary.lower().replace(" ", "_"))

            return params, folder_name

        except Exception as e:
            print(f"General parsing error: {e}")
            return None, None

    def parse_ranked_playlist(self, llm_response):
        if isinstance(llm_response, str):
            try:
                json_str = re.search(r'\{.*\}', llm_response, re.DOTALL)
                if json_str:
                    llm_response = json.loads(json_str.group())
                else:
                    print("Parsing error: No valid JSON found.")
                    return None, "default_folder"
            except json.JSONDecodeError:
                print("Parsing error: JSON decode failed.")
                return None, "default_folder"

        try:
            ranked_playlist = llm_response.get("ranked_playlist", [])
            summary = llm_response.get("summary", "default_folder")

            folder_name = summary.lower().replace(" ", "_").replace("/", "_")
            return ranked_playlist, folder_name

        except Exception as e:
            print(f"General parsing error: {e}")
            return None, "default_folder"
