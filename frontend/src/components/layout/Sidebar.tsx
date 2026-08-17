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
    <div className="h-full bg-surface border-r border-border flex flex-col shadow-sm transition-colors duration-300">
      <div className="h-16 flex items-center justify-between px-6 border-b border-border shrink-0">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="bg-primary p-1.5 rounded-lg text-white shadow-sm">
            <BrainCircuit size={20} />
          </div>
          <span className="font-bold text-foreground tracking-tight text-lg">Education LLM</span>
        </Link>
        {onClose && (
          <button onClick={onClose} className="lg:hidden text-muted hover:text-foreground">
            <X size={20} />
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto py-6 px-4 space-y-8">
        {navGroups.map((group) => (
          <div key={group.title}>
            <h3 className="px-3 text-xs font-semibold text-muted uppercase tracking-wider mb-3">
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
                        ? "bg-primary/10 text-primary font-medium" 
                        : "text-muted hover:bg-surface-hover hover:text-foreground"
                    }`}
                  >
                    <Icon size={18} className={isActive ? "text-primary" : "text-muted"} />
                    <span className="text-sm">{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-border">
        <button 
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 w-full rounded-lg text-muted hover:bg-error-bg hover:text-error transition-all duration-200"
        >
          <LogOut size={18} className="text-muted" />
          <span className="text-sm font-medium">Log out</span>
        </button>
      </div>
    </div>
  );
}
