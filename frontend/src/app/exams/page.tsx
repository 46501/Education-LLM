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
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Award className="text-indigo-600" /> Exam Engine
          </h1>
          <p className="text-gray-500 mt-2 text-lg">Manage your study plans and mock exams.</p>
        </div>
        <button
          onClick={() => router.push("/exams/create")}
          className="flex items-center justify-center gap-2 bg-indigo-600 text-white px-6 py-3 rounded-xl font-medium hover:bg-indigo-700 transition shadow-sm premium-shadow whitespace-nowrap"
        >
          <Plus size={18} /> New Exam Plan
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {exams.length === 0 ? (
          <div className="col-span-full flex flex-col items-center justify-center p-12 bg-white rounded-3xl border border-gray-100 premium-shadow">
            <div className="w-20 h-20 bg-indigo-50 text-indigo-500 rounded-full flex items-center justify-center mb-6">
              <Calendar size={40} />
            </div>
            <h3 className="text-xl font-bold text-gray-900">No active exam plans</h3>
            <p className="text-gray-500 mt-3 text-center max-w-md leading-relaxed">
              Create a new exam plan to set your syllabus, define your goals, and generate targeted mock tests that adapt to your weaknesses.
            </p>
            <button
              onClick={() => router.push("/exams/create")}
              className="mt-8 bg-indigo-50 text-indigo-700 px-8 py-3 rounded-xl font-bold hover:bg-indigo-100 transition"
            >
              Set up First Exam
            </button>
          </div>
        ) : (
          exams.map((exam) => (
            <div
              key={exam.id}
              className="bg-white rounded-3xl border border-gray-100 overflow-hidden hover:border-indigo-300 premium-shadow-hover transition cursor-pointer group flex flex-col"
              onClick={() => router.push(`/exams/${exam.id}`)}
            >
              <div className="p-8 flex-1">
                <div className="flex justify-between items-start mb-6 gap-2">
                  <h3 className="text-xl font-bold text-gray-900 leading-tight">
                    {exam.title}
                  </h3>
                  <span
                    className={`px-3 py-1.5 text-xs font-bold uppercase tracking-wider rounded-full shrink-0 ${
                      exam.status === "ACTIVE"
                        ? "bg-emerald-100 text-emerald-800"
                        : exam.status === "COMPLETED"
                        ? "bg-gray-100 text-gray-800"
                        : "bg-indigo-100 text-indigo-800"
                    }`}
                  >
                    {exam.status}
                  </span>
                </div>

                <div className="space-y-4 mb-8">
                  <div className="flex items-center text-[15px] text-gray-600 gap-3">
                    <div className="w-8 h-8 rounded-lg bg-gray-50 flex items-center justify-center text-gray-400">
                      <Calendar size={16} />
                    </div>
                    <span className="font-medium">{new Date(exam.exam_date).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}</span>
                  </div>
                  
                  {exam.status !== "COMPLETED" && (
                    <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                      <div className="flex items-center justify-between text-sm mb-2">
                        <span className="text-gray-600 font-medium flex items-center gap-2">
                          <Activity size={16} className="text-gray-400" /> Readiness
                        </span>
                        <span className="font-bold text-gray-900">{exam.readiness_score.toFixed(0)}%</span>
                      </div>
                      <div className="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className={`h-full transition-all ${exam.readiness_score > 70 ? 'bg-emerald-500' : exam.readiness_score > 40 ? 'bg-amber-500' : 'bg-red-500'}`} 
                          style={{ width: `${exam.readiness_score}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="p-4 bg-gray-50 border-t border-gray-100">
                <button className="text-indigo-600 font-bold text-sm group-hover:text-indigo-700 flex items-center justify-center gap-2 w-full py-2">
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
