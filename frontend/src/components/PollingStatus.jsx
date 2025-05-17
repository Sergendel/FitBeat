import { useEffect, useState } from "react";

function PollingStatus({ jobId }) {
  const [status, setStatus] = useState("processing");
  const [playlist, setPlaylist] = useState(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(
          `https://7u03tx4h0d.execute-api.us-east-1.amazonaws.com/Prod/status/${jobId}`
        );
        const data = await response.json();

        if (data.status === "completed") {
          setStatus("completed");
          setPlaylist(data.playlist);
          clearInterval(interval);
        }
      } catch (error) {
        console.error("Polling failed:", error);
      }
    }, 3000); // poll every 3 seconds

    return () => clearInterval(interval);
  }, [jobId]);

  if (status === "processing") {
    return <p className="text-center text-yellow-600">⏳ Generating your playlist...</p>;
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-green-700 mb-4">🎶 Your Playlist:</h2>
      <ul className="space-y-2">
        {playlist.map((track, index) => (
          <li key={index} className="border p-3 rounded bg-white shadow">
            <p><strong>Artist:</strong> {track.artist}</p>
            <p><strong>Track:</strong> {track.track}</p>
            <a
              href={track.youtube_link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 underline"
            >
              Watch on YouTube
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default PollingStatus;
