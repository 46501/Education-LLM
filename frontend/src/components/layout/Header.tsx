"use client";

import { Menu, Bell, Search, Sun, Moon, Flame, Zap } from "lucide-react";
import { usePathname } from "next/navigation";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export default function Header({ onMenuClick }: { onMenuClick: () => void }) {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const getPageTitle = () => {
    if (pathname.includes("/chat")) return "AI Tutor";
    if (pathname.includes("/quizzes")) return "Quizzes";
    if (pathname.includes("/practice")) return "Practice";
    if (pathname.includes("/progress")) return "Progress";
    if (pathname.includes("/exams")) return "Exams";
    if (pathname.includes("/interview")) return "Interviews";
    if (pathname.includes("/flashcards")) return "Flashcards";
    if (pathname.includes("/dashboard")) return "Dashboard";
    return "Education LLM";
  };

  return (
    <header className="bg-surface border-b border-border h-16 flex items-center justify-between px-4 lg:px-8 z-10 shrink-0 transition-colors duration-300">
      <div className="flex items-center gap-4">
        <button 
          onClick={onMenuClick}
          className="lg:hidden p-2 text-muted hover:bg-surface-hover rounded-md transition"
        >
          <Menu size={20} />
        </button>
        <h2 className="text-xl font-semibold text-foreground hidden sm:block">
          {getPageTitle()}
        </h2>
      </div>

      <div className="flex items-center gap-3 md:gap-5">
        
        {/* Gamification Stats */}
        <div className="hidden sm:flex items-center gap-4 mr-2 bg-muted-bg px-4 py-1.5 rounded-full border border-border">
          <div className="flex items-center gap-1.5 text-orange-500 font-bold text-sm">
            <Flame size={16} className="fill-orange-500" />
            <span>3 Day</span>
          </div>
          <div className="w-px h-4 bg-border"></div>
          <div className="flex items-center gap-1.5 text-indigo-500 font-bold text-sm">
            <Zap size={16} className="fill-indigo-500" />
            <span>120 XP</span>
          </div>
        </div>

        <div className="hidden md:flex items-center relative">
          <Search size={18} className="absolute left-3 text-muted" />
          <input 
            type="text" 
            placeholder="Search topics..." 
            className="pl-10 pr-4 py-2 bg-background border border-border rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 w-48 lg:w-64 transition-all text-foreground"
          />
        </div>

        {/* Theme Toggle */}
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="p-2 text-muted hover:text-primary hover:bg-primary-light/50 rounded-full transition relative"
        >
          {mounted && theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
        </button>
        
        <button className="p-2 text-muted hover:text-primary hover:bg-primary-light/50 rounded-full transition relative">
          <Bell size={20} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-surface"></span>
        </button>
        
        <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 text-white flex items-center justify-center font-semibold text-sm shadow-sm cursor-pointer border border-white/20">
          S
        </div>
      </div>
    </header>
  );
}
