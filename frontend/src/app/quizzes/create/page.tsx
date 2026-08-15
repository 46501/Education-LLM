"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function CreateQuiz() {
  const [subject, setSubject] = useState("");
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("MEDIUM");
  const [numQuestions, setNumQuestions] = useState(5);
  const [useRag, setUseRag] = useState(false);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const token = localStorage.getItem("token");

    try {
      const res = await fetch("http://localhost:8000/api/quizzes/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          title: `${topic} Quiz`,
          subject,
          topic,
          difficulty,
          number_of_questions: numQuestions,
          use_rag: useRag
        })
      });

      if (!res.ok) throw new Error("Failed to generate quiz");
      const data = await res.json();
      router.push(`/quizzes/${data.quiz_id}`);
    } catch (err) {
      alert(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto bg-white p-8 rounded-xl shadow-sm border border-gray-200">
        <h1 className="text-2xl font-bold mb-6 text-gray-800">Generate a Quiz</h1>
        <form onSubmit={handleGenerate} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Subject</label>
            <input required type="text" className="mt-1 block w-full p-2 border border-gray-300 rounded" value={subject} onChange={e => setSubject(e.target.value)} placeholder="e.g., Computer Science" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Topic</label>
            <input required type="text" className="mt-1 block w-full p-2 border border-gray-300 rounded" value={topic} onChange={e => setTopic(e.target.value)} placeholder="e.g., Binary Trees" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Difficulty</label>
            <select className="mt-1 block w-full p-2 border border-gray-300 rounded" value={difficulty} onChange={e => setDifficulty(e.target.value)}>
              <option value="BEGINNER">Beginner</option>
              <option value="EASY">Easy</option>
              <option value="MEDIUM">Medium</option>
              <option value="HARD">Hard</option>
              <option value="EXPERT">Expert</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Number of Questions</label>
            <input type="number" min="1" max="20" className="mt-1 block w-full p-2 border border-gray-300 rounded" value={numQuestions} onChange={e => setNumQuestions(parseInt(e.target.value))} />
          </div>
          <div className="flex items-center">
            <input type="checkbox" id="rag" className="mr-2" checked={useRag} onChange={e => setUseRag(e.target.checked)} />
            <label htmlFor="rag" className="text-sm font-medium text-gray-700">Base questions on my uploaded documents</label>
          </div>
          <button type="submit" disabled={loading} className="w-full bg-blue-600 text-white p-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50">
            {loading ? "Generating (this may take a minute)..." : "Generate Quiz"}
          </button>
        </form>
      </div>
    </div>
  );
}
