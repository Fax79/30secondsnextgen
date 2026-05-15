'use client';

import React, { useState } from 'react';

export default function Home() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
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
      setStep(4);
    } catch (error) {
      setResult({ status: 'rosso', title: 'Errore', reason: 'Connessione al server fallita.' });
      setStep(4);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center py-12 px-4 text-black">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-extrabold italic tracking-tighter">
          30Seconds<span className="text-orange-600">ToGuide</span>
        </h1>
        <p className="text-gray-400 text-sm font-bold uppercase tracking-widest mt-2">No Bullshit Travel Validator</p>
      </div>

      <div className="w-full max-w-xl bg-white rounded-[2.5rem] shadow-2xl p-10 border border-gray-100">
        
        {/* STEP 1: LOGISTICA ESSENZIALE */}
        {step === 1 && (
          <div className="space-y-8">
            <div className="space-y-2">
              <h2 className="text-3xl font-black italic uppercase tracking-tighter">Rotta</h2>
              <div className="grid grid-cols-2 gap-3">
                <input 
                  placeholder="Da (es. Milano)" 
                  value={formData.origin}
                  className="p-5 rounded-2xl bg-gray-50 border-none focus:ring-2 focus:ring-orange-500 outline-none font-bold shadow-inner"
                  onChange={(e) => setFormData({...formData, origin: e.target.value})}
                />
                <input 
                  placeholder="A (es. Bali)" 
                  value={formData.destination}
                  className="p-5 rounded-2xl bg-gray-50 border-none focus:ring-2 focus:ring-orange-500 outline-none font-bold shadow-inner"
                  onChange={(e) => setFormData({...formData, destination: e.target.value})}
                />
              </div>
            </div>

            <div className="space-y-2">
              <h2 className="text-3xl font-black italic uppercase tracking-tighter">Date</h2>
              <div className="grid grid-cols-2 gap-3">
                <input 
                  type="date"
                  value={formData.startDate}
                  className="p-5 rounded-2xl bg-gray-50 border-none focus:ring-2 focus:ring-orange-500 outline-none font-bold shadow-inner text-gray-700"
                  onChange={(e) => setFormData({...formData, startDate: e.target.value})}
                />
                <input 
                  type="date"
                  value={formData.endDate}
                  min={formData.startDate}
                  className="p-5 rounded-2xl bg-gray-50 border-none focus:ring-2 focus:ring-orange-500 outline-none font-bold shadow-inner text-gray-700"
                  onChange={(e) => setFormData({...formData, endDate: e.target.value})}
                />
              </div>
            </div>

            <button 
              onClick={() => setStep(2)}
              disabled={!formData.destination}
              className="w-full bg-black text-white font-black py-6 rounded-2xl text-xl uppercase tracking-tighter hover:scale-[1.02] transition-all disabled:opacity-30"
            >
              Passeggeri ➜
            </button>
          </div>
        )}

        {/* STEP 2: PASSEGGERI */}
        {step === 2 && (
          <div className="space-y-8">
            <div className="space-y-2">
              <h2 className="text-3xl font-black italic uppercase tracking-tighter">Chi Viaggia?</h2>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-bold text-gray-500 uppercase tracking-wider mb-2 ml-2">Adulti</label>
                  <input 
                    type="number" min="1"
                    value={formData.adults}
                    className="w-full p-5 rounded-2xl bg-gray-50 border-none focus:ring-2 focus:ring-orange-500 outline-none font-black text-2xl shadow-inner text-center"
                    onChange={(e) => setFormData({...formData, adults: parseInt(e.target.value) || 1})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-500 uppercase tracking-wider mb-2 ml-2">Minorenni</label>
                  <input 
                    type="number" min="0"
                    value={formData.kids}
                    className="w-full p-5 rounded-2xl bg-gray-50 border-none focus:ring-2 focus:ring-orange-500 outline-none font-black text-2xl shadow-inner text-center"
                    onChange={handleKidsChange}
                  />
                </div>
              </div>
            </div>

            {formData.kids > 0 && (
              <div className="space-y-2 p-5 bg-gray-50 rounded-2xl shadow-inner border border-gray-100">
                <label className="block text-sm font-bold text-gray-500 uppercase tracking-wider mb-2">Età dei minorenni</label>
                <div className="grid grid-cols-4 gap-3">
                  {formData.kidsAges.map((age, index) => (
                    <input 
                      key={index}
                      type="number" min="0" max="17"
                      value={age}
                      className="w-full p-4 rounded-xl bg-white border border-gray-200 focus:ring-2 focus:ring-orange-500 outline-none font-bold text-center shadow-sm"
                      onChange={(e) => updateKidAge(index, parseInt(e.target.value) || 0)}
                    />
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-4">
              <button onClick={() => setStep(1)} className="flex-1 py-6 font-black text-gray-300 uppercase italic hover:text-gray-500 transition-colors">Indietro</button>
              <button onClick={() => setStep(3)} className="flex-[2] bg-black text-white font-black py-6 rounded-2xl text-xl uppercase tracking-tighter hover:scale-[1.02] transition-all">
                Dettagli e Budget ➜
              </button>
            </div>
          </div>
        )}

        {/* STEP 3: BUDGET & DETTAGLI */}
        {step === 3 && (
          <div className="space-y-8">
            <div className="space-y-2">
              <h2 className="text-xl font-black italic uppercase tracking-tighter text-gray-400">Note Extra (Opzionale)</h2>
              <textarea 
                placeholder="Es: Partenza da Milano, voglio fare scalo a Dubai. Mi interessano musei e trekking..." 
                value={formData.description}
                className="w-full p-5 rounded-2xl bg-gray-50 border-none focus:ring-2 focus:ring-orange-500 outline-none font-medium shadow-inner h-32 resize-none"
                onChange={(e) => setFormData({...formData, description: e.target.value})}
              />
            </div>

            <div className="space-y-2 text-center">
              <h2 className="text-3xl font-black italic uppercase tracking-tighter">Budget Totale</h2>
              <div className="relative">
                <span className="absolute left-6 top-1/2 -translate-y-1/2 text-3xl font-black text-gray-300">€</span>
                <input 
                  type="number" step="100" min="100"
                  value={formData.budget}
                  className="w-full p-8 pl-16 text-5xl font-black rounded-2xl bg-gray-50 border-none text-orange-600 outline-none shadow-inner"
                  onChange={(e) => setFormData({...formData, budget: parseInt(e.target.value) || 0})}
                />
              </div>
            </div>

            <div className="flex gap-4">
              <button onClick={() => setStep(2)} className="flex-1 py-6 font-black text-gray-300 uppercase italic hover:text-gray-500 transition-colors">Indietro</button>
              <button 
                onClick={handleValidate}
                disabled={loading}
                className="flex-[2] bg-orange-600 text-white font-black py-6 rounded-2xl text-xl uppercase tracking-tighter hover:bg-orange-700 transition-all shadow-lg disabled:opacity-50"
              >
                {loading ? "Analisi in corso..." : "Valuta Fattibilità"}
              </button>
            </div>
          </div>
        )}

        {/* STEP 4: VERDETTO */}
        {step === 4 && (
          <div className="text-center space-y-8">
            <div className={`w-28 h-28 rounded-full flex items-center justify-center mx-auto text-5xl shadow-xl
              ${result.status === 'verde' ? 'bg-green-500 text-white' : 
                result.status === 'giallo' ? 'bg-orange-500 text-white' : 'bg-red-600 text-white'}`}>
              {result.status === 'verde' ? '✓' : result.status === 'giallo' ? '!' : '✕'}
            </div>
            
            <div className="space-y-2">
              <h2 className="text-4xl font-black italic uppercase tracking-tighter leading-none">
                {result.title || (result.status === 'verde' ? 'Approvato' : 'Attenzione')}
              </h2>
              <p className="text-lg font-bold text-gray-500 leading-tight px-4">
                {result.reason}
              </p>
            </div>

            <div className="pt-8 border-t border-gray-100 flex flex-col gap-4">
              <button className="w-full bg-black text-white font-black py-6 rounded-2xl text-xl uppercase tracking-tighter hover:scale-[1.02] transition-all shadow-xl">
                Genera Guida PDF
              </button>
              <button onClick={() => setStep(1)} className="text-gray-400 font-bold uppercase text-xs tracking-[0.2em] hover:text-gray-600 transition-colors">
                Modifica Parametri
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}