import { useState, useCallback, useRef } from "react";
import InputForm from "./components/InputForm";

const simulatedSteps = [
  "🧠 Understanding your musical taste...",
  "🔍 Filtering perfect tracks just for you...",
  "🔌 Fetching additional song insights...",
  "📈 Ranking tracks by best fit...",
  "📊 Finalizing your personalized playlist...",
];

function App() {
  const [loading, setLoading] = useState(false);
  const [playlist, setPlaylist] = useState(null);
  const [transcript, setTranscript] = useState([]);
  const executed = useRef(false);

  const fetchPlaylist = useCallback((jobId, retries = 150) => {
    fetch(`https://hhdpmxbqwg.execute-api.us-east-1.amazonaws.com/Prod/status/${jobId}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "completed" && data.playlist) {
          setPlaylist(data.playlist);
          setLoading(false);
        } else if (retries > 0) {
          setTimeout(() => fetchPlaylist(jobId, retries - 1), 4000);
        }
      });
  }, []);

  const handleSubmit = async (desc) => {
    setLoading(true);
    setPlaylist(null);
    setTranscript([]);
    executed.current = false;

    const response = await fetch(
      "https://hhdpmxbqwg.execute-api.us-east-1.amazonaws.com/Prod/recommend",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: desc, clear_memory: true }),
      }
    );
    const data = await response.json();

    if (!executed.current) {
      executed.current = true;
      simulatedSteps.forEach((step, i) => {
        setTimeout(() => {
          setTranscript((prev) => [...prev, step]);
          if (i === simulatedSteps.length - 1) fetchPlaylist(data.job_id);
        }, i * 800);
      });
    }
  };

  const handleReset = () => {
    setPlaylist(null);
    setTranscript([]);
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 text-gray-100 p-6 font-[Poppins]">
      <div className="w-full max-w-4xl bg-gray-800 rounded-3xl shadow-2xl border border-gray-700 p-10">
        <h1 className="text-4xl font-extrabold text-indigo-300 mb-8 text-center">
          🎧 FitBeat AI Music Recommender
        </h1>

        <InputForm onSubmit={handleSubmit} loading={loading} />

        <div className="text-center my-8 space-y-2">
          {transcript.map((step, idx) => (
            <p key={idx} className="text-xl text-indigo-400 animate-pulse font-semibold my-3">
              {step}
            </p>
          ))}
        </div>

        {playlist && (
          <>
            <h2 className="text-2xl font-bold my-6 text-indigo-300 text-center">
              🎵 Your Personalized AI Playlist
            </h2>
            <div className="flex justify-center overflow-x-auto shadow-xl rounded-xl">
              <table className="min-w-full divide-y divide-gray-700 table-auto">
                <thead className="bg-indigo-600 text-white">
                  <tr>
                    <th className="px-8 py-4 text-left">Artist</th>
                    <th className="px-8 py-4 text-left">Track Name</th>
                    <th className="px-8 py-4 text-left">YouTube</th>
                  </tr>
                </thead>
                <tbody className="bg-gray-700 divide-y divide-gray-600">
                  {playlist.map(({ artist, track, youtube_link }, i) => (
                    <tr key={i} className="hover:bg-gray-600 transition duration-300">
                      <td className="px-8 py-4 font-semibold">{artist}</td>
                      <td className="px-8 py-4">{track}</td>
                      <td className="px-8 py-4">
                        <a
                          href={youtube_link}
                          target="_blank"
                          className="text-indigo-300 hover:text-indigo-100 transition"
                        >
                          ▶️ Play
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="flex justify-center">
              <button
                className="mt-8 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold py-3 px-8 rounded-xl shadow-xl transition duration-300 ease-in-out"
                onClick={handleReset}
              >
                🔄 Create Another Playlist
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
