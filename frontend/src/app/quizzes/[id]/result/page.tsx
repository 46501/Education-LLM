"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Award, CheckCircle, ChevronLeft, Lightbulb, Target, TrendingUp, XCircle, FileText, Loader2 } from "lucide-react";

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

  if (!results) {
    return (
      <div className="flex flex-col items-center justify-center h-[calc(100vh-4rem)]">
        <Loader2 size={40} className="text-indigo-600 animate-spin mb-4" />
        <p className="text-gray-500 font-medium">Analyzing your results...</p>
      </div>
    );
  }

  const accuracy = results.accuracy || 0;
  let grade = "bg-gray-100 text-gray-800";
  let gradeMessage = "Good effort!";
  if (accuracy >= 90) { grade = "bg-emerald-100 text-emerald-800"; gradeMessage = "Exceptional!"; }
  else if (accuracy >= 75) { grade = "bg-indigo-100 text-indigo-800"; gradeMessage = "Great job!"; }
  else if (accuracy >= 60) { grade = "bg-amber-100 text-amber-800"; gradeMessage = "Almost there."; }
  else { grade = "bg-red-100 text-red-800"; gradeMessage = "Needs review."; }

  return (
    <div className="p-6 md:p-10 max-w-5xl mx-auto min-h-[calc(100vh-4rem)] animate-in">
      
      {/* Overview Card */}
      <div className="bg-white rounded-3xl border border-gray-100 p-8 md:p-12 text-center relative overflow-hidden mb-12 premium-shadow">
        <div className="absolute top-0 right-0 p-8 opacity-5 text-indigo-600">
          <Award size={200} />
        </div>
        <div className="relative z-10 flex flex-col items-center">
          <span className={`px-4 py-1.5 rounded-full text-sm font-bold uppercase tracking-wider mb-6 ${grade}`}>
            {gradeMessage}
          </span>
          <h1 className="text-3xl md:text-4xl font-extrabold text-gray-900 mb-2">Quiz Results</h1>
          
          <div className="relative my-8">
            <svg className="w-40 h-40 transform -rotate-90">
              <circle cx="80" cy="80" r="70" stroke="currentColor" strokeWidth="12" fill="transparent" className="text-gray-100" />
              <circle cx="80" cy="80" r="70" stroke="currentColor" strokeWidth="12" fill="transparent" strokeDasharray="440" strokeDashoffset={440 - (440 * accuracy) / 100} className="text-indigo-600 transition-all duration-1000 ease-out" />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center flex-col">
              <span className="text-4xl font-extrabold text-gray-900">{accuracy.toFixed(0)}%</span>
            </div>
          </div>
          
          <p className="text-gray-600 text-lg font-medium mb-8">
            You scored <span className="text-gray-900 font-bold">{results.total_score}</span> out of <span className="text-gray-900 font-bold">{results.max_score}</span> points.
          </p>

          <div className="flex gap-4">
            <button onClick={() => router.push("/progress")} className="flex items-center gap-2 bg-indigo-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-indigo-700 transition shadow-sm">
              <TrendingUp size={18} /> View Progress
            </button>
            <button onClick={() => router.push("/dashboard")} className="flex items-center gap-2 bg-white border border-gray-200 text-gray-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-50 transition">
              <ChevronLeft size={18} /> Back to Dashboard
            </button>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <FileText className="text-indigo-600" /> Detailed Breakdown
        </h2>
        
        {results.breakdown.map((item: any, idx: number) => (
          <div key={idx} className={`p-6 md:p-8 rounded-2xl border ${item.is_correct ? 'bg-emerald-50/30 border-emerald-100' : 'bg-red-50/30 border-red-100'} premium-shadow-hover transition`}>
            
            <div className="flex gap-4 mb-6">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${item.is_correct ? 'bg-emerald-100 text-emerald-600' : 'bg-red-100 text-red-600'}`}>
                {item.is_correct ? <CheckCircle size={18} /> : <XCircle size={18} />}
              </div>
              <h3 className="text-lg font-medium text-gray-800 leading-relaxed pt-1">
                <span className="font-bold mr-2 text-gray-400">Q{idx + 1}.</span> {item.question}
              </h3>
            </div>
            
            <div className="pl-12">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-white/60 rounded-xl p-5 border border-gray-100 mb-4">
                <div>
                  <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider block mb-1">Your Answer</span>
                  <span className={`font-medium ${item.is_correct ? 'text-emerald-700' : 'text-red-700 line-through'}`}>{item.submitted_answer || "Skipped"}</span>
                </div>
                {!item.is_correct && (
                  <div>
                    <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider block mb-1">Correct Answer</span>
                    <span className="text-emerald-700 font-medium">{typeof item.correct_answer === 'string' ? item.correct_answer : JSON.stringify(item.correct_answer)}</span>
                  </div>
                )}
              </div>
              
              {item.feedback?.feedback && (
                <div className="bg-indigo-50/50 p-5 rounded-xl border border-indigo-100 flex gap-3">
                  <Lightbulb className="text-indigo-500 shrink-0 mt-0.5" size={20} />
                  <div>
                    <strong className="text-indigo-900 block text-sm mb-1">AI Tutor Insight</strong>
                    <p className="text-indigo-800/80 text-sm leading-relaxed">{item.feedback.feedback}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
