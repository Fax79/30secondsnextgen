'use client';

import React, { useState, useEffect } from 'react';

interface LoadingProps {
  destination: string;
  curiosity: string;
}

export default function LoadingScreen({ destination, curiosity }: LoadingProps) {
  const [progress, setProgress] = useState(0);

  // Simulazione progresso barra
  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((old) => (old < 95 ? old + 0.5 : old));
    }, 500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 text-[#1a1a1a] relative overflow-hidden" style={{ backgroundColor: '#faf9f6' }}>
      
      {/* Pattern editoriale di sfondo */}
      <div className="absolute inset-0 z-0 pointer-events-none opacity-40" 
           style={{ backgroundImage: 'radial-gradient(#1a1a1a 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
      </div>

      <div className="relative z-10 w-full max-w-md text-center space-y-12">
        
        {/* Header e Progress Bar */}
        <div className="space-y-4">
          <h2 className="text-4xl font-black uppercase tracking-tighter leading-none text-[#1a1a1a]">
            Stiamo creando <br />la tua <span className="text-[#e67e22]">Guida</span>
          </h2>
          <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden">
            <div 
              className="h-full bg-[#e67e22] transition-all duration-500 ease-out" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <p className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400">
            {progress < 40 ? "Accensione motori IA..." : "Impaginazione editoriale in corso..."}
          </p>
        </div>

        {/* Slot Curiosità Dinamica */}
        <div className="bg-white p-8 rounded-3xl shadow-xl border border-gray-100 rotate-1 transform transition-all">
           <span className="block text-[#e67e22] text-[10px] font-black uppercase tracking-widest mb-3 text-center">Lo sapevi?</span>
           <p className="text-xl font-bold leading-tight italic text-center text-[#1a1a1a]">
             {curiosity || `Stiamo scoprendo una curiosità affascinante su ${destination}...`}
           </p>
        </div>

        {/* Slot Affiliazioni (Marketing) */}
        <div className="grid gap-4">
          
          {/* Saily eSIM */}
          <div className="bg-[#1a1a1a] text-white p-5 rounded-2xl flex items-center justify-between hover:scale-[1.02] transition-transform shadow-lg cursor-pointer">
            <div className="text-left">
              <span className="block text-[9px] font-black text-white/50 uppercase tracking-widest">Connessione immediata</span>
              <p className="font-bold">Sconto 5$ con Saily</p>
              <code className="text-[#e67e22] font-black text-xs">Codice: FABIO13455</code>
            </div>
            <div className="bg-white/10 p-3 rounded-xl text-[10px] font-black uppercase tracking-tighter">Attiva</div>
          </div>

          {/* Heymondo Assicurazione */}
          <div className="bg-white border-2 border-[#1a1a1a] p-5 rounded-2xl flex items-center justify-between hover:scale-[1.02] transition-transform shadow-lg cursor-pointer">
            <div className="text-left">
              <span className="block text-[9px] font-black text-gray-400 uppercase tracking-widest">Viaggia Protetto</span>
              <p className="font-bold text-[#1a1a1a]">Assicurazione Heymondo</p>
              <p className="text-[#e67e22] font-black text-xs">-10% Riservato</p>
            </div>
            <div className="bg-[#1a1a1a] text-white p-3 rounded-xl text-[10px] font-black uppercase tracking-tighter">Sconto</div>
          </div>

        </div>

        <p className="text-[10px] font-medium text-gray-400 px-6 leading-relaxed">
          Questa guida è gratuita grazie ai nostri partner. <br />
          Il download inizierà automaticamente tra pochi istanti.
        </p>
      </div>
    </div>
  );
}