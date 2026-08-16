"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Mic, Briefcase, Layers, Sparkles } from "lucide-react";

export default function InterviewSetup() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    interview_type: "TECHNICAL",
    role: "Software Engineer",
    experience_level: "ENTRY",
    difficulty: "MEDIUM",
    num_questions: 5,
    topics: "Python, Algorithms", // string to be split
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const token = localStorage.getItem("token");
    try {
      const payload = {
        ...formData,
        topics: formData.topics.split(",").map(t => t.trim()).filter(Boolean)
      };

      const res = await fetch("http://localhost:8000/api/interviews", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        // Start interview immediately
        const startRes = await fetch(`http://localhost:8000/api/interviews/${data.id}/start`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` }
        });
        if (startRes.ok) {
          const startData = await startRes.json();
          router.push(`/interview/${data.id}/session?session=${startData.session_id}`);
        }
      } else {
        alert("Failed to setup interview");
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 md:p-10 max-w-4xl mx-auto min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center animate-in">
      <div className="w-full max-w-2xl bg-white rounded-3xl border border-gray-100 overflow-hidden premium-shadow">
        
        <div className="bg-gradient-to-r from-purple-900 to-indigo-900 px-8 py-10 text-white flex flex-col md:flex-row items-center gap-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-5 rounded-full blur-3xl transform translate-x-1/2 -translate-y-1/2"></div>
          <div className="w-16 h-16 bg-white/10 rounded-2xl flex items-center justify-center shrink-0 border border-white/20 z-10 backdrop-blur-sm">
            <Mic size={32} className="text-white" />
          </div>
          <div className="text-center md:text-left z-10">
            <h1 className="text-2xl font-bold tracking-tight">Mock Interview Setup</h1>
            <p className="text-purple-200 mt-1">Configure your AI interviewer for a realistic session.</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-8 md:p-10 space-y-8">
          <div className="space-y-6">
            
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Target Role</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                  <Briefcase className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  required
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  className="pl-11 w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:bg-white outline-none transition-all"
                  placeholder="e.g. Frontend Developer"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Topics (comma separated)</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                  <Layers className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  required
                  value={formData.topics}
                  onChange={(e) => setFormData({ ...formData, topics: e.target.value })}
                  className="pl-11 w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:bg-white outline-none transition-all"
                  placeholder="e.g. React, System Design, JavaScript"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">Experience Level</label>
                <select
                  value={formData.experience_level}
                  onChange={(e) => setFormData({ ...formData, experience_level: e.target.value })}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:bg-white outline-none transition-all appearance-none"
                >
                  <option value="INTERN">Intern</option>
                  <option value="ENTRY">Entry Level</option>
                  <option value="MID">Mid Level</option>
                  <option value="SENIOR">Senior</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">Number of Questions</label>
                <input
                  type="number"
                  required
                  min={3}
                  max={15}
                  value={formData.num_questions}
                  onChange={(e) => setFormData({ ...formData, num_questions: parseInt(e.target.value) })}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:bg-white outline-none transition-all"
                />
              </div>
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 bg-purple-600 text-white rounded-xl font-bold hover:bg-purple-700 transition-all shadow-sm disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Initializing AI Interviewer...
                </>
              ) : (
                <>
                  <Sparkles size={18} />
                  Start Interview Session
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
