"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

interface Message {
  id: string;
  role: string;
  content: string;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/");
    }
  }, [router]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    // Initialize Speech Recognition
    if (typeof window !== "undefined") {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;

        recognitionRef.current.onresult = (event: any) => {
          let currentTranscript = "";
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              setInput((prev) => prev + transcript + " ");
            } else {
              currentTranscript += transcript;
            }
          }
          // Note: for simplicity we append final results to input. 
          // Interim results could be shown differently if desired.
        };

        recognitionRef.current.onerror = (event: any) => {
          console.error("Speech recognition error", event.error);
          setIsListening(false);
        };
        
        recognitionRef.current.onend = () => {
          setIsListening(false);
        };
      }
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      if (!recognitionRef.current) {
        alert("Speech recognition is not supported in this browser.");
        return;
      }
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (e) {
        console.error(e);
      }
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    if (isListening) {
      toggleListening();
    }

    const token = localStorage.getItem("token");
    const userMessage: Message = { id: Date.now().toString(), role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ content: userMessage.content }),
      });

      if (!response.ok) {
        if (response.status === 401) router.push("/");
        throw new Error("Chat error");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder("utf-8");
      
      let aiMessageContent = "";
      const aiMessageId = (Date.now() + 1).toString();
      
      setMessages((prev) => [...prev, { id: aiMessageId, role: "tutor", content: "" }]);

      while (reader) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.replace("data: ", "");
            if (dataStr) {
              const data = JSON.parse(dataStr);
              aiMessageContent += data.content;
              setMessages((prev) => 
                prev.map(msg => msg.id === aiMessageId ? { ...msg, content: aiMessageContent } : msg)
              );
            }
          }
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex h-full flex-col max-w-5xl mx-auto w-full">
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center max-w-lg mx-auto pb-20">
            <div className="w-16 h-16 bg-indigo-100 text-indigo-600 rounded-2xl flex items-center justify-center mb-6">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2a2 2 0 0 1 2 2c-.11.66-.54 1.25-1.16 1.58A3.01 3.01 0 0 0 11 8.5c0 1.25.79 2.36 1.95 2.82A2 2 0 0 1 14 13h0a2 2 0 0 1-2 2c-.11.66-.54 1.25-1.16 1.58A3.01 3.01 0 0 0 11 19.5c0 1.25.79 2.36 1.95 2.82A2 2 0 0 1 14 24"></path><path d="M10 2a2 2 0 0 0-2 2c.11.66.54 1.25 1.16 1.58A3.01 3.01 0 0 1 11 8.5c0 1.25-.79 2.36-1.95 2.82A2 2 0 0 0 8 13h0a2 2 0 0 0 2 2c.11.66.54 1.25 1.16 1.58A3.01 3.01 0 0 1 11 19.5c0 1.25-.79 2.36-1.95 2.82A2 2 0 0 0 8 24"></path></svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">How can I help you learn today?</h2>
            <p className="text-gray-500 mb-8">Ask a question, request a summary, or have me explain a difficult concept from your study materials.</p>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
              {["Explain quantum physics simply", "Quiz me on Python basics", "Summarize my uploaded notes", "Give me a coding example"].map((suggestion) => (
                <button 
                  key={suggestion}
                  onClick={() => setInput(suggestion)}
                  className="bg-white border border-gray-200 p-3 rounded-xl text-sm text-gray-600 hover:border-indigo-300 hover:text-indigo-700 transition text-left"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] md:max-w-2xl p-4 rounded-2xl shadow-sm leading-relaxed ${
              msg.role === 'user' 
                ? 'bg-indigo-600 text-white rounded-br-none' 
                : 'bg-white text-gray-800 border border-gray-100 rounded-bl-none'
            }`}>
              <div className="whitespace-pre-wrap text-[15px]">{msg.content}</div>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-white p-4 rounded-2xl rounded-bl-none border border-gray-100 shadow-sm flex gap-1.5 items-center">
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-transparent border-t-0 mb-4 shrink-0">
        <form onSubmit={handleSend} className="relative max-w-3xl mx-auto shadow-sm rounded-2xl bg-white border border-gray-200 overflow-hidden focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-transparent transition-all">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend(e as any);
              }
            }}
            placeholder={isListening ? "Listening..." : "Message AI Tutor..."}
            className="w-full max-h-32 min-h-[56px] p-4 pr-24 resize-none focus:outline-none text-gray-800 dark:text-gray-100 bg-transparent"
            rows={1}
          />
          <div className="absolute right-2 bottom-2 flex items-center gap-1">
            <button
              type="button"
              onClick={toggleListening}
              className={`p-2.5 rounded-lg transition-colors ${
                isListening 
                  ? "bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400" 
                  : "text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
              }`}
            >
              {isListening ? (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="1" y1="1" x2="23" y2="23"></line><path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"></path><path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>
              ) : (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="22"></line></svg>
              )}
            </button>
            <button
              type="submit"
              disabled={isTyping || (!input.trim() && !isListening)}
              className="p-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:hover:bg-indigo-600 transition"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            </button>
          </div>
        </form>
        <p className="text-center text-xs text-gray-400 mt-3">AI Tutor can make mistakes. Verify important information.</p>
      </div>
    </div>
  );
}
