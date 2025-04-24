from corpus.embeddings.semantic_retrieval import get_or_create_song_embedding
from llm_executor import LLMExecutor
from output_parser import OutputParser
from prompt_engineer import PromptEngineer
import pandas as pd

class RAGSemanticRefiner:
    def __init__(self):
        self.llm_executor = LLMExecutor()
        self.parser = OutputParser()
        self.prompt_engineer = PromptEngineer()

    def retrieve_semantic_context(self, tracks):
        """
        Retrieves semantic context explicitly for each track.
        """
        semantic_contexts = []
        for idx, track in tracks.iterrows():
            artist = track['artists'].split(';')[0].strip()
            title = track['track_name']

            print(f"\nRetrieving semantic context for: {artist} - {title}")

            song_text = get_or_create_song_embedding(artist, title)

            if song_text:
                #print(f"Semantic context retrieved for '{title}'.")
                semantic_contexts.append({
                    'artist': artist,
                    'title': title,
                    'context': song_text
                })
            else:
                print(f"No semantic context found for '{title}'. Proceeding without semantic context.")
                semantic_contexts.append({
                    'artist': artist,
                    'title': title,
                    'context': None
                })

        return semantic_contexts

    def reorder_tracks_by_semantic_ranking(self, original_tracks, ranked_playlist):
        """
        Reorders tracks explicitly based on semantic ranking.
        """
        ranked_df = pd.DataFrame(ranked_playlist)
        ranked_df['title'] = ranked_df['title'].str.lower().str.strip()
        ranked_df['artist'] = ranked_df['artist'].str.lower().str.strip()

        original_tracks['normalized_title'] = original_tracks['track_name'].str.lower().str.strip()
        original_tracks['normalized_artist'] = original_tracks['artists'].str.lower().str.split(';').str[0].str.strip()

        filtered_df = pd.merge(ranked_df, original_tracks,
                               left_on=['title', 'artist'],
                               right_on=['normalized_title', 'normalized_artist'],
                               how='inner').drop_duplicates(subset=['track_name', 'artists'])

        missing_tracks = set(ranked_df['title']) - set(filtered_df['normalized_title'])
        if missing_tracks:
            print(f"Missing tracks after merge: {missing_tracks}")

        return filtered_df

    def refine_tracks_with_rag(self, user_prompt, tracks, folder_name):
        """
    Refines and ranks a list of tracks  using RAG based on semantic context (lyrics and descriptions).

    This method:
        1. Retrieves semantic context (lyrics, descriptions) for each track from the Genius API or local corpus.
        2. Constructs a refined prompt with the retrieved context and the user's original request.
        3. Invokes an LLM to rank the provided tracks based on their semantic relevance to the user's prompt.
        4. Reorders the original DataFrame of tracks according to the semantic ranking provided by the LLM.

    Parameters:
        user_prompt (str):
            The original user's emotional or situational description.

        tracks (pd.DataFrame):
            DataFrame of tracks previously filtered numerically, containing at least:
                - 'track_name': The name of each track.
                - 'artists': The artists associated with each track.
                - Additional numeric audio features and metadata.

        folder_name (str):
            The name of the folder used to store track files and outputs.
            May be updated if the semantic refinement suggests a more suitable name.

    Returns:
        tuple:
            - refined_tracks (pd.DataFrame): Tracks reordered according to semantic relevance.
            - refined_folder_name (str): Potentially updated folder name reflecting semantic refinement.
                                         Defaults to the original `folder_name` if no change is suggested.

    Error Handling Explicitly:
        - If semantic context retrieval fails for certain tracks, the method logs these issues but continues refinement.
        - Ensures robustness against missing or incomplete LLM responses, proceeding with original data if refinement fails.

    """
        print("\nRetrieving semantic context (lyrics and descriptions) for candidate tracks...\n"
              "Context will be loaded from the local corpus if available; otherwise, it will be retrieved dynamically from the Genius API.")

        refined_tracks_context = self.retrieve_semantic_context(tracks)
        print(f"\n\n Semantic context retrieved.")
        print("\n\n\nConstructing refined prompt — combining user request and retrieved semantic contexts...")
        refined_prompt = self.prompt_engineer.construct_refined_prompt(user_prompt, refined_tracks_context)
        messages = refined_prompt.format_messages(user_prompt=user_prompt)

        print("******   LLM is ranking candidate tracks based on semantic relevance to user prompt...")
        ranked_playlist, refined_folder_name = self.parser.parse_ranked_playlist(
            self.llm_executor.execute(messages))

        if ranked_playlist:
            tracks = self.reorder_tracks_by_semantic_ranking(tracks, ranked_playlist)
            folder_name = refined_folder_name or folder_name
            print("\nSemantic refinement (RAG) completed successfully!")
            print("\nRanked Playlist:")
            for track_number, (_, row) in enumerate(tracks.iterrows(), start=1):
                print(f"{track_number}. {row['track_name']} by {row['artists']}")
        else:
            print("Refinement failed; proceeding with original tracks.")

        return tracks, folder_name
