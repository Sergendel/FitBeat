import { useState } from "react";
import InputForm from "./components/InputForm";
import PollingStatus from "./components/PollingStatus";

function App() {
  const [jobId, setJobId] = useState(null);

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-xl mx-auto bg-white shadow-lg rounded-lg p-6">
        <h1 className="text-2xl font-bold mb-4 text-center">🎧 FitBeat: AI Music Recommender</h1>
        {!jobId ? (
          <InputForm onJobIdReceived={(id) => setJobId(id)} />
        ) : (
          <PollingStatus jobId={jobId} />
        )}
      </div>
    </div>
  );
}

export default App;
