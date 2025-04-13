from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage

class PromptEngineer:
    def __init__(self):
        self.dataset_genres = [
            "acoustic", "afrobeat", "alt-rock", "alternative", "ambient", "anime", "black-metal",
            "bluegrass", "blues", "brazil", "breakbeat", "british", "cantopop", "chicago-house",
            "children", "chill", "classical", "club", "comedy", "country", "dance", "dancehall",
            "death-metal", "deep-house", "detroit-techno", "disco", "disney", "drum-and-bass",
            "dub", "dubstep", "edm", "electro", "electronic", "emo", "folk", "forro", "french",
            "funk", "garage", "german", "gospel", "goth", "grindcore", "groove", "grunge", "guitar",
            "happy", "hard-rock", "hardcore", "hardstyle", "heavy-metal", "hip-hop", "honky-tonk",
            "house", "idm", "indian", "indie", "indie-pop", "industrial", "iranian", "j-dance",
            "j-idol", "j-pop", "j-rock", "jazz", "k-pop", "kids", "latin", "latino", "malay",
            "mandopop", "metal", "metalcore", "minimal-techno", "mpb", "new-age", "opera", "pagode",
            "party", "piano", "pop", "pop-film", "power-pop", "progressive-house", "psych-rock",
            "punk", "punk-rock", "r-n-b", "reggae", "reggaeton", "rock", "rock-n-roll", "rockabilly",
            "romance", "sad", "salsa", "samba", "sertanejo", "show-tunes", "singer-songwriter", "ska",
            "sleep", "songwriter", "soul", "spanish", "study", "swedish", "synth-pop", "tango",
            "techno", "trance", "trip-hop", "turkish", "world-music"
        ]

        self.system_template = """
               You're a music recommendation expert.
               The user provides a general emotional or situational description.
               You must explicitly respond in JSON format containing ranges or explicit values for these parameters:

               - explicit: Explicitly boolean (true = explicit lyrics; false = no explicit lyrics; null if uncertain).
               - danceability (0.0–1.0): How suitable a track is for dancing based on tempo, rhythm stability, beat strength, and regularity.
               - energy (0.0–1.0): Intensity and activity. Energetic tracks feel fast, loud, noisy (e.g. death metal = high energy, Bach prelude = low energy).
               - loudness (-60 to 0 dB): Overall track loudness (closer to 0 is louder).
               - mode: Modality of the track explicitly (0 = minor, 1 = major, null if uncertain).
               - speechiness (0.0–1.0): Presence of spoken words (values >0.66 = mostly speech, 0.33–0.66 = rap/music mix, <0.33 = mostly music).
               - acousticness (0.0–1.0): Likelihood track is acoustic (1.0 = fully acoustic).
               - instrumentalness (0.0–1.0): Likelihood track has no vocals (1.0 = instrumental only).
               - liveness (0.0–1.0): Presence of audience (values >0.8 = live performance).
               - valence (0.0–1.0): Musical positiveness (1.0 = happy/euphoric, 0.0 = sad/angry).
               - tempo (60–200 BPM): Overall speed or pace of a track in beats per minute.
               - time_signature (3–7): Number of beats per bar (typical values: 3 to 7).
               - track_genre: Select explicitly from provided genre list:
                 {genres}

        If any parameter explicitly can't be determined, explicitly return "null".

        Additionally, explicitly include a short summary (2-4 words) capturing the user's request for folder naming.

        Explicit JSON response format:
        {{
            "numeric_ranges": {{
                "explicit": true, 
                "tempo": [min, max],
                ...
            }},
            "summary": "short summary here"
        }}
        """

    def construct_prompt(self, user_prompt):
        system_message = SystemMessage(content=self.system_template.format(genres=self.dataset_genres))
        user_message = HumanMessage(content=user_prompt)

        return ChatPromptTemplate.from_messages([system_message, user_message])
