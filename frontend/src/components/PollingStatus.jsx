import { useEffect, useState, useCallback, useRef } from "react";

const simulatedSteps = [
  "🧠 Understanding your musical taste...",
  "🔍 Filtering perfect tracks just for you...",
  "🔌 Fetching additional song insights...",
  "📈 Ranking tracks by best fit...",
  "📊 Finalizing your personalized playlist...",
];

function PollingStatus({ jobId, onReset }) {
  const [status, setStatus] = useState("processing");
  const [playlist, setPlaylist] = useState(null);
  const [transcript, setTranscript] = useState([]);

  const executed = useRef(false);

  const fetchPlaylist = useCallback((retries = 150) => {
    fetch(`https://hhdpmxbqwg.execute-api.us-east-1.amazonaws.com/Prod/status/${jobId}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "completed" && data.playlist) {
          setStatus("completed");
          setPlaylist(data.playlist);
        } else if (retries > 0) {
          setTimeout(() => fetchPlaylist(retries - 1), 4000);
        }
      });
  }, [jobId]);

  useEffect(() => {
    if (executed.current) return;
    executed.current = true;

    simulatedSteps.forEach((step, i) => {
      setTimeout(() => {
        setTranscript((prev) => [...prev, step]);
        if (i === simulatedSteps.length - 1) fetchPlaylist();
      }, i * 800);
    });
  }, [fetchPlaylist]);

  return (
    <div className="text-center p-4">
      <div className="space-y-2 my-4 text-lg text-indigo-700 font-medium">
        {transcript.map((step, idx) => (
          <p key={idx} className="my-2 py-2 animate-pulse">
            {step}
          </p>
        ))}
      </div>

      {status === "processing" && (
        <div className="text-sm text-gray-500 mb-4">
          ⏳ This process may take up to 2 minutes. Thank you for your patience!
        </div>
      )}

      {status === "completed" && playlist && (
        <>
          <h2 className="text-2xl font-bold my-4 text-indigo-700">
            🎵 Your Personalized AI Playlist
          </h2>
          <div className="overflow-x-auto shadow-lg rounded-lg">
            <table className="w-full text-left table-auto">
              <thead className="bg-indigo-700 text-white">
                <tr>
                  <th className="px-6 py-3">Artist</th>
                  <th className="px-6 py-3">Track Name</th>
                  <th className="px-6 py-3">YouTube</th>
                </tr>
              </thead>
              <tbody>
                {playlist.map(({ artist, track, youtube_link }, i) => (
                  <tr
                    key={i}
                    className="odd:bg-gray-50 even:bg-white hover:bg-indigo-100 transition duration-300"
                  >
                    <td className="px-6 py-4 font-medium text-gray-800">
                      {artist}
                    </td>
                    <td className="px-6 py-4 text-gray-700">
                      {track}
                    </td>
                    <td className="px-6 py-4">
                      <a
                        href={youtube_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-indigo-600 hover:text-indigo-800 hover:underline transition duration-200"
                      >
                        ▶️ Play
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <button
            className="mt-6 bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-6 rounded-lg shadow-md transition duration-300 ease-in-out"
            onClick={onReset}
          >
            🔄 Create Another Playlist
          </button>
        </>
      )}
    </div>
  );
}

export default PollingStatus;
