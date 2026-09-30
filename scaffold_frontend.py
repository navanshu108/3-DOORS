import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content.strip() + '\n')

write_file('frontend/src/App.tsx', """
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import GamePage from './pages/GamePage';
import ResultsPage from './pages/ResultsPage';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#0a0a0c] text-green-400 font-mono selection:bg-green-500/30 selection:text-green-200">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/game" element={<GamePage />} />
          <Route path="/results" element={<ResultsPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
""")

write_file('frontend/src/pages/LandingPage.tsx', """
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8 text-center relative overflow-hidden">
      
      {/* Background grid */}
      <div className="absolute inset-0 bg-[url('https://transparenttextures.com/patterns/cubes.png')] opacity-10 pointer-events-none"></div>

      <motion.h1 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
        className="text-6xl md:text-8xl font-bold mb-4 tracking-tighter"
      >
        3 DOORS
      </motion.h1>
      
      <motion.h3 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5, duration: 1 }}
        className="text-xl md:text-2xl mb-8 tracking-widest uppercase text-green-300/80"
      >
        Engineering Intelligence Challenge
      </motion.h3>

      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1, duration: 1 }}
        className="text-lg md:text-xl mb-12 max-w-lg text-green-200/60"
      >
        <p>Three problems.</p>
        <p>One efficient path.</p>
        <p className="mt-4 italic">Don't solve everything. Choose wisely.</p>
      </motion.div>

      <div className="flex gap-4 mb-16 z-10">
        <button 
          onClick={() => navigate('/game')}
          className="px-8 py-3 bg-green-500/20 border border-green-500 text-green-400 font-bold hover:bg-green-500 hover:text-black transition-all shadow-[0_0_15px_rgba(34,197,94,0.3)] hover:shadow-[0_0_30px_rgba(34,197,94,0.6)]"
        >
          START CHALLENGE
        </button>
        <button className="px-8 py-3 bg-transparent border border-gray-600 text-gray-400 font-bold hover:text-white hover:border-gray-400 transition-all">
          HOW IT WORKS
        </button>
      </div>

      {/* Door visual */}
      <div className="flex gap-6 z-10">
        {[1, 2, 3].map((num) => (
          <motion.div 
            key={num}
            whileHover={{ y: -10, boxShadow: '0 0 20px rgba(34,197,94,0.5)' }}
            className="w-24 h-36 border border-green-500/50 flex flex-col items-center justify-center bg-black/50 backdrop-blur-sm relative"
          >
            <span className="absolute top-2 text-xs text-green-500/50">0{num}</span>
            <span className="text-2xl font-bold">???</span>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
""")

write_file('frontend/src/pages/GamePage.tsx', """
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

// Mock types
type Door = {
  puzzle_id: string;
  category: string;
  question: string;
  question_type: string;
};

type Level = {
  level_number: int;
  title: string;
  doors: Door[];
};

export default function GamePage() {
  const navigate = useNavigate();
  const [level, setLevel] = useState<Level | null>(null);
  const [selectedDoor, setSelectedDoor] = useState<Door | null>(null);
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(true);
  const [mistakes, setMistakes] = useState(0);
  const [runId, setRunId] = useState<string | null>(null);

  useEffect(() => {
    // Start run
    const start = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/runs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: 1 })
        });
        const data = await res.json();
        setRunId(data.run_id);
        fetchLevel(data.run_id);
      } catch (e) {
        console.error(e);
      }
    };
    start();
  }, []);

  const fetchLevel = async (id: string) => {
    setLoading(true);
    setSelectedDoor(null);
    setAnswer('');
    try {
      const res = await fetch(`http://localhost:8000/api/runs/${id}/level`);
      const data = await res.json();
      setLevel(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!selectedDoor || !runId) return;
    try {
      const res = await fetch(`http://localhost:8000/api/runs/${runId}/attempt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          puzzle_id: selectedDoor.puzzle_id,
          answer: answer,
          time_taken: 5.0
        })
      });
      const data = await res.json();
      if (data.correct) {
        if (data.run_state.current_level > 15) {
          navigate('/results');
        } else {
          fetchLevel(runId);
        }
      } else {
        setMistakes(data.run_state.mistakes);
        // Error animation could go here
        alert('Incorrect. Try again or choose a different door.');
      }
    } catch (e) {
      console.error(e);
    }
  };

  if (loading || !level) {
    return <div className="min-h-screen flex items-center justify-center text-xl animate-pulse">Initializing System...</div>;
  }

  return (
    <div className="min-h-screen flex flex-col p-6 max-w-6xl mx-auto">
      {/* HUD */}
      <div className="flex justify-between items-center border-b border-green-500/30 pb-4 mb-12">
        <div>
          <h2 className="text-2xl font-bold tracking-widest">3 DOORS</h2>
          <div className="text-sm text-green-500/60">RUN {runId}</div>
        </div>
        <div className="text-right">
          <div className="text-xl">LEVEL {level.level_number.toString().padStart(2, '0')} / 15</div>
          <div className="text-sm text-red-500/80">ERRORS: {mistakes}</div>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {!selectedDoor ? (
          <motion.div 
            key="doors"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex-1 flex flex-col items-center justify-center"
          >
            <h3 className="text-2xl mb-12 font-bold tracking-widest text-center">ANALYZE AND SELECT</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full">
              {level.doors.map((door, idx) => (
                <motion.div
                  key={door.puzzle_id}
                  whileHover={{ scale: 1.05, borderColor: 'rgba(34,197,94,0.8)' }}
                  onClick={() => setSelectedDoor(door)}
                  className="border border-green-500/40 p-6 flex flex-col cursor-pointer bg-black/40 backdrop-blur min-h-[300px] transition-colors hover:bg-green-900/10"
                >
                  <div className="flex justify-between items-center mb-6 border-b border-green-500/20 pb-2">
                    <span className="text-xl font-bold">DOOR 0{idx + 1}</span>
                    <span className="text-xs uppercase tracking-widest text-green-400/60">{door.category}</span>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm opacity-80 whitespace-pre-wrap font-sans">{door.question}</p>
                  </div>
                  <div className="mt-4 text-center border-t border-green-500/20 pt-4 text-sm text-green-500/50">
                    CLICK TO ENTER
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        ) : (
          <motion.div 
            key="puzzle"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex-1 flex flex-col max-w-2xl mx-auto w-full"
          >
            <button 
              onClick={() => setSelectedDoor(null)}
              className="text-left mb-8 text-sm text-green-500/60 hover:text-green-400"
            >
              ← RETURN TO DOORS
            </button>
            
            <div className="border border-green-500 p-8 bg-black/60 shadow-[0_0_30px_rgba(34,197,94,0.15)] relative">
              <div className="absolute top-0 right-0 p-2 text-xs text-green-500/40">{selectedDoor.category}</div>
              
              <h3 className="text-xl mb-8 font-bold border-b border-green-500/30 pb-4">TERMINAL // INPUT REQUIRED</h3>
              
              <div className="mb-8 whitespace-pre-wrap font-sans text-lg">
                {selectedDoor.question}
              </div>

              <div className="flex gap-4 mt-12">
                <input 
                  type="text" 
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && submitAnswer()}
                  className="flex-1 bg-transparent border-b-2 border-green-500/50 p-2 focus:outline-none focus:border-green-400 text-xl placeholder-green-900"
                  placeholder="Enter solution..."
                  autoFocus
                />
                <button 
                  onClick={submitAnswer}
                  className="px-8 py-2 bg-green-500/20 border border-green-500 hover:bg-green-500 hover:text-black font-bold transition-colors"
                >
                  SUBMIT
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
""")

write_file('frontend/src/pages/ResultsPage.tsx', """
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function ResultsPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6">
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="border-2 border-green-500 p-12 bg-black/50 max-w-2xl w-full text-center shadow-[0_0_50px_rgba(34,197,94,0.2)]"
      >
        <h1 className="text-5xl font-bold mb-4 tracking-tighter">RUN COMPLETE</h1>
        <div className="text-3xl text-white mb-12">08:42.31</div>
        
        <div className="text-xl mb-12 tracking-widest">15 / 15 LEVELS CLEARED</div>
        
        <div className="grid grid-cols-2 gap-8 text-left max-w-sm mx-auto mb-16 border-y border-green-500/30 py-8">
          <div className="text-green-500/60">ACCURACY</div>
          <div className="text-right font-bold text-xl">93%</div>
          
          <div className="text-green-500/60">EFFICIENCY</div>
          <div className="text-right font-bold text-xl">87%</div>
          
          <div className="text-green-500/60">AVG TIME</div>
          <div className="text-right font-bold text-xl">34.8s</div>
          
          <div className="text-green-500/60">MISTAKES</div>
          <div className="text-right font-bold text-xl text-red-400">2</div>
        </div>
        
        <div className="flex flex-col gap-4 max-w-xs mx-auto">
          <button className="px-6 py-3 border border-green-500 bg-green-500/10 hover:bg-green-500 hover:text-black font-bold transition-colors">
            VIEW LEADERBOARD
          </button>
          <button className="px-6 py-3 border border-green-500/50 text-green-500/80 hover:bg-green-500/20 font-bold transition-colors">
            CHALLENGE FRIEND
          </button>
          <button 
            onClick={() => navigate('/')}
            className="px-6 py-3 border border-green-500/50 text-green-500/80 hover:bg-green-500/20 font-bold transition-colors"
          >
            PLAY AGAIN
          </button>
        </div>
      </motion.div>
    </div>
  );
}
""")

write_file('frontend/package.json', """
{
  "name": "local-research-agent-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.26.2",
    "framer-motion": "^11.5.6",
    "lucide-react": "^0.441.0",
    "tailwind-merge": "^2.5.2",
    "clsx": "^2.1.1"
  },
  "devDependencies": {
    "@eslint/js": "^9.9.0",
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.20",
    "eslint": "^9.9.0",
    "eslint-plugin-react-hooks": "^5.1.0-rc.0",
    "eslint-plugin-react-refresh": "^0.4.9",
    "globals": "^15.9.0",
    "postcss": "^8.4.47",
    "tailwindcss": "^3.4.12",
    "typescript": "^5.5.3",
    "typescript-eslint": "^8.0.1",
    "vite": "^5.4.1"
  }
}
""")

print("Frontend scaffolded successfully")
