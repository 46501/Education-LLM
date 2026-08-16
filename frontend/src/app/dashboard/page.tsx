"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Target, TrendingUp, BookOpen, Clock, Activity, Calendar } from "lucide-react";
import Link from "next/link";

export default function Dashboard() {
  const router = useRouter();
  const [userName, setUserName] = useState("Student");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/");
    }
    // In a real app, fetch user profile to get name
  }, [router]);

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-7xl mx-auto space-y-8 animate-in">
      
      {/* Welcome Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
            Good morning, {userName}
          </h1>
          <p className="text-gray-500 mt-1 text-lg">
            Here's your learning overview for today.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link 
            href="/chat"
            className="bg-indigo-600 text-white px-5 py-2.5 rounded-lg font-medium hover:bg-indigo-700 transition shadow-sm premium-shadow flex items-center gap-2"
          >
            Ask AI Tutor
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Today's Focus */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-xl font-bold text-gray-900">Today's Focus</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white p-6 rounded-2xl border border-gray-100 premium-shadow-hover transition cursor-pointer group">
              <div className="w-12 h-12 bg-amber-100 text-amber-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Target size={24} />
              </div>
              <h3 className="font-semibold text-gray-900 text-lg mb-1">Priority Revision</h3>
              <p className="text-gray-500 text-sm mb-4">You have 3 weak topics that need review before your mock exam.</p>
              <span className="text-indigo-600 font-medium text-sm group-hover:text-indigo-700">Start session &rarr;</span>
            </div>
            
            <div className="bg-white p-6 rounded-2xl border border-gray-100 premium-shadow-hover transition cursor-pointer group">
              <div className="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Activity size={24} />
              </div>
              <h3 className="font-semibold text-gray-900 text-lg mb-1">Recommended Practice</h3>
              <p className="text-gray-500 text-sm mb-4">Complete 10 questions on Python Data Structures to boost your mastery.</p>
              <span className="text-indigo-600 font-medium text-sm group-hover:text-indigo-700">Start practice &rarr;</span>
            </div>
          </div>

          <div className="bg-gradient-to-br from-indigo-900 to-purple-900 rounded-2xl p-8 text-white relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-5 rounded-full blur-3xl transform translate-x-1/2 -translate-y-1/2"></div>
            <div className="relative z-10">
              <span className="inline-block px-3 py-1 bg-white/20 rounded-full text-xs font-semibold tracking-wider uppercase mb-3">Next Milestone</span>
              <h3 className="text-2xl font-bold mb-2">AWS Solutions Architect Mock Exam</h3>
              <p className="text-indigo-100 mb-6 max-w-md">Your readiness score is 68%. You need a 75% to hit your target. Keep pushing!</p>
              <Link href="/exams" className="bg-white text-indigo-900 px-6 py-2.5 rounded-lg font-medium hover:bg-gray-50 transition shadow-sm">
                View Exam Plan
              </Link>
            </div>
          </div>
        </div>

        {/* Sidebar widgets */}
        <div className="space-y-6">
          <h2 className="text-xl font-bold text-gray-900">Your Progress</h2>
          <div className="bg-white rounded-2xl border border-gray-100 p-6 space-y-6 premium-shadow">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-500 font-medium">Overall Mastery</span>
                <span className="text-indigo-600 font-bold">72%</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2.5">
                <div className="bg-indigo-600 h-2.5 rounded-full" style={{ width: '72%' }}></div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-100">
              <div>
                <p className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-1">Questions</p>
                <p className="text-2xl font-bold text-gray-900">342</p>
              </div>
              <div>
                <p className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-1">Accuracy</p>
                <p className="text-2xl font-bold text-gray-900">68%</p>
              </div>
            </div>
          </div>

          <h2 className="text-xl font-bold text-gray-900 pt-2">Recent Activity</h2>
          <div className="bg-white rounded-2xl border border-gray-100 p-6 space-y-4">
            {[
              { title: "Completed Python Quiz", time: "2 hours ago", icon: BookOpen, color: "text-blue-500", bg: "bg-blue-50" },
              { title: "Uploaded 'System Design.pdf'", time: "Yesterday", icon: Calendar, color: "text-purple-500", bg: "bg-purple-50" },
              { title: "Mock Interview: Frontend", time: "2 days ago", icon: TrendingUp, color: "text-emerald-500", bg: "bg-emerald-50" }
            ].map((activity, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${activity.bg} ${activity.color}`}>
                  <activity.icon size={16} />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                  <p className="text-xs text-gray-500">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
