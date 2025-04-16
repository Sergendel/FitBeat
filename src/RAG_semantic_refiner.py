from corpus.embeddings.semantic_retrieval import retrieve_or_add_song
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

            print(f"Retrieving semantic context explicitly for: {artist} - {title}")

            song_text = retrieve_or_add_song(artist, title)

            if song_text:
                print(f"✅ Semantic context explicitly retrieved for '{title}'.")
                semantic_contexts.append({
                    'artist': artist,
                    'title': title,
                    'context': song_text
                })
            else:
                print(f"⚠️ No semantic context explicitly found for '{title}'. Proceeding without semantic context.")
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
        Main method explicitly for semantic refinement using RAG.
        """
        refined_tracks_context = self.retrieve_semantic_context(tracks)
        refined_prompt = self.prompt_engineer.construct_refined_prompt(user_prompt, refined_tracks_context)
        messages = refined_prompt.format_messages(user_prompt=user_prompt)

        ranked_playlist, refined_folder_name = self.parser.parse_ranked_playlist(
            self.llm_executor.execute(messages))

        if ranked_playlist:
            tracks = self.reorder_tracks_by_semantic_ranking(tracks, ranked_playlist)
            folder_name = refined_folder_name or folder_name
            print("✅ Refinement (RAG) explicitly completed successfully!")
        else:
            print("⚠️ Refinement explicitly failed; proceeding with original tracks.")

        return tracks, folder_name
