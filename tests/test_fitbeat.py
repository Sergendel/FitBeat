import pytest
from src.user_prompt_utils import prompt_to_audio_params
from src.filtering_utils import filter_tracks_by_audio_params
import pandas as pd


@pytest.fixture
def sample_dataset():
    # explicitly simple sample data
    return pd.DataFrame({
        'track_name': ['Song A', 'Song B'],
        'artists': ['Artist A', 'Artist B'],
        'tempo': [120, 130],
        'danceability': [0.6, 0.8],
        'popularity': [50, 80]
    })

def test_prompt_to_audio_params():
    params, folder_name = prompt_to_audio_params("relaxing music")
    assert isinstance(params, dict), "params should be a dictionary"
    assert "tempo" in params, "params should include tempo"


def test_filter_tracks_by_audio_params(sample_dataset):
    params = {"tempo": [115, 125], "danceability": [0.5, 0.7]}
    filtered_tracks = filter_tracks_by_audio_params(sample_dataset, params, "test_folder")

    assert not filtered_tracks.empty, "should filter at least one track"

    # Explicitly verify that at least one track matches original criteria
    assert filtered_tracks[
               (filtered_tracks["tempo"] >= 115) &
               (filtered_tracks["tempo"] <= 125) &
               (filtered_tracks["danceability"] >= 0.5) &
               (filtered_tracks["danceability"] <= 0.7)
               ].shape[0] >= 1, "At least one track should exactly match original criteria"

