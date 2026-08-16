"use client";
import { useState, useEffect } from "react";
import { Target, AlertTriangle, TrendingUp, Sparkles, AlertCircle } from "lucide-react";

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

  if (loading) {
    return (
      <div className="p-6 md:p-10 max-w-6xl mx-auto space-y-8 animate-pulse">
        <div className="h-10 bg-gray-200 rounded-lg w-1/4"></div>
        <div className="h-32 bg-gray-200 rounded-2xl w-full"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="h-48 bg-gray-200 rounded-2xl"></div>
          <div className="h-48 bg-gray-200 rounded-2xl"></div>
          <div className="h-48 bg-gray-200 rounded-2xl"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 md:p-10 max-w-6xl mx-auto space-y-8 animate-in">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <TrendingUp className="text-indigo-600" /> Learning Analytics
        </h1>
        <p className="text-gray-500 mt-2 text-lg">Track your progress and identify areas for improvement.</p>
      </div>
      
      {/* Recommendations */}
      <section className="bg-indigo-50/50 p-6 rounded-2xl border border-indigo-100 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-10 text-indigo-600">
          <Sparkles size={120} />
        </div>
        <div className="relative z-10">
          <h2 className="text-lg font-bold text-indigo-900 mb-4 flex items-center gap-2">
            <Sparkles className="text-indigo-600" size={20} /> AI Recommendations
          </h2>
          <ul className="space-y-3 text-indigo-800">
            {recommendations.length > 0 ? (
              recommendations.map((r, i) => (
                <li key={i} className="flex items-start gap-3 bg-white/60 p-4 rounded-xl border border-indigo-100/50 backdrop-blur-sm shadow-sm">
                  <div className="w-6 h-6 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                    {i + 1}
                  </div>
                  <span className="font-medium">{r}</span>
                </li>
              ))
            ) : (
              <li className="flex items-center gap-2 text-indigo-600/70">
                <AlertCircle size={18} /> Keep practicing to unlock personalized insights!
              </li>
            )}
          </ul>
        </div>
      </section>

      {/* Mastery */}
      <section>
        <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <Target className="text-emerald-500" /> Topic Mastery
        </h2>
        {mastery.length === 0 ? (
          <div className="text-center p-12 bg-white rounded-2xl border border-gray-100 border-dashed">
            <p className="text-gray-500">No mastery data available yet. Start practicing!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mastery.map((m, i) => (
              <div key={i} className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 premium-shadow-hover transition">
                <h3 className="font-bold text-gray-900 text-lg mb-4 truncate">{m.topic_name}</h3>
                
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-500 font-medium">Mastery</span>
                      <span className="font-bold text-indigo-600">{m.mastery_score.toFixed(0)}%</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
                      <div 
                        className={`h-full rounded-full ${m.mastery_score > 75 ? 'bg-emerald-500' : m.mastery_score > 40 ? 'bg-amber-500' : 'bg-red-500'}`} 
                        style={{ width: `${m.mastery_score}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t border-gray-50">
                    <div>
                      <p className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Difficulty</p>
                      <p className="text-sm font-medium text-gray-800 mt-0.5">{m.current_difficulty}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Accuracy</p>
                      <p className="text-sm font-medium text-gray-800 mt-0.5">{m.accuracy.toFixed(0)}%</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Recent Mistakes */}
      <section>
        <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <AlertTriangle className="text-red-500" /> Areas for Review
        </h2>
        
        {mistakes.length === 0 ? (
          <div className="text-center p-12 bg-white rounded-2xl border border-gray-100 border-dashed">
            <p className="text-gray-500">Great job! No recent mistakes to review.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {mistakes.map((m, i) => (
              <div key={i} className="bg-white p-6 rounded-2xl border border-red-100 shadow-sm relative overflow-hidden group">
                <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-red-400"></div>
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4">
                  <h4 className="font-bold text-gray-900">{m.topic}</h4>
                  <span className="text-xs bg-red-50 text-red-700 px-3 py-1 rounded-full font-semibold border border-red-100">
                    {m.error_category}
                  </span>
                </div>
                
                <p className="text-[15px] font-medium text-gray-800 mb-4">{m.question}</p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-50 rounded-xl p-4 border border-gray-100">
                  <div>
                    <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider block mb-1">Your Answer</span>
                    <span className="text-red-600 line-through font-medium">{m.student_answer}</span>
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider block mb-1">Correct Answer</span>
                    <span className="text-emerald-600 font-medium">{m.correct_answer}</span>
                  </div>
                </div>
                
                {m.explanation && (
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <p className="text-sm text-gray-600 leading-relaxed"><span className="font-semibold text-gray-800">Explanation:</span> {m.explanation}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
