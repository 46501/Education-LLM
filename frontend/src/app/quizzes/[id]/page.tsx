"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { CheckCircle2, ChevronRight, FileQuestion, HelpCircle, Loader2 } from "lucide-react";

export default function TakeQuiz({ params }: { params: { id: string } }) {
  const [quiz, setQuiz] = useState<any>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
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
    setSubmitting(true);
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
        setSubmitting(false);
      }
    } catch (err) {
      console.error(err);
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[calc(100vh-4rem)]">
        <Loader2 size={40} className="text-primary animate-spin mb-4" />
        <p className="text-muted font-medium">Loading your quiz...</p>
      </div>
    );
  }
  
  if (!quiz) return <div className="p-8 text-center text-muted">Quiz not found.</div>;

  const answeredCount = Object.keys(answers).length;
  const totalQuestions = quiz.questions.length;
  const progress = (answeredCount / totalQuestions) * 100;
  const isComplete = answeredCount === totalQuestions;

  return (
    <div className="p-6 md:p-10 max-w-4xl mx-auto min-h-[calc(100vh-4rem)] animate-in">
      
      {/* Sticky Header */}
      <div className="sticky top-0 z-10 bg-background/90 backdrop-blur-md pb-6 pt-2 mb-6">
        <div className="bg-surface p-6 rounded-2xl shadow-sm border border-border flex flex-col md:flex-row md:items-center justify-between gap-6 premium-shadow">
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-foreground mb-2">{quiz.title}</h1>
            <div className="flex items-center gap-4 text-sm font-medium">
              <span className="bg-primary-light/30 text-primary px-3 py-1 rounded-full">{quiz.subject}</span>
              <span className="text-muted flex items-center gap-1.5"><FileQuestion size={16} /> {totalQuestions} Questions</span>
            </div>
          </div>
          
          <div className="flex flex-col items-end gap-3 min-w-[200px]">
            <div className="w-full flex justify-between text-sm mb-1">
              <span className="text-muted font-medium">Progress</span>
              <span className="font-bold text-primary">{answeredCount} of {totalQuestions}</span>
            </div>
            <div className="w-full bg-muted-bg rounded-full h-2">
              <div 
                className="bg-primary h-2 rounded-full transition-all duration-500" 
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Quiz Questions */}
      <div className="space-y-8">
        {quiz.questions.map((q: any, idx: number) => {
          const isAnswered = !!answers[q.id];
          return (
            <div key={q.id} className={`bg-surface p-6 md:p-8 rounded-2xl border transition-all ${isAnswered ? 'border-primary/50' : 'border-border'} premium-shadow-hover`}>
              <div className="flex gap-4 mb-6">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm shrink-0 ${isAnswered ? 'bg-primary text-white' : 'bg-muted-bg text-muted'}`}>
                  {idx + 1}
                </div>
                <h3 className="text-lg font-medium text-foreground leading-relaxed pt-1">{q.text}</h3>
              </div>
              
              <div className="pl-12">
                {q.type === "MCQ" ? (
                  <div className="space-y-3">
                    {q.options?.map((opt: string, i: number) => {
                      const isSelected = answers[q.id] === opt;
                      return (
                        <label 
                          key={i} 
                          className={`flex items-center gap-4 p-4 border-2 rounded-xl cursor-pointer transition-all ${
                            isSelected 
                              ? 'bg-primary-light/20 border-primary ring-1 ring-primary' 
                              : 'bg-surface border-border hover:border-primary-light hover:bg-surface-hover'
                          }`}
                        >
                          <input 
                            type="radio" 
                            name={`q-${q.id}`} 
                            value={opt} 
                            checked={isSelected}
                            onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
                            className="w-5 h-5 text-primary border-border focus:ring-primary"
                          />
                          <span className="font-medium text-foreground">{opt}</span>
                        </label>
                      );
                    })}
                  </div>
                ) : (
                  <textarea 
                    className="w-full p-4 border border-border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary bg-background focus:bg-surface transition-all resize-y min-h-[120px] text-foreground"
                    placeholder="Type your detailed answer here..."
                    value={answers[q.id] || ""}
                    onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
                  ></textarea>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-12 flex justify-end">
        <button 
          onClick={handleSubmit} 
          disabled={submitting} 
          className={`px-8 py-3.5 rounded-xl font-bold flex items-center gap-2 transition-all shadow-sm ${
            isComplete 
              ? 'bg-success hover:bg-success/90 text-white' 
              : 'bg-muted hover:bg-muted/80 text-white'
          } disabled:opacity-50`}
        >
          {submitting ? (
            <><span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span> Submitting...</>
          ) : isComplete ? (
            <><CheckCircle2 size={20} /> Submit Quiz</>
          ) : (
            <>Submit Partially <ChevronRight size={20} /></>
          )}
        </button>
      </div>
    </div>
  );
}
