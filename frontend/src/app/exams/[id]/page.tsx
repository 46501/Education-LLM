"use client";
import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { ArrowLeft, Play, Sparkles, AlertCircle } from "lucide-react";

interface ExamDetail {
  id: string;
  title: string;
  status: string;
  readiness_score: number;
  duration_minutes: number;
  total_marks: number;
}

export default function ExamDetail() {
  const params = useParams();
  const router = useRouter();
  const [exam, setExam] = useState<ExamDetail | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchExam = async () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    try {
      const res = await fetch(`http://localhost:8000/api/exams/${params.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        setExam(await res.json());
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchExam();
  }, [params.id]);

  const handleGenerate = async () => {
    setLoading(true);
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`http://localhost:8000/api/exams/${params.id}/generate`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        await fetchExam(); // refresh to get ACTIVE status
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleStart = async () => {
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`http://localhost:8000/api/exams/${params.id}/start`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        router.push(`/exams/${params.id}/take?session=${data.session_id}`);
      }
    } catch (e) {
      console.error(e);
    }
  };

  if (!exam) return <div className="p-12 text-center text-muted">Loading...</div>;

  return (
    <div className="min-h-screen bg-background p-6 md:p-12">
      <div className="max-w-3xl mx-auto">
        <button
          onClick={() => router.push('/exams')}
          className="flex items-center gap-2 text-muted hover:text-foreground mb-8 transition-colors"
        >
          <ArrowLeft size={20} /> Back to Dashboard
        </button>

        <div className="bg-surface rounded-2xl shadow-sm border border-border overflow-hidden">
          <div className="p-8">
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-3xl font-bold text-foreground">{exam.title}</h1>
              <span
                className={`px-3 py-1 text-sm font-semibold rounded-full ${
                  exam.status === "ACTIVE" ? "bg-success/20 text-success" : "bg-warning/20 text-warning"
                }`}
              >
                {exam.status}
              </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-muted-bg rounded-xl p-4 border border-border">
                <p className="text-sm text-muted mb-1">Duration</p>
                <p className="text-lg font-semibold text-foreground">{exam.duration_minutes}m</p>
              </div>
              <div className="bg-muted-bg rounded-xl p-4 border border-border">
                <p className="text-sm text-muted mb-1">Total Marks</p>
                <p className="text-lg font-semibold text-foreground">{exam.total_marks}</p>
              </div>
              <div className="bg-muted-bg rounded-xl p-4 border border-border col-span-2">
                <p className="text-sm text-muted mb-1">Readiness</p>
                <div className="flex items-center gap-3 mt-1">
                  <div className="h-2 flex-1 bg-background rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${exam.readiness_score > 70 ? 'bg-success' : 'bg-warning'}`} 
                      style={{ width: `${exam.readiness_score}%` }}
                    />
                  </div>
                  <span className="font-semibold text-foreground">{exam.readiness_score.toFixed(0)}%</span>
                </div>
              </div>
            </div>

            <div className="bg-primary-light/10 border border-primary/20 rounded-xl p-6 flex items-start gap-4">
              <AlertCircle className="text-primary shrink-0 mt-1" />
              <div>
                <h3 className="font-semibold text-foreground mb-1">
                  {exam.status === "DRAFT" ? "Ready to generate your mock exam?" : "Your mock exam is ready"}
                </h3>
                <p className="text-muted text-sm mb-4">
                  {exam.status === "DRAFT" 
                    ? "Our AI will analyze your syllabus and past mistakes to construct a highly targeted exam designed to push your limits."
                    : "You have 120 minutes to complete this exam once you begin. Ensure you are in a quiet environment."}
                </p>
                
                {exam.status === "DRAFT" ? (
                  <button
                    onClick={handleGenerate}
                    disabled={loading}
                    className="flex items-center gap-2 bg-primary text-white px-5 py-2.5 rounded-lg font-medium hover:bg-primary-hover transition shadow-sm disabled:opacity-50"
                  >
                    <Sparkles size={18} />
                    {loading ? "Generating..." : "Generate AI Mock Exam"}
                  </button>
                ) : (
                  <button
                    onClick={handleStart}
                    className="flex items-center gap-2 bg-success text-white px-5 py-2.5 rounded-lg font-medium hover:bg-success/90 transition shadow-sm"
                  >
                    <Play size={18} /> Start Exam Session
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
