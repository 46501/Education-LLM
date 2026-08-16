"use strict";
"use client";

import { useState, useEffect } from "react";
import { Layers, Plus, Play, BrainCircuit, Search } from "lucide-react";
import Link from "next/link";

interface Deck {
  id: string;
  title: string;
  description: string;
  flashcards: any[];
}

export default function FlashcardsDashboard() {
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Mock data for initial UI before backend integration is fully stable
  useEffect(() => {
    // In a real implementation this would fetch from /api/flashcards/decks
    setTimeout(() => {
      setDecks([
        {
          id: "1",
          title: "Machine Learning Basics",
          description: "Core concepts of supervised and unsupervised learning.",
          flashcards: Array(25).fill({})
        },
        {
          id: "2",
          title: "Data Structures",
          description: "Arrays, Trees, Graphs, and Hash Tables.",
          flashcards: Array(42).fill({})
        }
      ]);
      setLoading(false);
    }, 500);
  }, []);

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-8 animate-in">
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <Layers className="text-indigo-600 dark:text-indigo-400" size={32} />
            Flashcard Decks
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2">
            Master concepts with spaced repetition learning.
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input 
              type="text" 
              placeholder="Search decks..." 
              className="pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white w-full md:w-64 transition-shadow premium-shadow-hover"
            />
          </div>
          <button className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium transition-colors premium-shadow-hover shrink-0">
            <Plus size={18} />
            <span>New Deck</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white dark:bg-gray-800 rounded-xl p-6 h-48 border border-gray-100 dark:border-gray-700 animate-pulse">
              <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-4"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full mb-2"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
            </div>
          ))}
        </div>
      ) : decks.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-12 border border-gray-100 dark:border-gray-700 text-center glass-panel">
          <div className="w-16 h-16 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-full flex items-center justify-center mx-auto mb-4">
            <Layers size={32} />
          </div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">No Decks Yet</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-md mx-auto">
            Create your first flashcard deck or ask the AI Tutor to generate one for you based on a topic.
          </p>
          <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-lg font-medium transition-colors premium-shadow inline-flex items-center gap-2">
            <Plus size={18} />
            Create First Deck
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {decks.map((deck) => (
            <div key={deck.id} className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-100 dark:border-gray-700 premium-shadow hover:premium-shadow-hover transition-all group flex flex-col">
              <div className="flex-1">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-2 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-lg group-hover:scale-110 transition-transform">
                    <BrainCircuit size={24} />
                  </div>
                  <span className="bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs font-semibold px-2.5 py-1 rounded-full">
                    {deck.flashcards.length} cards
                  </span>
                </div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">{deck.title}</h3>
                <p className="text-gray-500 dark:text-gray-400 text-sm line-clamp-2">
                  {deck.description || "No description provided."}
                </p>
              </div>
              
              <div className="mt-6 pt-4 border-t border-gray-100 dark:border-gray-700 flex gap-3">
                <Link 
                  href={`/flashcards/${deck.id}/study`}
                  className="flex-1 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-100 dark:hover:bg-indigo-900/40 py-2 rounded-lg font-medium text-sm flex items-center justify-center gap-2 transition-colors"
                >
                  <Play size={16} />
                  Study Now
                </Link>
                <Link 
                  href={`/flashcards/${deck.id}`}
                  className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg font-medium text-sm transition-colors border border-gray-200 dark:border-gray-600"
                >
                  Edit
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
