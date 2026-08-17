"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, BookOpen, Clock, Target, Calendar } from "lucide-react";

export default function CreateExam() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    exam_date: "",
    duration_minutes: 60,
    total_marks: 100,
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const token = localStorage.getItem("token");
    try {
      // Mock some standard topics for now
      const payload = {
        ...formData,
        exam_date: new Date(formData.exam_date).toISOString(),
        topics: [] // Typically users would select these in a multiselect
      };

      const res = await fetch("http://localhost:8000/api/exams", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        router.push(`/exams/${data.id}`);
      } else {
        alert("Failed to create exam");
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background p-6 md:p-12">
      <div className="max-w-2xl mx-auto">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-muted hover:text-foreground mb-8 transition-colors"
        >
          <ArrowLeft size={20} /> Back to Dashboard
        </button>

        <div className="bg-surface rounded-2xl shadow-sm border border-border overflow-hidden">
          <div className="bg-primary px-8 py-6 text-white">
            <h1 className="text-2xl font-bold">Create Exam Plan</h1>
            <p className="text-primary-light mt-1">Configure your goal and let AI build the syllabus</p>
          </div>

          <form onSubmit={handleSubmit} className="p-8 space-y-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-foreground/80 mb-1">Exam Title</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <BookOpen className="h-5 w-5 text-muted" />
                  </div>
                  <input
                    type="text"
                    required
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="pl-10 w-full px-4 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all text-foreground"
                    placeholder="e.g. AWS Solutions Architect"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-foreground/80 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all h-24 resize-none text-foreground"
                  placeholder="Goals or specific areas to focus on..."
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-semibold text-foreground/80 mb-1">Target Date</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Calendar className="h-5 w-5 text-muted" />
                    </div>
                    <input
                      type="date"
                      required
                      value={formData.exam_date}
                      onChange={(e) => setFormData({ ...formData, exam_date: e.target.value })}
                      className="pl-10 w-full px-4 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all text-foreground"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-foreground/80 mb-1">Duration (mins)</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Clock className="h-5 w-5 text-muted" />
                    </div>
                    <input
                      type="number"
                      required
                      min={10}
                      value={formData.duration_minutes}
                      onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) })}
                      className="pl-10 w-full px-4 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all text-foreground"
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-6 border-t border-border flex justify-end gap-3">
              <button
                type="button"
                onClick={() => router.back()}
                className="px-6 py-2 border border-border text-foreground rounded-lg font-medium hover:bg-surface-hover transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-primary text-white rounded-lg font-medium hover:bg-primary-hover transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loading ? "Creating..." : "Create Exam Plan"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
