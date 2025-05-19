import { useState } from "react";

function InputForm({ onSubmit, loading }) {
  const [description, setDescription] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(description);
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col items-center gap-4">
      <input
        type="text"
        placeholder="Describe your musical mood or preference..."
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        required
        disabled={loading}
        className="w-full px-6 py-4 rounded-xl border-2 border-gray-500 shadow-xl text-lg bg-gray-700 text-gray-100 transition duration-200 focus:outline-none focus:border-indigo-500"
      />
      <button
        type="submit"
        className={`w-full md:w-auto bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white py-3 px-8 rounded-xl shadow-lg font-semibold transition duration-300 ${
          loading ? "opacity-60 cursor-not-allowed" : ""
        }`}
        disabled={loading}
      >
        {loading ? "Generating Playlist..." : "🎶 Generate Playlist"}
      </button>
    </form>
  );
}

export default InputForm;
