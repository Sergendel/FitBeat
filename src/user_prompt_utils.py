import pandas as pd
from src.prompt_engineer import PromptEngineer
from src.llm_executor import LLMExecutor
from src.output_parser import OutputParser

def prompt_to_audio_params(user_prompt):
    """
        Converts a user's emotional/situational prompt explicitly into numeric audio parameters using an LLM.

        :param user_prompt: user prompt (str).
        :return: (params: dict, folder_name: str)
    """
    llm_executor = LLMExecutor()
    parser = OutputParser()
    prompt_engineer = PromptEngineer()
    print(f'\nLLM is analyzing the user prompt: "{user_prompt}"\n'
          f'to derive numeric audio parameters.\n'
          f'Additionally, the LLM suggests a suitable folder name for the playlist.\n')
    prompt_template = prompt_engineer.construct_prompt(user_prompt)
    messages = prompt_template.format_messages(user_prompt=user_prompt)
    llm_response = llm_executor.execute(messages)

    if llm_response is None:
        raise ValueError("LLM returned None or invalid response during analyze step.")

    params, folder_name = parser.parse_response(llm_response)



    if not params or not folder_name:
        raise ValueError("Missing params or folder_name from LLM response.")
    else:
        print("Resulting ranges of numerical audio parameters:")
        for key, value in params.items():
            print(f"  - {key.capitalize()}: {value}")
        print(
            f"\n****   The tracks will be stored in the folder '{folder_name}'   *****.\n")
    return params, folder_name


def parse_user_prompt_to_dataframe(user_prompt):
    """
    Parses user-provided tracks explicitly from a textual prompt into a structured DataFrame.

    Parameters:
        user_prompt (str): Text input explicitly provided by the user containing tracks.

    Returns:
        pd.DataFrame: DataFrame explicitly structured with columns like:
            - artists
            - track_name
            - popularity, tempo, explicit, danceability, etc. (set explicitly to None placeholders)
    """
    lines = user_prompt.strip().split("\n")
    tracks = []

    for line in lines:
        line = line.strip()
        if line.startswith("-"):
            line_content = line[1:].strip()
            if " - " in line_content:
                artist, track_name = line_content.split(" - ", 1)
                tracks.append({
                    'artists': artist.strip(),
                    'track_name': track_name.strip(),
                    'popularity': None,
                    'tempo': None,
                    'explicit': None,
                    'danceability': None,
                    'energy': None,
                    'loudness': None,
                    'mode': None,
                    'speechiness': None,
                    'acousticness': None,
                    'instrumentalness': None,
                    'liveness': None,
                    'valence': None,
                    'time_signature': None,
                    'track_genre': None
                })

    if not tracks:
        print("No provided tracks found in user prompt.")
    else:
        print(f"Found {len(tracks)} explicitly user-provided tracks.")

    return pd.DataFrame(tracks)



