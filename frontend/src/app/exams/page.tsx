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
    <div className="flex min-h-screen bg-gray-50 flex-col">
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <Award className="text-blue-600" /> Exam Engine
          </h1>
          <button
            onClick={() => router.push("/exams/create")}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition"
          >
            <Plus size={18} /> New Exam
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 flex-1 w-full">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {exams.length === 0 ? (
            <div className="col-span-full flex flex-col items-center justify-center p-12 bg-white rounded-xl shadow-sm border border-gray-100">
              <div className="w-16 h-16 bg-blue-50 text-blue-500 rounded-full flex items-center justify-center mb-4">
                <Calendar size={32} />
              </div>
              <h3 className="text-lg font-medium text-gray-900">No upcoming exams</h3>
              <p className="text-gray-500 mt-2 text-center max-w-sm">
                Create a new exam to set up your syllabus and generate mock tests tailored to your weaknesses.
              </p>
              <button
                onClick={() => router.push("/exams/create")}
                className="mt-6 bg-blue-50 text-blue-700 px-6 py-2 rounded-lg font-medium hover:bg-blue-100 transition"
              >
                Create First Exam
              </button>
            </div>
          ) : (
            exams.map((exam) => (
              <div
                key={exam.id}
                className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow group cursor-pointer"
                onClick={() => router.push(`/exams/${exam.id}`)}
              >
                <div className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 leading-tight">
                      {exam.title}
                    </h3>
                    <span
                      className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                        exam.status === "ACTIVE"
                          ? "bg-green-100 text-green-800"
                          : exam.status === "COMPLETED"
                          ? "bg-gray-100 text-gray-800"
                          : "bg-blue-100 text-blue-800"
                      }`}
                    >
                      {exam.status}
                    </span>
                  </div>

                  <div className="space-y-3 mb-6">
                    <div className="flex items-center text-sm text-gray-600 gap-2">
                      <Calendar size={16} className="text-gray-400" />
                      <span>{new Date(exam.exam_date).toLocaleDateString()}</span>
                    </div>
                    
                    {exam.status !== "COMPLETED" && (
                      <div className="flex items-center text-sm text-gray-600 gap-2">
                        <Activity size={16} className="text-gray-400" />
                        <span>Readiness Score:</span>
                        <div className="flex-1 ml-2">
                          <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                            <div 
                              className={`h-full ${exam.readiness_score > 70 ? 'bg-green-500' : exam.readiness_score > 40 ? 'bg-yellow-500' : 'bg-red-500'}`} 
                              style={{ width: `${exam.readiness_score}%` }}
                            />
                          </div>
                        </div>
                        <span className="font-medium">{exam.readiness_score.toFixed(0)}%</span>
                      </div>
                    )}
                  </div>

                  <div className="pt-4 border-t border-gray-100">
                    <button className="text-blue-600 font-medium text-sm group-hover:text-blue-700 flex items-center justify-between w-full">
                      View Details
                      <span className="transform translate-x-0 group-hover:translate-x-1 transition-transform">
                        →
                      </span>
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  );
}
