import { useState } from "react";

function InputForm({ onJobIdReceived }) {
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch("https://7u03tx4h0d.execute-api.us-east-1.amazonaws.com/Prod/recommend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          description: description,
          clear_memory: true,
        }),
      });

      const data = await response.json();
      onJobIdReceived(data.job_id); // pass job_id to parent
    } catch (error) {
      console.error("Error submitting description:", error);
      alert("Something went wrong!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input
        type="text"
        className="w-full p-2 border border-gray-300 rounded"
        placeholder="Describe the music you're looking for..."
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        required
      />
      <button
        type="submit"
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        disabled={loading}
      >
        {loading ? "Submitting..." : "Get Playlist"}
      </button>
    </form>
  );
}

export default InputForm;
