"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Award, BookOpen, Target, Sliders, Hash, FileText, Check, Settings2, Sparkles } from "lucide-react";

export default function CreateQuiz() {
  const [subject, setSubject] = useState("");
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("MEDIUM");
  const [numQuestions, setNumQuestions] = useState(5);
  const [useRag, setUseRag] = useState(false);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const token = localStorage.getItem("token");

    try {
      const res = await fetch("http://localhost:8000/api/quizzes/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          title: `${topic} Quiz`,
          subject,
          topic,
          difficulty,
          number_of_questions: numQuestions,
          use_rag: useRag
        })
      });

      if (!res.ok) throw new Error("Failed to generate quiz");
      const data = await res.json();
      router.push(`/quizzes/${data.quiz_id}`);
    } catch (err) {
      alert(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 md:p-10 max-w-4xl mx-auto min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center animate-in">
      
      <div className="w-full max-w-xl bg-surface p-8 md:p-10 rounded-3xl border border-border premium-shadow">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-primary-light/30 text-primary rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Award size={32} />
          </div>
          <h1 className="text-2xl font-bold text-foreground">Generate a Quiz</h1>
          <p className="text-muted mt-2 text-sm">Configure your quiz settings. Our AI will craft personalized questions for you.</p>
        </div>

        <form onSubmit={handleGenerate} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-foreground/80 mb-1.5">Subject</label>
              <div className="relative">
                <BookOpen className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={16} />
                <input 
                  required 
                  type="text" 
                  placeholder="e.g. History"
                  className="w-full pl-10 pr-4 py-2.5 bg-background border border-border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all text-sm text-foreground" 
                  value={subject} 
                  onChange={e => setSubject(e.target.value)} 
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-semibold text-foreground/80 mb-1.5">Topic</label>
              <div className="relative">
                <Target className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={16} />
                <input 
                  required 
                  type="text" 
                  placeholder="e.g. World War II"
                  className="w-full pl-10 pr-4 py-2.5 bg-background border border-border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all text-sm text-foreground" 
                  value={topic} 
                  onChange={e => setTopic(e.target.value)} 
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-foreground/80 mb-1.5">Difficulty</label>
              <div className="relative">
                <Sliders className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={16} />
                <select 
                  className="w-full pl-10 pr-4 py-2.5 bg-background border border-border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all text-sm appearance-none text-foreground" 
                  value={difficulty} 
                  onChange={e => setDifficulty(e.target.value)}
                >
                  <option value="BEGINNER">Beginner</option>
                  <option value="EASY">Easy</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HARD">Hard</option>
                  <option value="EXPERT">Expert</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-semibold text-foreground/80 mb-1.5">Questions</label>
              <div className="relative">
                <Hash className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={16} />
                <input 
                  type="number" 
                  min="1" 
                  max="20" 
                  className="w-full pl-10 pr-4 py-2.5 bg-background border border-border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all text-sm text-foreground" 
                  value={numQuestions} 
                  onChange={e => setNumQuestions(parseInt(e.target.value))} 
                />
              </div>
            </div>
          </div>

          <div className="bg-primary-light/20 border border-primary/20 rounded-xl p-4">
            <label className="flex items-start gap-3 cursor-pointer group">
              <div className="relative flex items-center justify-center shrink-0 mt-0.5">
                <input 
                  type="checkbox" 
                  className="peer sr-only" 
                  checked={useRag} 
                  onChange={e => setUseRag(e.target.checked)} 
                />
                <div className="w-5 h-5 border-2 border-primary/30 rounded bg-background peer-checked:bg-primary peer-checked:border-primary transition-all"></div>
                <Check size={14} className="absolute text-white opacity-0 peer-checked:opacity-100 transition-opacity" />
              </div>
              <div>
                <p className="text-sm font-semibold text-foreground flex items-center gap-1.5">
                  <FileText size={16} /> Base questions on my documents
                </p>
                <p className="text-xs text-muted mt-1">If enabled, the AI will prioritize testing you on content from PDFs you've uploaded.</p>
              </div>
            </label>
          </div>

          <button 
            type="submit" 
            disabled={loading} 
            className="w-full bg-primary text-white py-3.5 rounded-xl font-semibold hover:bg-primary-hover disabled:opacity-70 disabled:hover:bg-primary transition-all shadow-sm flex items-center justify-center gap-2 mt-4"
          >
            {loading ? (
              <>
                <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Crafting your Quiz...</span>
              </>
            ) : (
              <>
                <Sparkles size={18} />
                <span>Generate Quiz</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
