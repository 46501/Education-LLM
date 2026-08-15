"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function TakeQuiz({ params }: { params: { id: string } }) {
  const [quiz, setQuiz] = useState<any>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchQuiz = async () => {
      const token = localStorage.getItem("token");
      try {
        const res = await fetch(`http://localhost:8000/api/quizzes/${params.id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (!res.ok) throw new Error("Failed to load quiz");
        const data = await res.json();
        setQuiz(data);
      } catch (err) {
        alert("Failed to load quiz");
      } finally {
        setLoading(false);
      }
    };
    fetchQuiz();
  }, [params.id]);

  const handleSubmit = async () => {
    const token = localStorage.getItem("token");
    const payload = {
      answers: Object.entries(answers).map(([qId, ans]) => ({ question_id: qId, submitted_answer: ans }))
    };

    try {
      const res = await fetch(`http://localhost:8000/api/quizzes/${params.id}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        router.push(`/quizzes/${params.id}/result`);
      } else {
        alert("Failed to submit");
      }
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (!quiz) return <div className="p-8">Quiz not found.</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-6 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">{quiz.title}</h1>
          <button onClick={handleSubmit} className="bg-green-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-green-700">Submit Quiz</button>
        </div>

        <div className="space-y-6">
          {quiz.questions.map((q: any, idx: number) => (
            <div key={q.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <h3 className="text-lg font-medium text-gray-800 mb-4">{idx + 1}. {q.text}</h3>
              {q.type === "MCQ" ? (
                <div className="space-y-2">
                  {q.options?.map((opt: string, i: number) => (
                    <label key={i} className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                      <input 
                        type="radio" 
                        name={`q-${q.id}`} 
                        value={opt} 
                        checked={answers[q.id] === opt}
                        onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
                        className="h-4 w-4 text-blue-600"
                      />
                      <span className="text-gray-700">{opt}</span>
                    </label>
                  ))}
                </div>
              ) : (
                <textarea 
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={4}
                  placeholder="Type your answer here..."
                  value={answers[q.id] || ""}
                  onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
                ></textarea>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
