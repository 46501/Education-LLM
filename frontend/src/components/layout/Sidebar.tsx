import { 
  LayoutDashboard, 
  MessageSquare, 
  BookOpen, 
  Target, 
  Award, 
  BrainCircuit,
  TrendingUp,
  FileText,
  X,
  LogOut,
  Layers
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

export default function Sidebar({ onClose }: { onClose?: () => void }) {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/");
  };

  const navGroups = [
    {
      title: "LEARN",
      items: [
        { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
        { label: "AI Tutor", href: "/chat", icon: MessageSquare },
        { label: "Study Material", href: "/material", icon: FileText },
      ]
    },
    {
      title: "PRACTICE",
      items: [
        { label: "Practice", href: "/practice", icon: Target },
        { label: "Quizzes", href: "/quizzes", icon: Award },
        { label: "Flashcards", href: "/flashcards", icon: Layers },
      ]
    },
    {
      title: "TRACK",
      items: [
        { label: "Progress", href: "/progress", icon: TrendingUp },
      ]
    },
    {
      title: "PREPARE",
      items: [
        { label: "Exams", href: "/exams", icon: BookOpen },
        { label: "Interviews", href: "/interview/setup", icon: BrainCircuit },
      ]
    }
  ];

  return (
    <div className="h-full bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col shadow-sm transition-colors duration-300">
      <div className="h-16 flex items-center justify-between px-6 border-b border-gray-100 dark:border-gray-800 shrink-0">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="bg-indigo-600 p-1.5 rounded-lg text-white shadow-sm">
            <BrainCircuit size={20} />
          </div>
          <span className="font-bold text-gray-900 dark:text-white tracking-tight text-lg">Education LLM</span>
        </Link>
        {onClose && (
          <button onClick={onClose} className="lg:hidden text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
            <X size={20} />
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto py-6 px-4 space-y-8">
        {navGroups.map((group) => (
          <div key={group.title}>
            <h3 className="px-3 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-3">
              {group.title}
            </h3>
            <nav className="space-y-1">
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = pathname.startsWith(item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={onClose}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                      isActive 
                        ? "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 font-medium" 
                        : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800/50 hover:text-gray-900 dark:hover:text-gray-200"
                    }`}
                  >
                    <Icon size={18} className={isActive ? "text-indigo-600 dark:text-indigo-400" : "text-gray-400 dark:text-gray-500"} />
                    <span className="text-sm">{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-gray-100 dark:border-gray-800">
        <button 
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 w-full rounded-lg text-gray-600 dark:text-gray-400 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-700 dark:hover:text-red-400 transition-all duration-200"
        >
          <LogOut size={18} className="text-gray-400 dark:text-gray-500" />
          <span className="text-sm font-medium">Log out</span>
        </button>
      </div>
    </div>
  );
}
