"use client";
import { useEffect, useState, Suspense } from "react";
import { useRouter, useParams, useSearchParams } from "next/navigation";
import { ArrowLeft, Target, AlertTriangle, CheckCircle, XCircle } from "lucide-react";

interface Mistake {
  question_text: string;
  student_answer: string;
  correct_answer: string;
  explanation: string;
  feedback: any;
}

interface ExamResult {
  exam_session_id: string;
  score: number;
  total_marks: number;
  percentage: number;
  mistakes: Mistake[];
  recommendations: string[];
}

function ExamResultContent() {
  const params = useParams();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session");
  const router = useRouter();

  const [result, setResult] = useState<ExamResult | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    const fetchResult = async () => {
      const token = localStorage.getItem("token");
      try {
        const res = await fetch(`http://localhost:8000/api/exams/${params.id}/session/${sessionId}/results`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          setResult(await res.json());
        }
      } catch (e) {
        console.error(e);
      }
    };
    fetchResult();
  }, [params.id, sessionId]);

  if (!result) return <div className="p-12 text-center text-muted">Loading Analysis...</div>;

  return (
    <div className="min-h-screen bg-background p-6 md:p-12">
      <div className="max-w-4xl mx-auto">
        <button
          onClick={() => router.push('/exams')}
          className="flex items-center gap-2 text-muted hover:text-foreground mb-8 transition-colors"
        >
          <ArrowLeft size={20} /> Back to Dashboard
        </button>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-surface rounded-2xl shadow-sm border border-border p-8 flex flex-col items-center justify-center col-span-1">
            <div className="w-32 h-32 relative">
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="64" cy="64" r="56" fill="transparent" stroke="#f3f4f6" strokeWidth="12" />
                <circle 
                  cx="64" cy="64" r="56" fill="transparent" 
                  stroke={result.percentage > 75 ? "#10b981" : result.percentage > 50 ? "#f59e0b" : "#ef4444"} 
                  strokeWidth="12" 
                  strokeDasharray={`${2 * Math.PI * 56}`}
                  strokeDashoffset={`${2 * Math.PI * 56 * (1 - result.percentage / 100)}`}
                  className="transition-all duration-1000 ease-out"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold text-foreground">{result.percentage.toFixed(0)}%</span>
              </div>
            </div>
            <h3 className="text-lg font-medium text-foreground mt-6">Overall Score</h3>
            <p className="text-muted">{result.score.toFixed(1)} / {result.total_marks}</p>
          </div>

          <div className="bg-surface rounded-2xl shadow-sm border border-border p-8 col-span-2">
            <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
              <Target className="text-primary" /> Actionable Recommendations
            </h3>
            <ul className="space-y-4">
              {result.recommendations.map((rec, i) => (
                <li key={i} className="flex items-start gap-3 bg-primary-light/10 p-4 rounded-xl border border-primary/20">
                  <div className="w-6 h-6 bg-primary-light/30 text-primary rounded-full flex items-center justify-center font-bold text-sm shrink-0">
                    {i + 1}
                  </div>
                  <span className="text-foreground">{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="bg-surface rounded-2xl shadow-sm border border-border overflow-hidden">
          <div className="px-8 py-6 border-b border-border bg-muted-bg">
            <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
              <AlertTriangle className="text-warning" /> Mistakes Analysis
            </h2>
            <p className="text-sm text-muted mt-1">Review your incorrect answers to improve your weaknesses.</p>
          </div>
          
          <div className="divide-y divide-border">
            {result.mistakes.length === 0 ? (
              <div className="p-12 text-center text-muted">Perfect score! No mistakes to review.</div>
            ) : (
              result.mistakes.map((m, i) => (
                <div key={i} className="p-8">
                  <h4 className="text-lg font-medium text-foreground mb-6">{i + 1}. {m.question_text}</h4>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div className="bg-error-bg border border-error/20 rounded-xl p-5">
                      <div className="flex items-center gap-2 text-error font-semibold mb-2">
                        <XCircle size={18} /> Your Answer
                      </div>
                      <p className="text-foreground text-sm">{m.student_answer || "(Blank)"}</p>
                    </div>
                    
                    <div className="bg-success/20 border border-success/30 rounded-xl p-5">
                      <div className="flex items-center gap-2 text-success font-semibold mb-2">
                        <CheckCircle size={18} /> Correct Answer
                      </div>
                      <p className="text-foreground text-sm">{m.correct_answer}</p>
                    </div>
                  </div>

                  <div className="bg-muted-bg rounded-xl p-5 border border-border">
                    <h5 className="font-medium text-foreground mb-2">AI Feedback</h5>
                    <p className="text-foreground/80 text-sm leading-relaxed">{m.feedback.feedback}</p>
                    {m.explanation && (
                      <p className="text-foreground/80 text-sm mt-3 pt-3 border-t border-border">
                        <span className="font-medium">Explanation:</span> {m.explanation}
                      </p>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ExamResultPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-muted">Loading...</div>}>
      <ExamResultContent />
    </Suspense>
  );
}
