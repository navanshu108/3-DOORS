import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

interface PuzzleDoor {
  puzzle_id: string;
  category: string;
  question: string;
  question_type: string;
}

interface LevelView {
  level_number: number;
  title: string;
  doors: PuzzleDoor[];
}

export default function GamePage() {
  const navigate = useNavigate();
  const [level, setLevel] = useState<LevelView | null>(null);
  const [selectedDoor, setSelectedDoor] = useState<PuzzleDoor | null>(null);
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(true);
  const [mistakes, setMistakes] = useState(0);
  const [doorChanges, setDoorChanges] = useState(0);
  const [score, setScore] = useState(0);
  const [runId, setRunId] = useState<string | null>(null);
  const [startTime, setStartTime] = useState<number>(0);
  const [lastGrade, setLastGrade] = useState<string | null>(null);

  useEffect(() => {
    initRun();
  }, []);

  const initRun = async () => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/runs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'ngrok-skip-browser-warning': 'true' },
        body: JSON.stringify({ user_id: 1 })
      });
      const data = await res.json();
      setRunId(data.run_id);
      fetchLevel(data.run_id);
    } catch (e) {
      console.error(e);
      setLoading(false);
    }
  };

  const fetchLevel = async (rId: string) => {
    setLoading(true);
    setLastGrade(null);
    setSelectedDoor(null);
    setAnswer('');
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/runs/${rId}/level`, {
        headers: { 'ngrok-skip-browser-warning': 'true' }
      });
      const data = await res.json();
      setLevel(data);
      setStartTime(Date.now());
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };



  const handleAbandon = async () => {
    if (!runId || !selectedDoor) return;
    const confirm = window.confirm("Leaving this puzzle will deduct 1 point. Continue?");
    if (!confirm) return;
    
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/runs/${runId}/abandon`, { 
        method: 'POST',
        headers: { 'ngrok-skip-browser-warning': 'true' }
      });
      const data = await res.json();
      setScore(data.run_state.score);
      setDoorChanges(data.run_state.door_changes);
      setSelectedDoor(null);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!runId || !selectedDoor) return;

    const timeTaken = (Date.now() - startTime) / 1000;

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/runs/${runId}/attempt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'ngrok-skip-browser-warning': 'true' },
        body: JSON.stringify({
          puzzle_id: selectedDoor.puzzle_id,
          answer,
          time_taken: timeTaken
        })
      });
      const data = await res.json();
      
      if (!data.correct) {
        alert("INCORRECT! -1 Point");
        setScore(data.run_state.score);
        setMistakes(data.run_state.mistakes);
      }
      
      if (data.correct) {
        setScore(data.run_state.score);
        setLastGrade(data.grade);
        if (data.run_state.current_level > 5) {
          navigate('/results', { state: { 
            score: data.run_state.score, 
            mistakes: data.run_state.mistakes, 
            doorChanges: data.run_state.door_changes,
            levelsCleared: data.run_state.current_level - 1 
          }});
        } else {
          setTimeout(() => fetchLevel(runId), 1500);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  if (loading || !level) {
    return <div className="min-h-screen flex items-center justify-center text-xl animate-pulse text-green-500 font-mono">Initializing System...</div>;
  }

  return (
    <div className="min-h-screen flex flex-col p-6 max-w-6xl mx-auto text-green-500 font-mono relative" style={{ perspective: '1200px' }}>
      
      {/* Background Graphic from user request */}
      <div className="fixed inset-0 z-[-1] pointer-events-none">
        <img alt="Background Asset" className="w-full h-full object-cover object-center filter brightness-[0.4] contrast-[1.1] scale-105" src="https://lh3.googleusercontent.com/aida-public/AB6AXuD6KcwEFiwVBEGQaUtOxicnWERAkYn0_58HfDBUyXiT5rOtqIjQ4fDN3GeWYKBmAaK-A1qAtEblzLQsWv33aNxaZDBLvIj0TLurWhKahDvMCEKd7kXbgSSZcY3lLcOyfmgxN2qDLKCDHG3u-UnKXE0pegHM687R0uONuT0hPtUMVtpck1IqVARYZZ6J9ulnVi1Lf4Dn4M0HIuPM-hXhG--hY27w248Cp5DCgIFxeDn8LLsPGW8NPNf6ZQ"/>
        <div className="absolute inset-0 bg-black/60"></div>
      </div>

      {/* HUD */}
      <div className="flex justify-between items-center border-b border-green-500/30 pb-4 mb-12">
        <div>
          <h2 className="text-2xl font-bold tracking-widest">3 DOORS</h2>
          <div className="text-sm text-green-500/60">RUN {runId}</div>
        </div>
        <div className="text-center">
           <div className="text-3xl font-bold text-green-400">{score.toLocaleString()} PTS</div>
           <div className="text-xs tracking-widest text-green-500/60">CURRENT SCORE</div>
        </div>
        <div className="text-right">
          <div className="text-xl">LEVEL {level.level_number.toString().padStart(2, '0')} / 05</div>
          <div className="text-sm text-red-500/80">ERRORS: {mistakes}</div>
          <div className="text-sm text-orange-500/80">CHANGES: {doorChanges}</div>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {lastGrade ? (
          <motion.div 
            key="grade"
            initial={{ opacity: 0, scale: 0.5, rotateX: 45 }}
            animate={{ opacity: 1, scale: 1, rotateX: 0 }}
            exit={{ opacity: 0, scale: 1.5 }}
            className="flex-1 flex flex-col items-center justify-center"
          >
            <div className="text-9xl font-bold text-green-400 drop-shadow-[0_0_50px_rgba(34,197,94,0.8)]">
              {lastGrade}
            </div>
            <div className="text-xl mt-4 tracking-widest text-green-300">GRADE</div>
          </motion.div>
        ) : !selectedDoor ? (
          <motion.div 
            key="doors"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex-1 flex flex-col items-center justify-center relative"
          >
            <h3 className="text-2xl mb-12 font-bold tracking-widest text-center">ANALYZE AND SELECT</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-12 w-full max-w-4xl" style={{ transformStyle: 'preserve-3d' }}>
              {level.doors.map((door, idx) => (
                <motion.div
                  key={door.puzzle_id}
                  whileHover={{ 
                    scale: 1.1, 
                    rotateY: -15, 
                    rotateX: 5,
                    boxShadow: '-15px 15px 30px rgba(34,197,94,0.2)',
                    borderColor: 'rgba(34,197,94,0.8)' 
                  }}
                  onClick={() => setSelectedDoor(door)}
                  className="border-2 border-green-500/40 p-6 flex flex-col cursor-pointer bg-black/80 backdrop-blur min-h-[350px] transition-all relative overflow-hidden"
                  style={{ transformStyle: 'preserve-3d' }}
                >
                  <div className="absolute inset-0 bg-gradient-to-b from-green-500/10 to-transparent pointer-events-none" />
                  
                  <div className="flex justify-between items-center mb-6 border-b border-green-500/30 pb-2 relative z-10" style={{ transform: 'translateZ(20px)' }}>
                    <span className="text-xl font-bold drop-shadow-[0_0_5px_rgba(34,197,94,0.8)]">DOOR 0{idx + 1}</span>
                    <span className="text-xs uppercase tracking-widest text-green-400/60">UNKNOWN</span>
                  </div>
                  <div className="flex-1 flex items-center justify-center relative z-10" style={{ transform: 'translateZ(40px)' }}>
                    <p className="text-6xl opacity-30 font-bold drop-shadow-[0_0_10px_rgba(34,197,94,0.5)]">?</p>
                  </div>
                  <div className="mt-4 text-center border-t border-green-500/30 pt-4 text-sm text-green-500/80 relative z-10 font-bold" style={{ transform: 'translateZ(20px)' }}>
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
            transition={{ duration: 0.3 }}
            className="flex-1 flex flex-col max-w-2xl mx-auto w-full z-10 relative"
          >
            <button 
              onClick={handleAbandon}
              className="text-left mb-8 text-sm text-red-500/60 hover:text-red-400 uppercase tracking-widest font-bold"
            >
              ← ABANDON PUZZLE (-1 PT)
            </button>
            
            <div className="border border-green-500 p-10 bg-black/90 shadow-[0_0_50px_rgba(34,197,94,0.2)] relative backdrop-blur">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-green-500 to-transparent"></div>
              
              <div className="flex justify-between items-end mb-8 border-b border-green-500/30 pb-4">
                <div>
                  <div className="text-xs text-green-500/60 mb-1 tracking-widest">CATEGORY</div>
                  <h3 className="text-2xl font-bold">{selectedDoor?.category || 'UNKNOWN'}</h3>
                </div>
              </div>

              <div className="bg-green-500/5 p-6 rounded mb-8 font-mono text-sm whitespace-pre-wrap leading-relaxed border border-green-500/20">
                {selectedDoor ? selectedDoor.question : 'Loading...'}
              </div>

              <form onSubmit={handleSubmit} className="flex flex-col space-y-4">
                <input 
                  type="text" 
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  className="bg-black border border-green-500/50 p-4 rounded text-green-400 font-mono focus:outline-none focus:border-green-400 focus:shadow-[0_0_15px_rgba(34,197,94,0.3)] text-lg"
                  placeholder="> enter_answer_"
                  required 
                  autoFocus
                />
                <button 
                  type="submit" 
                  className="bg-green-500/20 hover:bg-green-500 text-green-500 hover:text-black border border-green-500 font-bold py-4 rounded tracking-widest transition-colors"
                >
                  EXECUTE
                </button>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
