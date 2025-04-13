import re

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
