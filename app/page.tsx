'use client';

import React, { useState } from 'react';

export default function Home() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    travelers: '2 Adulti',
    budget: 1500,
    notes: ''
  });

  const nextStep = () => setStep(step + 1);
  const prevStep = () => setStep(step - 1);

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center py-12 px-4">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-extrabold text-gray-900 mb-2">
          30Seconds<span className="text-orange-600">ToGuide</span>
        </h1>
        <p className="text-gray-600">Il tuo itinerario STRAperfetto, validato dall'AI.</p>
      </div>

      <div className="w-full max-w-2xl bg-white rounded-3xl shadow-xl p-8 border border-gray-100">
        <div className="flex gap-2 mb-8">
          {[1, 2, 3].map((s) => (
            <div 
              key={s} 
              className={`h-2 flex-1 rounded-full transition-all ${s <= step ? 'bg-orange-600' : 'bg-gray-100'}`}
            />
          ))}
        </div>

        {step === 1 && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-800">Da dove si parte?</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Partenza</label>
                <input 
                  type="text" 
                  placeholder="Es: Milano" 
                  className="w-full p-3 rounded-xl border border-gray-200 text-black outline-none focus:ring-2 focus:ring-orange-500"
                  value={formData.origin}
                  onChange={(e) => setFormData({...formData, origin: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Destinazione</label>
                <input 
                  type="text" 
                  placeholder="Es: Tokyo" 
                  className="w-full p-3 rounded-xl border border-gray-200 text-black outline-none focus:ring-2 focus:ring-orange-500"
                  value={formData.destination}
                  onChange={(e) => setFormData({...formData, destination: e.target.value})}
                />
              </div>
            </div>
            <button 
              onClick={nextStep}
              disabled={!formData.destination}
              className="w-full bg-black text-white font-bold py-4 rounded-2xl hover:bg-gray-800 transition-all disabled:opacity-50"
            >
              Continua ➜
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-800">Dettagli del viaggio</h2>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1 text-black">Budget Totale (€)</label>
              <input 
                type="number" 
                className="w-full p-3 rounded-xl border border-gray-200 text-black outline-none focus:ring-2 focus:ring-orange-500"
                value={formData.budget}
                onChange={(e) => setFormData({...formData, budget: parseInt(e.target.value)})}
              />
            </div>
            <div className="flex gap-4">
              <button onClick={prevStep} className="flex-1 py-4 font-bold text-gray-500">Indietro</button>
              <button onClick={nextStep} className="flex-[2] bg-black text-white font-bold py-4 rounded-2xl hover:bg-gray-800 transition-all">
                Valuta Budget ➜
              </button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="text-center space-y-6">
            <div className="w-20 h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto text-3xl font-bold">
              ✓
            </div>
            <h2 className="text-2xl font-bold text-gray-800 text-black">Budget Approvato!</h2>
            <p className="text-gray-600">
              Con {formData.budget}€ puoi goderti {formData.destination}.
            </p>
            <button className="w-full bg-orange-600 text-white font-bold py-4 rounded-2xl hover:bg-orange-700 transition-all">
              Genera Guida PDF
            </button>
          </div>
        )}
      </div>
    </main>
  );
}