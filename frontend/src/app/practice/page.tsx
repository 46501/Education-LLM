"use client";
import { useState } from "react";
import { BookOpen, Target, Settings2, Play, CheckCircle, XCircle, ArrowRight } from "lucide-react";

export default function PracticeMode() {
  const [subject, setSubject] = useState("");
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("BEGINNER");
  const [activeQuestion, setActiveQuestion] = useState<any>(null);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault();
    await fetchNextQuestion(difficulty);
  };

  const fetchNextQuestion = async (targetDifficulty: string) => {
    setLoading(true);
    setFeedback(null);
    setAnswer("");
    const token = localStorage.getItem("token");

    try {
      const res = await fetch("http://localhost:8000/api/practice/start", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ subject, topic, difficulty: targetDifficulty })
      });
      if (!res.ok) throw new Error("Failed to load question");
      setActiveQuestion(await res.json());
    } catch (err) {
      alert("Error loading question");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = async () => {
    if (!answer) return;
    setLoading(true);
    const token = localStorage.getItem("token");

    try {
      const res = await fetch("http://localhost:8000/api/practice/answer", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ question_id: activeQuestion.id, submitted_answer: answer })
      });
      if (!res.ok) throw new Error("Failed to submit");
      const data = await res.json();
      setFeedback(data);
      setDifficulty(data.new_recommended_difficulty);
    } catch (err) {
      alert("Error submitting answer");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 md:p-10 max-w-4xl mx-auto flex flex-col h-full min-h-[calc(100vh-4rem)]">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Target className="text-indigo-600" /> Practice Mode
        </h1>
        <p className="text-gray-500 mt-1">Hone your skills with adaptive difficulty questions.</p>
      </div>

      <div className="flex-1 flex flex-col items-center justify-center">
        {!activeQuestion ? (
          <div className="w-full max-w-lg bg-white p-8 rounded-2xl border border-gray-100 premium-shadow">
            <h2 className="text-lg font-bold mb-6 text-gray-900 border-b border-gray-100 pb-4 flex items-center gap-2">
              <Settings2 size={18} className="text-gray-400" /> Configure Session
            </h2>
            <form onSubmit={handleStart} className="space-y-5">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Subject</label>
                <div className="relative">
                  <BookOpen className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                  <input 
                    required 
                    type="text" 
                    placeholder="e.g. Computer Science"
                    className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all" 
                    value={subject} 
                    onChange={e => setSubject(e.target.value)} 
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Topic</label>
                <div className="relative">
                  <Target className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                  <input 
                    required 
                    type="text" 
                    placeholder="e.g. Algorithms"
                    className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all" 
                    value={topic} 
                    onChange={e => setTopic(e.target.value)} 
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Starting Difficulty</label>
                <select 
                  className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all" 
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

              <button 
                type="submit" 
                disabled={loading} 
                className="w-full flex items-center justify-center gap-2 bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 transition shadow-sm mt-4 disabled:opacity-70"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Starting...
                  </span>
                ) : (
                  <>Start Practicing <Play size={18} /></>
                )}
              </button>
            </form>
          </div>
        ) : (
          <div className="w-full bg-white p-8 rounded-2xl border border-gray-100 premium-shadow">
            <div className="flex justify-between items-center mb-6 pb-4 border-b border-gray-100">
              <h2 className="text-lg font-bold text-gray-900">{topic}</h2>
              <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                difficulty === 'BEGINNER' || difficulty === 'EASY' ? 'bg-emerald-100 text-emerald-800' :
                difficulty === 'MEDIUM' ? 'bg-amber-100 text-amber-800' :
                'bg-red-100 text-red-800'
              }`}>
                {difficulty}
              </span>
            </div>

            <h3 className="text-xl font-medium text-gray-800 mb-8 leading-relaxed">{activeQuestion.text}</h3>
            
            <div className="space-y-3 mb-8">
              {activeQuestion.options?.map((opt: string, i: number) => {
                const isSelected = answer === opt;
                let bgState = "bg-white border-gray-200 hover:border-indigo-300 hover:bg-gray-50";
                if (isSelected) bgState = "bg-indigo-50 border-indigo-500 ring-1 ring-indigo-500";
                
                // If feedback exists, show correct/incorrect styling on the options
                if (feedback) {
                  if (opt === feedback.correct_answer) {
                    bgState = "bg-emerald-50 border-emerald-500 text-emerald-900";
                  } else if (isSelected && !feedback.is_correct) {
                    bgState = "bg-red-50 border-red-500 text-red-900";
                  } else {
                    bgState = "bg-gray-50 border-gray-200 opacity-50";
                  }
                }

                return (
                  <label key={i} className={`flex items-center gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all ${bgState}`}>
                    <input 
                      type="radio" 
                      name="practice-q" 
                      value={opt} 
                      checked={isSelected} 
                      onChange={(e) => setAnswer(e.target.value)} 
                      className="w-5 h-5 text-indigo-600 border-gray-300 focus:ring-indigo-500" 
                      disabled={!!feedback} 
                    />
                    <span className="font-medium">{opt}</span>
                    {feedback && opt === feedback.correct_answer && <CheckCircle className="ml-auto text-emerald-500" size={20} />}
                    {feedback && isSelected && !feedback.is_correct && <XCircle className="ml-auto text-red-500" size={20} />}
                  </label>
                );
              })}
            </div>

            {!feedback ? (
              <button 
                onClick={handleAnswer} 
                disabled={!answer || loading} 
                className="w-full bg-gray-900 text-white py-3 rounded-lg font-medium hover:bg-gray-800 disabled:opacity-50 transition flex items-center justify-center gap-2"
              >
                {loading ? "Checking..." : "Submit Answer"}
              </button>
            ) : (
              <div className="animate-in">
                <div className={`p-6 rounded-xl border mb-6 ${feedback.is_correct ? 'bg-emerald-50 border-emerald-200' : 'bg-red-50 border-red-200'}`}>
                  <h4 className={`text-lg font-bold flex items-center gap-2 mb-2 ${feedback.is_correct ? 'text-emerald-800' : 'text-red-800'}`}>
                    {feedback.is_correct ? <><CheckCircle /> Correct!</> : <><XCircle /> Incorrect</>}
                  </h4>
                  {feedback.explanation && <p className="text-gray-700 leading-relaxed mt-2">{feedback.explanation}</p>}
                </div>
                
                <button 
                  onClick={() => fetchNextQuestion(feedback.new_recommended_difficulty)} 
                  className="w-full bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 transition flex items-center justify-center gap-2"
                >
                  Next Question <ArrowRight size={18} />
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
