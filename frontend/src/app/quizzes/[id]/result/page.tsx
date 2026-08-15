"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function QuizResult({ params }: { params: { id: string } }) {
  const [results, setResults] = useState<any>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchResults = async () => {
      const token = localStorage.getItem("token");
      try {
        const res = await fetch(`http://localhost:8000/api/quizzes/${params.id}/results`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          setResults(await res.json());
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchResults();
  }, [params.id]);

  if (!results) return <div className="p-8">Loading results...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Quiz Results</h1>
          <div className="text-5xl font-extrabold text-blue-600 mb-4">{results.accuracy.toFixed(1)}%</div>
          <p className="text-gray-600 text-lg">You scored {results.total_score} out of {results.max_score}</p>
          <button onClick={() => router.push("/progress")} className="mt-6 bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700">View Progress</button>
        </div>

        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Detailed Breakdown</h2>
          {results.breakdown.map((item: any, idx: number) => (
            <div key={idx} className={`p-6 rounded-xl border ${item.is_correct ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
              <h3 className="font-semibold text-gray-800 mb-2">Q{idx + 1}: {item.question}</h3>
              <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                <div>
                  <span className="font-semibold text-gray-600">Your Answer: </span>
                  <span className={item.is_correct ? 'text-green-700' : 'text-red-700'}>{item.submitted_answer || "Skipped"}</span>
                </div>
                <div>
                  <span className="font-semibold text-gray-600">Correct Answer: </span>
                  <span className="text-green-700">{typeof item.correct_answer === 'string' ? item.correct_answer : JSON.stringify(item.correct_answer)}</span>
                </div>
              </div>
              {item.feedback?.feedback && (
                <div className="bg-white p-4 rounded border border-gray-100 text-gray-700 text-sm">
                  <strong>AI Feedback: </strong> {item.feedback.feedback}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
