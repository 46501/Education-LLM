"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Mic, Briefcase, Star, Layers } from "lucide-react";

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
    <div className="min-h-screen bg-gray-50 p-6 md:p-12">
      <div className="max-w-2xl mx-auto">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-gray-500 hover:text-gray-900 mb-8 transition-colors"
        >
          <ArrowLeft size={20} /> Back
        </button>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="bg-gradient-to-r from-purple-600 to-indigo-600 px-8 py-8 text-white flex items-center gap-4">
            <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center shrink-0">
              <Mic size={24} className="text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Mock Interview Setup</h1>
              <p className="text-purple-100 mt-1">Configure your AI interviewer</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="p-8 space-y-6">
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Target Role</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Briefcase className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    required
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    className="pl-10 w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all"
                    placeholder="e.g. Frontend Developer"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Topics (comma separated)</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Layers className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    required
                    value={formData.topics}
                    onChange={(e) => setFormData({ ...formData, topics: e.target.value })}
                    className="pl-10 w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all"
                    placeholder="e.g. React, System Design, JavaScript"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">Experience Level</label>
                  <select
                    value={formData.experience_level}
                    onChange={(e) => setFormData({ ...formData, experience_level: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all bg-white"
                  >
                    <option value="INTERN">Intern</option>
                    <option value="ENTRY">Entry Level</option>
                    <option value="MID">Mid Level</option>
                    <option value="SENIOR">Senior</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">Number of Questions</label>
                  <input
                    type="number"
                    required
                    min={3}
                    max={15}
                    value={formData.num_questions}
                    onChange={(e) => setFormData({ ...formData, num_questions: parseInt(e.target.value) })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all"
                  />
                </div>
              </div>
            </div>

            <div className="pt-8 border-t border-gray-100">
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition shadow-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? "Initializing AI..." : "Start Interview"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
