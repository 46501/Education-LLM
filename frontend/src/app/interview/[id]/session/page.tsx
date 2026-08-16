"use client";
import { useEffect, useState, useRef, Suspense } from "react";
import { useRouter, useParams, useSearchParams } from "next/navigation";
import { Send, User as UserIcon, Bot, CheckCircle, BrainCircuit } from "lucide-react";

interface Message {
  role: "interviewer" | "student";
  content: string;
  evaluation?: {
    score: number;
    technical_accuracy: number;
    feedback: string;
  };
}

function InterviewSessionContent() {
  const params = useParams();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session");
  const router = useRouter();

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [finalScore, setFinalScore] = useState<number | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Ideally we'd fetch existing session messages here on mount
    // For now we assume a fresh session and rely on the start endpoint response
    setMessages([{ role: "interviewer", content: "Hello! I will be your interviewer today. Are you ready to begin?" }]);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isTyping || isCompleted) return;

    const token = localStorage.getItem("token");
    const userMsg = input.trim();
    setInput("");
    
    setMessages(prev => [...prev, { role: "student", content: userMsg }]);
    setIsTyping(true);

    try {
      const res = await fetch(`http://localhost:8000/api/interviews/session/${sessionId}/answer`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ answer: userMsg })
      });
      
      if (res.ok) {
        const data = await res.json();
        
        // Update user message with evaluation context
        setMessages(prev => {
          const newMsgs = [...prev];
          newMsgs[newMsgs.length - 1].evaluation = data.evaluation;
          return newMsgs;
        });

        // Add interviewer next question
        setMessages(prev => [...prev, { role: "interviewer", content: data.next_question }]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsTyping(false);
    }
  };

  const handleComplete = async () => {
    if (!confirm("Are you sure you want to end the interview?")) return;
    
    setIsTyping(true);
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`http://localhost:8000/api/interviews/session/${sessionId}/complete`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.ok) {
        const data = await res.json();
        setIsCompleted(true);
        setFinalScore(data.score);
        setMessages(prev => [...prev, { role: "interviewer", content: "The interview has concluded. Please review your performance analytics." }]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-800 flex items-center gap-2">
            <BrainCircuit className="text-purple-600" /> AI Interviewer
          </h1>
          {!isCompleted && (
            <button
              onClick={handleComplete}
              className="text-sm bg-gray-100 text-gray-600 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition"
            >
              End Interview
            </button>
          )}
        </div>
      </header>

      <main className="flex-1 max-w-4xl w-full mx-auto p-4 md:p-6 overflow-y-auto">
        {isCompleted && finalScore !== null && (
          <div className="mb-8 bg-purple-50 border border-purple-100 rounded-xl p-6 text-center">
            <h2 className="text-2xl font-bold text-purple-900 mb-2">Interview Completed</h2>
            <div className="text-5xl font-extrabold text-purple-600 my-4">{finalScore.toFixed(1)} <span className="text-2xl text-purple-400">/ 10</span></div>
            <p className="text-purple-800">Your detailed feedback is saved to your profile.</p>
            <button
              onClick={() => router.push('/exams')}
              className="mt-6 bg-purple-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-purple-700 transition"
            >
              Back to Dashboard
            </button>
          </div>
        )}

        <div className="space-y-6 pb-24">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === "student" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[85%] md:max-w-[75%] rounded-2xl p-5 ${
                msg.role === "student" 
                  ? "bg-purple-600 text-white rounded-br-none shadow-md" 
                  : "bg-white text-gray-800 border border-gray-100 shadow-sm rounded-bl-none"
              }`}>
                <div className="flex items-center gap-2 mb-2 opacity-80 text-sm font-medium">
                  {msg.role === "student" ? <UserIcon size={16} /> : <Bot size={16} />}
                  {msg.role === "student" ? "You" : "Interviewer"}
                </div>
                <div className="text-[15px] leading-relaxed whitespace-pre-wrap">{msg.content}</div>
                
                {msg.evaluation && (
                  <div className="mt-4 pt-3 border-t border-purple-400/30 text-sm bg-purple-700/30 p-3 rounded-lg">
                    <div className="font-semibold text-purple-100 mb-1 flex items-center justify-between">
                      <span>Internal Evaluation</span>
                      <span className="bg-purple-500 px-2 py-0.5 rounded text-xs">{msg.evaluation.score}/10</span>
                    </div>
                    <p className="text-purple-50 italic">"{msg.evaluation.feedback}"</p>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-100 shadow-sm rounded-2xl rounded-bl-none p-4 flex gap-2">
                <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce"></span>
                <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></span>
                <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      {!isCompleted && (
        <div className="bg-white border-t border-gray-200 p-4 fixed bottom-0 w-full">
          <div className="max-w-4xl mx-auto">
            <form onSubmit={handleSend} className="flex items-center gap-3 relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Speak your answer..."
                disabled={isTyping}
                className="w-full pl-5 pr-14 py-4 bg-gray-50 border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all disabled:opacity-70"
              />
              <button
                type="submit"
                disabled={!input.trim() || isTyping}
                className="absolute right-2 p-2.5 bg-purple-600 text-white rounded-full hover:bg-purple-700 transition disabled:opacity-50 disabled:hover:bg-purple-600"
              >
                <Send size={20} className={isTyping ? "opacity-0" : ""} />
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default function InterviewSessionPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-gray-500">Loading...</div>}>
      <InterviewSessionContent />
    </Suspense>
  );
}
