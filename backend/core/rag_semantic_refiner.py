import pandas as pd

from backend import config
from backend.core.llm_executor import LLMExecutor
from backend.core.output_parser import OutputParser
from backend.core.prompt_engineer import PromptEngineer
from backend.corpus.embeddings.semantic_retrieval import (
    embed_user_prompt,
    get_or_create_song_embedding,
    set_collection,
)


class RAGSemanticRefiner:
    def __init__(self):
        self.llm_executor = LLMExecutor()
        self.parser = OutputParser()
        self.prompt_engineer = PromptEngineer()

        # Set ChromaDB collection
        self.collection = set_collection()

        self.embed_user_prompt = embed_user_prompt

    def retrieve_semantic_context(self, tracks):
        """
        Retrieves semantic context for each track.
        """
        verbose = config.VERBOSE
        semantic_contexts = []
        for _, track in tracks.iterrows():
            artist = track["artists"].split(";")[0].strip()
            track_name = track["track_name"]

            if verbose:
                print(f"\nRetrieving semantic context for: {artist} - {track_name}")

            song_text = get_or_create_song_embedding(
                artist, track_name, self.collection
            )

            if song_text:
                # print(f"Semantic context retrieved for '{track_name}'.")
                semantic_contexts.append(
                    {"artist": artist, "track_name": track_name, "context": song_text}
                )
            else:
                if verbose:
                    print(
                        f"No semantic context found for '{track_name}'. "
                        f"Proceeding without semantic context."
                    )
                semantic_contexts.append(
                    {"artist": artist, "track_name": track_name, "context": None}
                )

        return semantic_contexts

    def reorder_tracks_by_semantic_ranking(self, original_tracks, ranked_playlist):

        verbose = config.VERBOSE

        ranked_df = pd.DataFrame(ranked_playlist)

        # Normalize strings to ensure accurate matching
        ranked_df["track_name"] = ranked_df["track_name"].str.lower().str.strip()
        ranked_df["artist"] = ranked_df["artist"].str.lower().str.strip()

        original_tracks["normalized_track_name"] = (
            original_tracks["track_name"].str.lower().str.strip()
        )
        original_tracks["normalized_artist"] = (
            original_tracks["artists"].str.lower().str.split(";").str[0].str.strip()
        )

        # Reorder by explicitly iterating through ranked_df
        ordered_rows = []
        missing_tracks = []

        for _, ranked_row in ranked_df.iterrows():
            mask = (
                original_tracks["normalized_track_name"] == ranked_row["track_name"]
            ) & (original_tracks["normalized_artist"] == ranked_row["artist"])
            match = original_tracks[mask]

            if not match.empty:
                ordered_rows.append(match.iloc[0])
            else:
                missing_tracks.append((ranked_row["artist"], ranked_row["track_name"]))

        # Combine ordered rows into final DataFrame
        ordered_df = pd.DataFrame(ordered_rows).reset_index(drop=True)

        if verbose and missing_tracks:
            print(f"Missing tracks: {missing_tracks}")

        # Drop temporary normalization columns
        ordered_df = ordered_df.drop(
            columns=["normalized_track_name", "normalized_artist"], errors="ignore"
        )

        return ordered_df

    def refine_tracks_with_rag(
        self, user_prompt, tracks, folder_name, embedding_top_k=None
    ):
        """
        Refines and ranks a list of tracks  using RAG based on semantic context
        (lyrics and descriptions).

        This method:
            1. Retrieves semantic context (lyrics, descriptions) for each track from
               the Genius API or local corpus.
            2. Constructs a refined prompt with the retrieved context and the user's
                original request.
            3. Invokes an LLM to rank the provided tracks based on semantic relevance
                to the user's prompt.
            4. Reorders the original DataFrame of tracks according to semantic ranking
               provided by the LLM.

        Parameters:
            user_prompt (str):
                The original user's emotional or situational description.

            tracks (pd.DataFrame):
                DataFrame of tracks previously filtered numerically, containing :
                    - 'track_name': The name of each track.
                    - 'artists': The artists associated with each track.
                    - Additional numeric audio features and metadata.

            folder_name (str):
                The name of the folder used to store track files and outputs.
                May be updated if semantic refinement suggests a more suitable name.

        Returns:
            tuple:
                - refined_tracks (pd.DataFrame):
                        Tracks reordered according to semantic relevance.
                - refined_folder_name (str):
                        Potentially updated folder name reflecting semantic refinement.
                        Defaults to the original `folder_name`
                        if no change is suggested.

        Error Handling Explicitly:
            - If semantic context retrieval fails for certain tracks,
              the method logs these issues but continues refinement.
            - Ensures robustness against missing or incomplete LLM responses,
               proceeding with original data if refinement fails.

        """
        verbose = config.VERBOSE

        if verbose:
            print(
                "\nRetrieving semantic context (lyrics and descriptions) "
                "for candidate tracks...\n"
                "Context will be loaded from the local corpus if available; otherwise,"
                " it will be retrieved dynamically from the Genius API."
            )

        refined_tracks_context = self.retrieve_semantic_context(tracks)
        if verbose:
            print("\n\n Semantic context retrieved.")
        if verbose:
            print(
                "\n\n\nConstructing refined prompt — combining user request and"
                " retrieved semantic contexts..."
            )
        refined_prompt = self.prompt_engineer.construct_refined_prompt(
            user_prompt, refined_tracks_context
        )
        messages = refined_prompt.format_messages(user_prompt=user_prompt)

        print(
            "******   LLM is ranking candidate tracks based on semantic"
            " relevance to user prompt..."
        )
        ranked_playlist, refined_folder_name = self.parser.parse_ranked_playlist(
            self.llm_executor.execute(messages)
        )

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

    def rank_tracks_by_embedding_similarity(
        self, user_prompt, tracks, top_k=50, verbose=False
    ):

        # Step 1 Ensure embeddings exist
        for artist, track_name in zip(tracks["artists"], tracks["track_name"]):
            get_or_create_song_embedding(artist, track_name, self.collection)

        # Step 2 Embed user prompt explicitly
        user_embedding = self.embed_user_prompt(user_prompt)

        # Step 3  Construct ChromaDB metadata filter
        track_metadata_conditions = [
            {
                "$and": [
                    {"artists": {"$eq": artist}},
                    {"track_name": {"$eq": track_name}},
                ]
            }
            for artist, track_name in zip(tracks["artists"], tracks["track_name"])
        ]

        # Step 4 explicitly: Perform ChromaDB semantic embedding search
        results = self.collection.query(
            query_embeddings=[user_embedding],
            n_results=min(top_k, len(track_metadata_conditions)),
            where={"$or": track_metadata_conditions},
            include=["metadatas", "distances"],
        )

        retrieved_metadatas = results["metadatas"][0]
        retrieved_distances = results["distances"][0]

        if not retrieved_metadatas:
            if verbose:
                print("No tracks matched the metadata conditions.")
            return pd.DataFrame([])

        # Step 5 : Build DataFrame from retrieved metadata
        embedding_df = pd.DataFrame(retrieved_metadatas)
        embedding_df["distance"] = retrieved_distances

        # Step 6 : Merge with numeric-filtered tracks
        final_df = embedding_df.merge(tracks, on=["artists", "track_name"], how="left")

        # Step 7: Sort final DataFrame by semantic distance
        final_df.sort_values("distance", inplace=True)
        final_df.reset_index(drop=True, inplace=True)

        # limit to top_k tracks
        final_df = final_df.head(top_k)

        return final_df

    def hybrid_refine_tracks(
        self,
        user_prompt,
        tracks,
        folder_name="hybrid_recommendations",
        embedding_top_k=10,
    ):

        print(
            "\nRanking tracks using the hybrid method:"
            f"\n   1. Embedding Ranking: Rank candidate tracks based on embedding "
            f"similarity to the user's prompt embedding and select "
            f"the top {embedding_top_k} tracks."
            "\n   2. Refine the ranking of selected tracks using LLM-based "
            "semantic relevance (RAG) to the user's prompt.\n"
        )

        # Step 1: rank_tracks_by_embedding_similarity
        print("----- Performing Embedding Ranking...  -------")
        embedding_filtered_tracks = self.rank_tracks_by_embedding_similarity(
            user_prompt, tracks, top_k=embedding_top_k
        )
        print("----- Performing LLM-based semantic relevance ranking ----- ...\n\n")
        # Step 2: Perform final LLM ranking (existing function)
        final_ranked_tracks, folder_name = self.refine_tracks_with_rag(
            user_prompt, embedding_filtered_tracks, folder_name=folder_name
        )

        return final_ranked_tracks, folder_name
