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
