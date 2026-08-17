"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Calendar, Clock, Award, Plus, Activity } from "lucide-react";

interface Exam {
  id: string;
  title: string;
  exam_date: string;
  status: string;
  readiness_score: number;
}

export default function ExamsDashboard() {
  const [exams, setExams] = useState<Exam[]>([]);
  const router = useRouter();

  useEffect(() => {
    const fetchExams = async () => {
      const token = localStorage.getItem("token");
      if (!token) {
        router.push("/");
        return;
      }
      try {
        const res = await fetch("http://localhost:8000/api/exams", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setExams(data);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchExams();
  }, [router]);

  return (
    <div className="p-6 md:p-10 max-w-7xl mx-auto flex-1 w-full animate-in">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-foreground flex items-center gap-3">
            <Award className="text-primary" /> Exam Engine
          </h1>
          <p className="text-muted mt-2 text-lg">Manage your study plans and mock exams.</p>
        </div>
        <button
          onClick={() => router.push("/exams/create")}
          className="flex items-center justify-center gap-2 bg-primary text-white px-6 py-3 rounded-xl font-medium hover:bg-primary-hover transition shadow-sm premium-shadow whitespace-nowrap"
        >
          <Plus size={18} /> New Exam Plan
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {exams.length === 0 ? (
          <div className="col-span-full flex flex-col items-center justify-center p-12 bg-surface rounded-3xl border border-border premium-shadow">
            <div className="w-20 h-20 bg-primary-light/30 text-primary rounded-full flex items-center justify-center mb-6">
              <Calendar size={40} />
            </div>
            <h3 className="text-xl font-bold text-foreground">No active exam plans</h3>
            <p className="text-muted mt-3 text-center max-w-md leading-relaxed">
              Create a new exam plan to set your syllabus, define your goals, and generate targeted mock tests that adapt to your weaknesses.
            </p>
            <button
              onClick={() => router.push("/exams/create")}
              className="mt-8 bg-primary-light/30 text-primary px-8 py-3 rounded-xl font-bold hover:bg-primary-light/50 transition"
            >
              Set up First Exam
            </button>
          </div>
        ) : (
          exams.map((exam) => (
            <div
              key={exam.id}
              className="bg-surface rounded-3xl border border-border overflow-hidden hover:border-primary-light premium-shadow-hover transition cursor-pointer group flex flex-col"
              onClick={() => router.push(`/exams/${exam.id}`)}
            >
              <div className="p-8 flex-1">
                <div className="flex justify-between items-start mb-6 gap-2">
                  <h3 className="text-xl font-bold text-foreground leading-tight">
                    {exam.title}
                  </h3>
                  <span
                    className={`px-3 py-1.5 text-xs font-bold uppercase tracking-wider rounded-full shrink-0 ${
                      exam.status === "ACTIVE"
                        ? "bg-success/20 text-success"
                        : exam.status === "COMPLETED"
                        ? "bg-muted-bg text-foreground"
                        : "bg-primary-light/30 text-primary"
                    }`}
                  >
                    {exam.status}
                  </span>
                </div>

                <div className="space-y-4 mb-8">
                  <div className="flex items-center text-[15px] text-foreground/80 gap-3">
                    <div className="w-8 h-8 rounded-lg bg-muted-bg flex items-center justify-center text-muted">
                      <Calendar size={16} />
                    </div>
                    <span className="font-medium">{new Date(exam.exam_date).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}</span>
                  </div>
                  
                  {exam.status !== "COMPLETED" && (
                    <div className="bg-muted-bg rounded-xl p-4 border border-border">
                      <div className="flex items-center justify-between text-sm mb-2">
                        <span className="text-foreground/80 font-medium flex items-center gap-2">
                          <Activity size={16} className="text-muted" /> Readiness
                        </span>
                        <span className="font-bold text-foreground">{exam.readiness_score.toFixed(0)}%</span>
                      </div>
                      <div className="h-2 w-full bg-background rounded-full overflow-hidden">
                        <div 
                          className={`h-full transition-all ${exam.readiness_score > 70 ? 'bg-success' : exam.readiness_score > 40 ? 'bg-warning' : 'bg-error'}`} 
                          style={{ width: `${exam.readiness_score}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="p-4 bg-muted-bg border-t border-border">
                <button className="text-primary font-bold text-sm group-hover:text-primary-hover flex items-center justify-center gap-2 w-full py-2">
                  View Exam Dashboard
                  <span className="transform translate-x-0 group-hover:translate-x-1 transition-transform">
                    →
                  </span>
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
