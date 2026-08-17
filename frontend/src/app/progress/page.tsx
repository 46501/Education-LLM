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
        <div className="h-10 bg-muted-bg rounded-lg w-1/4"></div>
        <div className="h-32 bg-muted-bg rounded-2xl w-full"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="h-48 bg-muted-bg rounded-2xl"></div>
          <div className="h-48 bg-muted-bg rounded-2xl"></div>
          <div className="h-48 bg-muted-bg rounded-2xl"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 md:p-10 max-w-6xl mx-auto space-y-8 animate-in">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground flex items-center gap-2">
          <TrendingUp className="text-primary" /> Learning Analytics
        </h1>
        <p className="text-muted mt-2 text-lg">Track your progress and identify areas for improvement.</p>
      </div>
      
      {/* Recommendations */}
      <section className="bg-primary-light/10 p-6 rounded-2xl border border-primary/20 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-10 text-primary">
          <Sparkles size={120} />
        </div>
        <div className="relative z-10">
          <h2 className="text-lg font-bold text-primary mb-4 flex items-center gap-2">
            <Sparkles className="text-primary" size={20} /> AI Recommendations
          </h2>
          <ul className="space-y-3 text-foreground">
            {recommendations.length > 0 ? (
              recommendations.map((r, i) => (
                <li key={i} className="flex items-start gap-3 bg-surface/60 p-4 rounded-xl border border-primary/20 backdrop-blur-sm shadow-sm">
                  <div className="w-6 h-6 bg-primary-light/30 text-primary rounded-full flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                    {i + 1}
                  </div>
                  <span className="font-medium">{r}</span>
                </li>
              ))
            ) : (
              <li className="flex items-center gap-2 text-primary/70">
                <AlertCircle size={18} /> Keep practicing to unlock personalized insights!
              </li>
            )}
          </ul>
        </div>
      </section>

      {/* Mastery */}
      <section>
        <h2 className="text-xl font-bold text-foreground mb-6 flex items-center gap-2">
          <Target className="text-success" /> Topic Mastery
        </h2>
        {mastery.length === 0 ? (
          <div className="text-center p-12 bg-surface rounded-2xl border border-border border-dashed">
            <p className="text-muted">No mastery data available yet. Start practicing!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mastery.map((m, i) => (
              <div key={i} className="bg-surface p-6 rounded-2xl shadow-sm border border-border premium-shadow-hover transition">
                <h3 className="font-bold text-foreground text-lg mb-4 truncate">{m.topic_name}</h3>
                
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-muted font-medium">Mastery</span>
                      <span className="font-bold text-primary">{m.mastery_score.toFixed(0)}%</span>
                    </div>
                    <div className="w-full bg-muted-bg rounded-full h-2.5 overflow-hidden">
                      <div 
                        className={`h-full rounded-full ${m.mastery_score > 75 ? 'bg-success' : m.mastery_score > 40 ? 'bg-warning' : 'bg-error'}`} 
                        style={{ width: `${m.mastery_score}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t border-border">
                    <div>
                      <p className="text-xs text-muted uppercase tracking-wider font-semibold">Difficulty</p>
                      <p className="text-sm font-medium text-foreground mt-0.5">{m.current_difficulty}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-muted uppercase tracking-wider font-semibold">Accuracy</p>
                      <p className="text-sm font-medium text-foreground mt-0.5">{m.accuracy.toFixed(0)}%</p>
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
        <h2 className="text-xl font-bold text-foreground mb-6 flex items-center gap-2">
          <AlertTriangle className="text-error" /> Areas for Review
        </h2>
        
        {mistakes.length === 0 ? (
          <div className="text-center p-12 bg-surface rounded-2xl border border-border border-dashed">
            <p className="text-muted">Great job! No recent mistakes to review.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {mistakes.map((m, i) => (
              <div key={i} className="bg-surface p-6 rounded-2xl border border-error/30 shadow-sm relative overflow-hidden group">
                <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-error"></div>
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4">
                  <h4 className="font-bold text-foreground">{m.topic}</h4>
                  <span className="text-xs bg-error-bg text-error px-3 py-1 rounded-full font-semibold border border-error/20">
                    {m.error_category}
                  </span>
                </div>
                
                <p className="text-[15px] font-medium text-foreground mb-4">{m.question}</p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-muted-bg rounded-xl p-4 border border-border">
                  <div>
                    <span className="text-xs font-semibold text-muted uppercase tracking-wider block mb-1">Your Answer</span>
                    <span className="text-error line-through font-medium">{m.student_answer}</span>
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-muted uppercase tracking-wider block mb-1">Correct Answer</span>
                    <span className="text-success font-medium">{m.correct_answer}</span>
                  </div>
                </div>
                
                {m.explanation && (
                  <div className="mt-4 pt-4 border-t border-border">
                    <p className="text-sm text-foreground/80 leading-relaxed"><span className="font-semibold text-foreground">Explanation:</span> {m.explanation}</p>
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
