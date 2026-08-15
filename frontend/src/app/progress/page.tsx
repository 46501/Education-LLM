"use client";
import { useState, useEffect } from "react";

export default function ProgressDashboard() {
  const [mastery, setMastery] = useState<any[]>([]);
  const [mistakes, setMistakes] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      const token = localStorage.getItem("token");
      try {
        const headers = { Authorization: `Bearer ${token}` };
        const [mastRes, mistRes, recRes] = await Promise.all([
          fetch("http://localhost:8000/api/analytics/mastery", { headers }),
          fetch("http://localhost:8000/api/analytics/mistakes", { headers }),
          fetch("http://localhost:8000/api/analytics/recommendations", { headers })
        ]);
        
        if (mastRes.ok) setMastery((await mastRes.json()).mastery);
        if (mistRes.ok) setMistakes((await mistRes.json()).mistakes);
        if (recRes.ok) setRecommendations((await recRes.json()).recommendations);
      } catch (err) {
        console.error("Failed to load analytics");
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) return <div className="p-8">Loading dashboard...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <h1 className="text-3xl font-bold text-gray-800">Learning Dashboard</h1>
        
        {/* Recommendations */}
        <section className="bg-white p-6 rounded-xl shadow-sm border border-blue-200">
          <h2 className="text-xl font-bold text-blue-800 mb-4">Recommended for You</h2>
          <ul className="list-disc pl-5 space-y-2 text-gray-700">
            {recommendations.length > 0 ? (
              recommendations.map((r, i) => <li key={i}>{r}</li>)
            ) : (
              <li>Keep practicing to unlock insights!</li>
            )}
          </ul>
        </section>

        {/* Mastery */}
        <section>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Topic Mastery</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mastery.map((m, i) => (
              <div key={i} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h3 className="font-bold text-lg mb-2">{m.topic_name}</h3>
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Score: {m.mastery_score.toFixed(1)}/100</span>
                  <span className="font-semibold text-blue-600">{m.current_difficulty}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${m.mastery_score}%` }}></div>
                </div>
                <p className="text-xs text-gray-500 mt-3">Accuracy: {m.accuracy.toFixed(1)}% | Attempts: {m.questions_attempted}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Recent Mistakes */}
        <section>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Recent Mistakes to Review</h2>
          <div className="space-y-4">
            {mistakes.map((m, i) => (
              <div key={i} className="bg-red-50 p-4 rounded-lg border border-red-200">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-bold text-red-800">{m.topic}</h4>
                  <span className="text-xs bg-red-200 text-red-800 px-2 py-1 rounded-full font-semibold">{m.error_category}</span>
                </div>
                <p className="text-sm font-medium text-gray-800 mb-2">{m.question}</p>
                <div className="text-sm">
                  <span className="text-red-600 line-through mr-3">{m.student_answer}</span>
                  <span className="text-green-700 font-semibold">{m.correct_answer}</span>
                </div>
                {m.explanation && <p className="text-xs text-gray-600 mt-2 italic">{m.explanation}</p>}
              </div>
            ))}
          </div>
        </section>

      </div>
    </div>
  );
}
