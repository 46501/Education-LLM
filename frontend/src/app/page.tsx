"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, APIError } from "../lib/api";

export default function Home() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLogin, setIsLogin] = useState(true);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const endpoint = isLogin ? "/auth/login" : "/auth/register";
    try {
      const data = await apiFetch<any>(endpoint, {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      if (isLogin) {
        localStorage.setItem("token", data.access_token);
        router.push("/dashboard");
      } else {
        setIsLogin(true);
      }
    } catch (err: any) {
      if (err instanceof APIError) {
        alert(err.message);
      } else {
        alert("An unexpected error occurred. Please try again.");
      }
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="w-full max-w-md p-8 bg-surface rounded-lg shadow-md border border-border">
        <h1 className="text-2xl font-bold mb-6 text-center text-foreground">
          {isLogin ? "Welcome Back" : "Create Account"}
        </h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground/80">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-1 w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-primary focus:border-primary text-foreground"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground/80">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="mt-1 w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-primary focus:border-primary text-foreground"
            />
          </div>
          <button
            type="submit"
            className="w-full bg-primary text-white py-2 rounded-md hover:bg-primary-hover transition"
          >
            {isLogin ? "Sign In" : "Sign Up"}
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-muted">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-primary hover:underline"
          >
            {isLogin ? "Sign up" : "Sign in"}
          </button>
        </p>
      </div>
    </div>
  );
}
