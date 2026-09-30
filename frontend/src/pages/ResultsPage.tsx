import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function ResultsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { score, mistakes, doorChanges, levelsCleared } = location.state || { score: 0, mistakes: 0, doorChanges: 0, levelsCleared: 5 };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-[#0a0a0c] text-green-500 font-mono relative">
      
      {/* Background Graphic from user request */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <img alt="Background Asset" className="w-full h-full object-cover object-center filter brightness-[0.3] contrast-[1.1] scale-105" src="https://lh3.googleusercontent.com/aida-public/AB6AXuD6KcwEFiwVBEGQaUtOxicnWERAkYn0_58HfDBUyXiT5rOtqIjQ4fDN3GeWYKBmAaK-A1qAtEblzLQsWv33aNxaZDBLvIj0TLurWhKahDvMCEKd7kXbgSSZcY3lLcOyfmgxN2qDLKCDHG3u-UnKXE0pegHM687R0uONuT0hPtUMVtpck1IqVARYZZ6J9ulnVi1Lf4Dn4M0HIuPM-hXhG--hY27w248Cp5DCgIFxeDn8LLsPGW8NPNf6ZQ"/>
        <div className="absolute inset-0 bg-black/60"></div>
      </div>

      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative z-10 border-2 border-green-500 p-12 bg-black/80 backdrop-blur max-w-2xl w-full text-center shadow-[0_0_50px_rgba(34,197,94,0.2)]"
      >
        <h1 className="text-5xl font-bold mb-4 tracking-tighter text-green-400">RUN COMPLETE</h1>
        <div className="text-3xl text-white mb-12">OVERALL SCORE: {score}</div>
        
        <div className="grid grid-cols-2 gap-8 text-left max-w-md mx-auto mb-16 border-y border-green-500/30 py-8">
          <div className="text-green-500/60 font-bold">LEVELS CLEARED</div>
          <div className="text-right font-bold text-2xl text-green-300">{levelsCleared} / 05</div>
          
          <div className="text-green-500/60 font-bold">WRONG ANSWERS (-1 PT EACH)</div>
          <div className="text-right font-bold text-2xl text-red-400">{mistakes}</div>
          
          <div className="text-green-500/60 font-bold">DOOR CHANGES (-1 PT EACH)</div>
          <div className="text-right font-bold text-2xl text-orange-400">{doorChanges}</div>
        </div>
        
        <div className="flex flex-col gap-4 max-w-xs mx-auto">
          <button className="px-6 py-3 border border-green-500 bg-green-500/10 hover:bg-green-500 hover:text-black font-bold transition-colors">
            VIEW LEADERBOARD
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
