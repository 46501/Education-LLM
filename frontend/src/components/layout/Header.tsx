import { Menu, Bell, Search, User } from "lucide-react";
import { usePathname } from "next/navigation";

export default function Header({ onMenuClick }: { onMenuClick: () => void }) {
  const pathname = usePathname();

  // Helper to format pathname into a readable title
  const getPageTitle = () => {
    if (pathname.includes("/chat")) return "AI Tutor";
    if (pathname.includes("/quizzes")) return "Quizzes";
    if (pathname.includes("/practice")) return "Practice";
    if (pathname.includes("/progress")) return "Progress";
    if (pathname.includes("/exams")) return "Exams";
    if (pathname.includes("/interview")) return "Interviews";
    if (pathname.includes("/dashboard")) return "Dashboard";
    return "Education LLM";
  };

  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-4 lg:px-8 z-10 shrink-0">
      <div className="flex items-center gap-4">
        <button 
          onClick={onMenuClick}
          className="lg:hidden p-2 text-gray-500 hover:bg-gray-100 rounded-md transition"
        >
          <Menu size={20} />
        </button>
        <h2 className="text-xl font-semibold text-gray-800 hidden sm:block">
          {getPageTitle()}
        </h2>
      </div>

      <div className="flex items-center gap-3 md:gap-6">
        <div className="hidden md:flex items-center relative">
          <Search size={18} className="absolute left-3 text-gray-400" />
          <input 
            type="text" 
            placeholder="Search topics..." 
            className="pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 w-64 transition-all"
          />
        </div>
        
        <button className="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-full transition relative">
          <Bell size={20} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
        </button>
        
        <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 text-white flex items-center justify-center font-semibold text-sm shadow-sm cursor-pointer">
          S
        </div>
      </div>
    </header>
  );
}
