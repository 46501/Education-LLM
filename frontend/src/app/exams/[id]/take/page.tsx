"use client";
import { useEffect, useState, Suspense } from "react";
import { useRouter, useParams, useSearchParams } from "next/navigation";
import { Clock, CheckCircle, ChevronRight, ChevronLeft } from "lucide-react";

interface ExamQuestion {
  question_id: string;
  question_text: string;
  question_type: string;
  difficulty: string;
  options: string[] | null;
  marks: number;
  question_order: number;
}

interface ExamSession {
  id: string;
  exam_id: string;
  started_at: string;
  duration_minutes: number;
  status: string;
  questions: ExamQuestion[];
}

function ExamSessionContent() {
  const params = useParams();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session");
  const router = useRouter();

  const [session, setSession] = useState<ExamSession | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [currentIndex, setCurrentIndex] = useState(0);
  const [timeLeft, setTimeLeft] = useState(0);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!sessionId) return;
    const fetchSession = async () => {
      const token = localStorage.getItem("token");
      try {
        const res = await fetch(`http://localhost:8000/api/exams/${params.id}/session/${sessionId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setSession(data);
          
          // Calculate time left based on server start time
          const start = new Date(data.started_at).getTime();
          const durationMs = data.duration_minutes * 60 * 1000;
          const end = start + durationMs;
          const now = Date.now();
          const diff = Math.max(0, Math.floor((end - now) / 1000));
          setTimeLeft(diff);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchSession();
  }, [params.id, sessionId]);

  useEffect(() => {
    if (timeLeft <= 0 || !session) return;
    const timer = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) {
          clearInterval(timer);
          handleSubmit(); // Auto submit
          return 0;
        }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [timeLeft, session]);

  const handleAnswerChange = (val: string) => {
    if (!session) return;
    const qid = session.questions[currentIndex].question_id;
    setAnswers({ ...answers, [qid]: val });
  };

  const handleSubmit = async () => {
    if (!session || submitting) return;
    setSubmitting(true);
    const payload = {
      answers: Object.keys(answers).map(qid => ({
        question_id: qid,
        answer: answers[qid]
      }))
    };

    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`http://localhost:8000/api/exams/${params.id}/session/${session.id}/submit`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        router.push(`/exams/${params.id}/result?session=${session.id}`);
      }
    } catch (err) {
      console.error(err);
      setSubmitting(false);
    }
  };

  if (!session) return <div className="p-12 text-center text-muted">Loading Exam...</div>;

  const currentQuestion = session.questions[currentIndex];
  const formatTime = (secs: number) => {
    const h = Math.floor(secs / 3600);
    const m = Math.floor((secs % 3600) / 60);
    const s = secs % 60;
    if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Sticky Top Bar */}
      <div className="bg-surface border-b border-border sticky top-0 z-20 shadow-sm">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-primary bg-primary-light/10 px-3 py-1.5 rounded-lg font-mono font-medium border border-primary/20">
              <Clock size={18} />
              {formatTime(timeLeft)}
            </div>
            <span className="text-muted text-sm font-medium">Remaining</span>
          </div>
          
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="flex items-center gap-2 bg-success text-white px-5 py-2 rounded-lg font-medium hover:bg-success/90 transition shadow-sm disabled:opacity-50"
          >
            <CheckCircle size={18} /> {submitting ? "Submitting..." : "Submit Exam"}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 max-w-4xl w-full mx-auto p-6 md:p-12">
        <div className="mb-6 flex gap-2 overflow-x-auto pb-4">
          {session.questions.map((q, idx) => (
            <button
              key={q.question_id}
              onClick={() => setCurrentIndex(idx)}
              className={`shrink-0 w-10 h-10 rounded-full font-medium border-2 transition flex items-center justify-center ${
                currentIndex === idx 
                  ? "border-primary text-primary bg-primary-light/10" 
                  : answers[q.question_id]
                  ? "border-success text-success bg-success/20"
                  : "border-border text-muted hover:border-muted"
              }`}
            >
              {idx + 1}
            </button>
          ))}
        </div>

        <div className="bg-surface rounded-2xl shadow-sm border border-border p-8 min-h-[400px] flex flex-col">
          <div className="flex justify-between items-start mb-6">
            <span className="text-sm font-bold text-muted uppercase tracking-wider">Question {currentIndex + 1} of {session.questions.length}</span>
            <span className="text-sm font-medium text-primary bg-primary-light/10 px-2 py-1 rounded">{currentQuestion.marks} Marks</span>
          </div>

          <h2 className="text-xl font-medium text-foreground mb-8">{currentQuestion.question_text}</h2>

          <div className="flex-1">
            {currentQuestion.question_type === "MULTIPLE_CHOICE" && currentQuestion.options ? (
              <div className="space-y-3">
                {currentQuestion.options.map((opt, i) => (
                  <label key={i} className={`flex items-center gap-3 p-4 rounded-xl border-2 cursor-pointer transition ${answers[currentQuestion.question_id] === opt ? "border-primary bg-primary-light/10" : "border-border hover:border-muted"}`}>
                    <input
                      type="radio"
                      name={currentQuestion.question_id}
                      value={opt}
                      checked={answers[currentQuestion.question_id] === opt}
                      onChange={() => handleAnswerChange(opt)}
                      className="w-5 h-5 text-primary border-border focus:ring-primary"
                    />
                    <span className="text-foreground">{opt}</span>
                  </label>
                ))}
              </div>
            ) : (
              <textarea
                value={answers[currentQuestion.question_id] || ""}
                onChange={(e) => handleAnswerChange(e.target.value)}
                placeholder="Write your answer here..."
                className="w-full h-64 p-4 rounded-xl border-2 bg-background border-border focus:border-primary focus:ring-0 outline-none resize-none transition text-foreground"
              />
            )}
          </div>
        </div>

        {/* Navigation Footer */}
        <div className="mt-8 flex justify-between">
          <button
            onClick={() => setCurrentIndex(c => Math.max(0, c - 1))}
            disabled={currentIndex === 0}
            className="flex items-center gap-2 px-6 py-3 rounded-xl font-medium text-foreground bg-surface border border-border hover:bg-surface-hover transition disabled:opacity-50"
          >
            <ChevronLeft size={20} /> Previous
          </button>

          {currentIndex < session.questions.length - 1 ? (
            <button
              onClick={() => setCurrentIndex(c => Math.min(session.questions.length - 1, c + 1))}
              className="flex items-center gap-2 px-6 py-3 rounded-xl font-medium text-white bg-primary hover:bg-primary-hover transition"
            >
              Next <ChevronRight size={20} />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="flex items-center gap-2 px-6 py-3 rounded-xl font-medium text-white bg-success hover:bg-success/90 transition"
            >
              Submit <CheckCircle size={20} />
            </button>
          )}
        </div>
      </main>
    </div>
  );
}

export default function ExamSessionPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-muted">Loading...</div>}>
      <ExamSessionContent />
    </Suspense>
  );
}
