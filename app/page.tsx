'use client';

import React, { useState } from 'react';
import LoadingScreen from '@/components/LoadingScreen';

export default function Home() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false); // Stato per il verdetto rapido
  const [isGenerating, setIsGenerating] = useState(false); // Stato per il PDF pesante
  const [curiosity, setCuriosity] = useState("");
  const [result, setResult] = useState({ status: '', title: '', reason: '' });
  
  const defaultStart = new Date();
  defaultStart.setDate(defaultStart.getDate() + 30);
  const defaultEnd = new Date(defaultStart);
  defaultEnd.setDate(defaultEnd.getDate() + 1);

  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    startDate: defaultStart.toISOString().split('T')[0],
    endDate: defaultEnd.toISOString().split('T')[0],
    adults: 2,
    kids: 0,
    kidsAges: [] as number[],
    description: '',
    budget: 3000
  });

  const handleKidsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const count = parseInt(e.target.value) || 0;
    const newAges = [...formData.kidsAges];
    if (count > newAges.length) {
      for (let i = newAges.length; i < count; i++) newAges.push(10);
    } else {
      newAges.splice(count);
    }
    setFormData({ ...formData, kids: count, kidsAges: newAges });
  };

  const updateKidAge = (index: number, age: number) => {
    const newAges = [...formData.kidsAges];
    newAges[index] = age;
    setFormData({ ...formData, kidsAges: newAges });
  };

  // 1. Funzione per il Verdetto Rapido (Vercel API)
  const handleValidate = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/verdetto', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      setResult(data);
      setStep(5);
    } catch (error) {
      setResult({ status: 'rosso', title: 'Errore', reason: 'Connessione fallita.' });
      setStep(5);
    } finally {
      setLoading(false);
    }
  };

  // 2. Funzione per la Generazione PDF (Render API + Curiosità)
  const handleGeneratePDF = async () => {
    setIsGenerating(true);
    
    // Chiamata immediata per la curiosità
    try {
      const resCuriosity = await fetch('/api/curiosita', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ destination: formData.destination }),
      });
      const data = await resCuriosity.json();
      setCuriosity(data.curiosity);
    } catch (e) {
      setCuriosity("Preparati a scoprire un tesoro del Mediterraneo.");
    }

    // Chiamata "lenta" al motorino Python
    try {
      const response = await fetch('https://tuo-servizio-python.onrender.com/genera-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `30SecondsGuide_${formData.destination}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        setIsGenerating(false);
        setStep(1); 
      }
    } catch (error) {
      console.error(error);
      setIsGenerating(false);
      alert("Errore nel download. Il motorino Python si sta probabilmente svegliando, riprova tra 30 secondi.");
    }
  };

  // Ritorno della Schermata di Caricamento se isGenerating è true
  if (isGenerating) {
    return <LoadingScreen destination={formData.destination} curiosity={curiosity} />;
  }

  return (
    <main className="min-h-screen relative flex flex-col items-center justify-center py-12 px-4 text-[#1a1a1a]" style={{ backgroundColor: '#faf9f6' }}>
      
      {/* Background editoriale */}
      <div className="absolute inset-0 z-0 pointer-events-none opacity-40" 
           style={{ backgroundImage: 'radial-gradient(#1a1a1a 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
      </div>

      {/* Header */}
      <div className="relative z-10 text-center mb-10 w-full max-w-2xl">
        <h1 className="text-5xl md:text-6xl font-black uppercase tracking-tighter text-[#1a1a1a] leading-none mb-3">
          Itinerary <span className="text-[#e67e22]">Wizard</span>
        </h1>
        <p className="text-[11px] font-extrabold tracking-[0.3em] uppercase text-gray-500">Il pianificatore di viaggi complessi</p>
      </div>

      {/* Card Principale */}
      <div className="relative z-10 w-full max-w-xl bg-white rounded-3xl shadow-xl border border-gray-100 p-8 sm:p-12">
        
        {step < 5 && (
          <div className="flex gap-2 mb-10">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className={`h-1.5 rounded-full flex-1 transition-all duration-300 ${step >= i ? 'bg-[#e67e22]' : 'bg-gray-100'}`} />
            ))}
          </div>
        )}

        {/* STEP 1: ROTTA */}
        {step === 1 && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h2 className="text-3xl font-black uppercase tracking-tighter border-b-2 border-[#1a1a1a] pb-3 inline-block">Rotta</h2>
            <div className="space-y-5 pt-2">
              <div>
                <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Partenza</label>
                <input type="text" placeholder="Milano..." value={formData.origin} onChange={(e) => setFormData({...formData, origin: e.target.value})} className="w-full bg-gray-50 border-2 border-transparent focus:border-[#e67e22] focus:bg-white rounded-2xl p-5 text-xl font-bold outline-none transition-all" />
              </div>
              <div>
                <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Destinazione</label>
                <input type="text" placeholder="Giappone..." value={formData.destination} onChange={(e) => setFormData({...formData, destination: e.target.value})} className="w-full bg-gray-50 border-2 border-transparent focus:border-[#e67e22] focus:bg-white rounded-2xl p-5 text-xl font-bold outline-none transition-all" />
              </div>
            </div>
            <button onClick={() => setStep(2)} disabled={!formData.destination} className="w-full bg-[#1a1a1a] text-white font-black uppercase tracking-widest rounded-2xl py-5 mt-6 hover:bg-[#e67e22] disabled:opacity-30">Avanti</button>
          </div>
        )}

        {/* STEP 2: DATE */}
        {step === 2 && (
          <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
            <h2 className="text-3xl font-black uppercase tracking-tighter border-b-2 border-[#1a1a1a] pb-3 inline-block">Periodo</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div>
                <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Andata</label>
                <input type="date" value={formData.startDate} onChange={(e) => setFormData({...formData, startDate: e.target.value})} className="w-full bg-gray-50 border-2 border-transparent focus:border-[#e67e22] rounded-2xl p-5 font-bold outline-none" />
              </div>
              <div>
                <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Ritorno</label>
                <input type="date" min={formData.startDate} value={formData.endDate} onChange={(e) => setFormData({...formData, endDate: e.target.value})} className="w-full bg-gray-50 border-2 border-transparent focus:border-[#e67e22] rounded-2xl p-5 font-bold outline-none" />
              </div>
            </div>
            <div className="flex gap-3 mt-8">
              <button onClick={() => setStep(1)} className="w-1/3 border-2 border-gray-100 rounded-2xl py-5 font-bold text-gray-400 uppercase tracking-widest">Indietro</button>
              <button onClick={() => setStep(3)} className="w-2/3 bg-[#1a1a1a] text-white font-black uppercase tracking-widest rounded-2xl py-5 hover:bg-[#e67e22]">Avanti</button>
            </div>
          </div>
        )}

        {/* STEP 3: PASSEGGERI */}
{step === 3 && (
  <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
    <h2 className="text-3xl font-black uppercase tracking-tighter border-b-2 border-[#1a1a1a] pb-3 inline-block">Viaggiatori</h2>
    
    <div className="grid grid-cols-2 gap-4 pt-2">
      <div className="bg-gray-50 p-4 rounded-2xl border-2 border-transparent focus-within:border-[#e67e22] transition-all">
        <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Adulti</label>
        <input 
          type="number" 
          min="1" 
          value={formData.adults} 
          onChange={(e) => setFormData({...formData, adults: parseInt(e.target.value) || 1})} 
          className="w-full bg-transparent text-3xl font-black outline-none" 
        />
      </div>
      <div className="bg-gray-50 p-4 rounded-2xl border-2 border-transparent focus-within:border-[#e67e22] transition-all">
        <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Minori</label>
        <input 
          type="number" 
          min="0" 
          value={formData.kids} 
          onChange={handleKidsChange} 
          className="w-full bg-transparent text-3xl font-black outline-none" 
        />
      </div>
    </div>

    {/* SEZIONE ETÀ MINORI (Ricostruita) */}
    {formData.kids > 0 && (
      <div className="space-y-3 pt-2 animate-in fade-in slide-in-from-top-2 duration-300">
        <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest">Età dei minori</label>
        <div className="flex flex-wrap gap-2">
          {formData.kidsAges.map((age, index) => (
            <div key={index} className="flex-1 min-w-[80px] bg-white border-2 border-gray-100 rounded-xl p-2 flex flex-col items-center">
              <span className="text-[9px] font-black text-gray-400 uppercase mb-1">Kid {index + 1}</span>
              <input 
                type="number" 
                min="0" 
                max="17" 
                value={age} 
                onChange={(e) => updateKidAge(index, parseInt(e.target.value) || 0)}
                className="w-full text-center font-black text-[#e67e22] text-xl outline-none"
              />
            </div>
          ))}
        </div>
      </div>
    )}

    <div className="flex gap-3 mt-8">
      <button onClick={() => setStep(2)} className="w-1/3 border-2 border-gray-100 rounded-2xl py-5 font-bold text-gray-400 uppercase tracking-widest hover:bg-gray-50 transition-colors">Indietro</button>
      <button onClick={() => setStep(4)} className="w-2/3 bg-[#1a1a1a] text-white font-black uppercase tracking-widest rounded-2xl py-5 hover:bg-[#e67e22] transition-all shadow-lg">Avanti</button>
    </div>
  </div>
)}

        {/* STEP 4: BUDGET & NOTE */}
        {step === 4 && (
          <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
            <h2 className="text-3xl font-black uppercase tracking-tighter border-b-2 border-[#1a1a1a] pb-3 inline-block">Risorse</h2>
            <textarea placeholder="Voglio volare in Business, hotel vista mare..." value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} className="w-full bg-gray-50 border-2 border-transparent focus:border-[#e67e22] rounded-2xl p-5 font-medium outline-none h-28 resize-none" />
            <div className="bg-[#1a1a1a] p-6 rounded-3xl relative overflow-hidden mt-4 shadow-xl">
              <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2 text-white/50">Budget Massimo</label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-3xl font-black text-gray-500">€</span>
                <input type="number" value={formData.budget} onChange={(e) => setFormData({...formData, budget: parseInt(e.target.value) || 0})} className="w-full bg-transparent text-white pl-14 text-5xl font-black outline-none border-b-2 border-gray-700 focus:border-[#e67e22] pb-2 rounded-none" />
              </div>
            </div>
            <div className="flex gap-3 mt-8">
              <button onClick={() => setStep(3)} className="w-1/3 border-2 border-gray-100 rounded-2xl py-5 font-bold text-gray-400 uppercase tracking-widest">Indietro</button>
              <button onClick={handleValidate} disabled={loading} className="w-2/3 bg-[#e67e22] text-white font-black uppercase tracking-widest rounded-2xl py-5 hover:bg-orange-700 disabled:opacity-50 transition-all shadow-lg">
                {loading ? "Analisi..." : "✨ Valida Budget"}
              </button>
            </div>
          </div>
        )}

        {/* STEP 5: VERDETTO E GENERAZIONE PDF */}
        {step === 5 && (
          <div className="space-y-8 text-center animate-in zoom-in-95 duration-500 py-4">
            <div className={`w-24 h-24 rounded-3xl flex items-center justify-center mx-auto text-4xl shadow-2xl rotate-3
              ${result.status === 'verde' ? 'bg-green-100 text-green-600 border-green-200' : result.status === 'giallo' ? 'bg-yellow-100 text-yellow-600 border-yellow-200' : 'bg-red-100 text-red-600 border-red-200'} border`}>
              {result.status === 'verde' ? '✓' : result.status === 'giallo' ? '!' : '✕'}
            </div>
            <div>
              <h2 className="text-4xl font-black uppercase tracking-tighter text-[#1a1a1a] mb-4">{result.title}</h2>
              <div className="bg-gray-50 p-6 rounded-2xl border-l-4 border-[#1a1a1a] text-left">
                <p className="font-medium text-gray-700">{result.reason}</p>
              </div>
            </div>
            <div className="space-y-3 pt-6">
              <button onClick={handleGeneratePDF} className="w-full bg-[#1a1a1a] text-white font-black uppercase tracking-widest rounded-2xl py-6 hover:bg-[#e67e22] transition-colors shadow-xl">
                Genera Travel Plan (PDF)
              </button>
              <button onClick={() => setStep(1)} className="w-full text-xs font-bold text-gray-400 uppercase tracking-widest py-4">← Modifica e riprova</button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}