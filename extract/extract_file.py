from extract.extract_base import ExtractBase
from pandas import read_csv, to_numeric
import config
from pathlib import Path
import config

class ExtractFile(ExtractBase):

    def __init__(self):
        # set path
        script_dir = Path(__file__).resolve().parent
        dataset_path = script_dir.parent / Path(config.FILE_PATH)
        self.file_path = dataset_path

    def load_data(self):
        # Load dataset and ensure 'tempo' is numeric
        df = read_csv(self.file_path)
        df['tempo'] = to_numeric(df['tempo'], errors='coerce')
        df.dropna(subset=['tempo'], inplace=True)  # remove invalid entries if any
        return df

if __name__ == "__main__":

    # set extractor
    extractor = ExtractFile(config.FILE_PATH)

    # extract
    data = extractor.load_data()
    print(data.head())

    # Show basic dataset info
    print(data.head())
    print(data.info())

    # Check BPM distribution quickly
    print(data['tempo'].describe())

    # Check genres quickly (optional)
    print(data['track_genre'].value_counts().head(10))
