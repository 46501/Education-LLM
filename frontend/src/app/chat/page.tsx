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
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/");
    }
  }, [router]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

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
    <div className="flex h-screen bg-gray-50">
      <div className="w-64 bg-gray-900 text-white p-4 hidden md:block flex flex-col">
        <h2 className="text-xl font-bold mb-4">Education LLM</h2>
        <nav className="space-y-2 flex-1">
          <a href="#" className="block py-2 px-4 bg-gray-800 rounded">AI Tutor</a>
          <a href="#" className="block py-2 px-4 hover:bg-gray-800 rounded">Quizzes</a>
        </nav>
        <div className="mt-8 border-t border-gray-700 pt-4">
          <h3 className="text-sm font-semibold text-gray-400 uppercase mb-2">Study Material</h3>
          <input 
            type="file" 
            className="w-full text-sm text-gray-300 file:mr-2 file:py-1 file:px-2 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-gray-700 file:text-white hover:file:bg-gray-600 cursor-pointer"
            onChange={async (e) => {
              if (e.target.files && e.target.files[0]) {
                const file = e.target.files[0];
                const token = localStorage.getItem("token");
                const formData = new FormData();
                formData.append("file", file);
                try {
                  alert("Uploading...");
                  const res = await fetch("http://localhost:8000/api/documents/upload", {
                    method: "POST",
                    headers: { Authorization: `Bearer ${token}` },
                    body: formData
                  });
                  if (res.ok) alert("Uploaded successfully. AI can now reference it!");
                  else alert("Failed to upload document.");
                } catch (err) {
                  alert("Upload error.");
                }
              }
            }}
          />
        </div>
      </div>
      
      <div className="flex-1 flex flex-col">
        <header className="bg-white shadow-sm p-4">
          <h1 className="text-xl font-semibold text-gray-800">AI Tutor</h1>
        </header>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-20">
              <h2 className="text-2xl font-semibold mb-2">Hello! I am your AI Tutor.</h2>
              <p>What would you like to learn today?</p>
            </div>
          )}
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-2xl p-4 rounded-lg shadow-sm ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white text-gray-800 border border-gray-200'}`}>
                {msg.content}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-800 p-4 rounded-lg border border-gray-200 shadow-sm animate-pulse">
                Thinking...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 bg-white border-t border-gray-200">
          <form onSubmit={handleSend} className="flex gap-2 max-w-4xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question..."
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={isTyping}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
