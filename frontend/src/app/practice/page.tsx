"use client";
import { useState } from "react";

export default function PracticeMode() {
  const [subject, setSubject] = useState("");
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("BEGINNER");
  const [activeQuestion, setActiveQuestion] = useState<any>(null);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault();
    await fetchNextQuestion(difficulty);
  };

  const fetchNextQuestion = async (targetDifficulty: string) => {
    setLoading(true);
    setFeedback(null);
    setAnswer("");
    const token = localStorage.getItem("token");

    try {
      const res = await fetch("http://localhost:8000/api/practice/start", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ subject, topic, difficulty: targetDifficulty })
      });
      if (!res.ok) throw new Error("Failed to load question");
      setActiveQuestion(await res.json());
    } catch (err) {
      alert("Error loading question");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = async () => {
    if (!answer) return;
    setLoading(true);
    const token = localStorage.getItem("token");

    try {
      const res = await fetch("http://localhost:8000/api/practice/answer", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ question_id: activeQuestion.id, submitted_answer: answer })
      });
      if (!res.ok) throw new Error("Failed to submit");
      const data = await res.json();
      setFeedback(data);
      setDifficulty(data.new_recommended_difficulty);
    } catch (err) {
      alert("Error submitting answer");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        {!activeQuestion ? (
          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
            <h1 className="text-2xl font-bold mb-6 text-gray-800">Adaptive Practice Mode</h1>
            <form onSubmit={handleStart} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Subject</label>
                <input required type="text" className="mt-1 block w-full p-2 border border-gray-300 rounded" value={subject} onChange={e => setSubject(e.target.value)} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Topic</label>
                <input required type="text" className="mt-1 block w-full p-2 border border-gray-300 rounded" value={topic} onChange={e => setTopic(e.target.value)} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Starting Difficulty</label>
                <select className="mt-1 block w-full p-2 border border-gray-300 rounded" value={difficulty} onChange={e => setDifficulty(e.target.value)}>
                  <option value="BEGINNER">Beginner</option>
                  <option value="EASY">Easy</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HARD">Hard</option>
                  <option value="EXPERT">Expert</option>
                </select>
              </div>
              <button type="submit" disabled={loading} className="w-full bg-blue-600 text-white p-3 rounded-lg font-semibold hover:bg-blue-700">
                {loading ? "Starting..." : "Start Practicing"}
              </button>
            </form>
          </div>
        ) : (
          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-800">Practice: {topic}</h2>
              <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded">{difficulty}</span>
            </div>

            <h3 className="text-lg font-medium text-gray-800 mb-4">{activeQuestion.text}</h3>
            
            <div className="space-y-2 mb-6">
              {activeQuestion.options?.map((opt: string, i: number) => (
                <label key={i} className={`flex items-center space-x-3 p-3 border rounded-lg cursor-pointer ${answer === opt ? 'bg-blue-50 border-blue-300' : 'hover:bg-gray-50'}`}>
                  <input type="radio" name="practice-q" value={opt} checked={answer === opt} onChange={(e) => setAnswer(e.target.value)} className="h-4 w-4 text-blue-600" disabled={!!feedback} />
                  <span className="text-gray-700">{opt}</span>
                </label>
              ))}
            </div>

            {!feedback ? (
              <button onClick={handleAnswer} disabled={!answer || loading} className="w-full bg-green-600 text-white p-3 rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50">
                {loading ? "Evaluating..." : "Check Answer"}
              </button>
            ) : (
              <div className={`p-4 rounded-lg border ${feedback.is_correct ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                <h4 className={`font-bold ${feedback.is_correct ? 'text-green-800' : 'text-red-800'}`}>
                  {feedback.is_correct ? 'Correct!' : 'Incorrect'}
                </h4>
                <p className="text-sm mt-2"><span className="font-semibold">Correct Answer:</span> {feedback.correct_answer}</p>
                {feedback.explanation && <p className="text-sm mt-1 text-gray-700 italic">{feedback.explanation}</p>}
                
                <button onClick={() => fetchNextQuestion(feedback.new_recommended_difficulty)} className="mt-4 w-full bg-blue-600 text-white p-2 rounded-lg font-semibold hover:bg-blue-700">
                  Next Question
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
