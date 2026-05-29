'use client';

import { useState, useEffect, useRef } from 'react';
import Script from 'next/script';
import Link from 'next/link';

declare global {
  interface Window {
    google: any;
  }
}

// --- NUOVO COMPONENTE STEPPER NUMERICO (Ottimizzato per Mobile e Desktop) ---
interface StepperProps {
  value: number;
  onChange: (val: number) => void;
  min?: number;
  max?: number;
  step?: number;
  prefix?: string;
}

const NumberStepper = ({ value, onChange, min = 0, max = 99999, step = 1, prefix = "" }: StepperProps) => {
  const handleMinus = () => {
    if (value - step >= min) onChange(value - step);
  };
  
  const handlePlus = () => {
    if (value + step <= max) onChange(value + step);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/\D/g, ''); // Accetta solo numeri
    if (raw === '') {
      onChange(0); // Permette di svuotare temporaneamente il campo
    } else {
      onChange(parseInt(raw, 10)); // Rimuove gli zeri iniziali
    }
  };

  const handleBlur = () => {
    // Quando l'utente smette di digitare, assicura che i limiti vengano rispettati
    if (value < min) onChange(min);
    if (value > max) onChange(max);
  };

  return (
    <div className="flex items-stretch border border-gray-300 rounded-md overflow-hidden bg-white focus-within:border-[#E67E22] transition-colors h-[48px]">
      <button 
        type="button" 
        onClick={handleMinus} 
        disabled={value <= min} 
        className="w-10 flex-shrink-0 flex items-center justify-center bg-gray-50 text-gray-600 hover:bg-gray-100 disabled:opacity-40 font-bold text-lg select-none border-r border-gray-200 transition"
      >
        &minus;
      </button>
      
      <div className="flex-1 flex items-center justify-center bg-white px-1 min-w-0">
        {prefix && <span className="text-sm font-bold text-gray-400 mr-1 select-none">{prefix}</span>}
        <input 
          type="text" 
          inputMode="numeric"
          value={value === 0 && min > 0 ? '' : value} 
          onChange={handleChange}
          onBlur={handleBlur}
          className="w-full min-w-0 p-0 m-0 text-center text-sm font-bold text-[#2C3E50] focus:outline-none bg-transparent"
        />
      </div>
      
      <button 
        type="button" 
        onClick={handlePlus} 
        disabled={value >= max} 
        className="w-10 flex-shrink-0 flex items-center justify-center bg-gray-50 text-gray-600 hover:bg-gray-100 disabled:opacity-40 font-bold text-lg select-none border-l border-gray-200 transition"
      >
        &#43;
      </button>
    </div>
  );
};


export default function Home() {
  const [step, setStep] = useState<0 | 1 | 2>(0);
  const [wizardStep, setWizardStep] = useState<1 | 2 | 3 | 4>(1);
  const [loading, setLoading] = useState(false);
  const [loadingBudget, setLoadingBudget] = useState(false);
  const [loadingTrivia, setLoadingTrivia] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Stati del modulo
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [budget, setBudget] = useState(3000);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [adults, setAdults] = useState(2);
  const [kids, setKids] = useState(0);
  const [kidsAges, setKidsAges] = useState<number[]>([]);
  const [description, setDescription] = useState('');
  
  // Contenuti dinamici generati lato client da Gemini
  const [budgetScore, setBudgetScore] = useState<number | null>(null);
  const [budgetAnalysis, setBudgetAnalysis] = useState<string | null>(null);
  
  // Stati Caroselli durante il caricamento
  const [triviaArray, setTriviaArray] = useState<string[]>([]);
  const [triviaIndex, setTriviaIndex] = useState(0);
  const [carouselIndex, setCarouselIndex] = useState(0);
  const [loadingMsgIndex, setLoadingMsgIndex] = useState(0);

  const destStandardContainerRef = useRef<HTMLDivElement>(null);

  const loadingMessages = [
    "Consultando centinaia di recensioni...",
    "Esplorando i vicoli segreti della città...",
    "Chiedendo consiglio alla gente del posto...",
    "Selezionando le migliori esperienze gastronomiche...",
    "Infilando la guida nello zaino...",
    "Impaginando il documento PDF con cura..."
  ];

  const affiliateLinks = [
    { provider: 'Kiwi.com', label: 'Migliori combinazioni di volo verificate.', url: 'https://kiwi.tpx.lt/k6iWGXOK' },
    { provider: 'Expedia', label: 'Tariffe Smart per hotel e appartamenti.', url: 'https://www.expedia.com' },
    { provider: 'Heymondo', label: 'Proteggi il tuo viaggio con il 10% di sconto.', url: 'https://heymondo.it/?utm_medium=Afiliado&utm_source=30SECONDSTOGUIDE&utm_campaign=PRINCIPAL&cod_descuento=30SECONDSTOGUIDE&ag_campaign=WIZARD&agencia=JzPWeAXXi7s0b94oPYh2FmTwaWKFpiCp1a8PkqOn&redirect=TEMPORAL' },
    { provider: 'Saily', label: 'eSim internazionale: 5$ di sconto con codice FABIOI3455.', url: 'https://go.saily.site/aff_c?offer_id=101&aff_id=13541&source=WIZARD' },
    { provider: 'Tiqets', label: 'Biglietti ufficiali e ingressi prioritari saltafila.', url: 'https://www.tiqets.com/?partner=30secondstoguide.it-185728' },
    { provider: 'GetYourGuide', label: 'Esplora e prenota tour ed esperienze locali.', url: 'https://gyg.me/YAGbtbpK' }
  ];

  useEffect(() => {
    let msgInterval: NodeJS.Timeout;
    let affiliateInterval: NodeJS.Timeout;
    let triviaInterval: NodeJS.Timeout;

    if (loading) {
      msgInterval = setInterval(() => {
        setLoadingMsgIndex((prev) => (prev + 1) % loadingMessages.length);
      }, 3500);

      affiliateInterval = setInterval(() => {
        setCarouselIndex((prev) => (prev + 1) % affiliateLinks.length);
      }, 10000);

      triviaInterval = setInterval(() => {
        setTriviaIndex((prev) => {
          return triviaArray.length > 0 ? (prev + 1) % triviaArray.length : 0;
        });
      }, 8000);
    }

    return () => {
      clearInterval(msgInterval);
      clearInterval(affiliateInterval);
      clearInterval(triviaInterval);
    };
  }, [loading, loadingMessages.length, affiliateLinks.length, triviaArray.length]);

  const initAutocomplete = async (containerElement: HTMLDivElement | null, callback: (value: string) => void) => {
    if (!containerElement || !window.google) return;

    try {
      const { PlaceAutocompleteElement } = await window.google.maps.importLibrary("places");
      containerElement.innerHTML = ''; 
      
      const autocomplete = new PlaceAutocompleteElement({
        includedPrimaryTypes: ['locality'], 
      });

      autocomplete.style.width = '100%';
      autocomplete.style.boxSizing = 'border-box';
      
      autocomplete.addEventListener('input', () => {
        callback('');
      });

      autocomplete.addEventListener('gmp-select', async (e: any) => {
        const prediction = e.placePrediction;
        if (prediction) {
          const place = prediction.toPlace();
          await place.fetchFields({ fields: ['formattedAddress'] });
          if (place.formattedAddress) {
            callback(place.formattedAddress);
          }
        }
      });

      containerElement.appendChild(autocomplete);
    } catch (err) {
      console.error("Errore nel caricamento di Places API:", err);
    }
  };

  useEffect(() => {
    if (typeof window !== 'undefined' && window.google) {
      if (step === 1) initAutocomplete(destStandardContainerRef.current, setDestination);
    }
  }, [step]);

  const handleGoogleMapsLoad = () => {
    if (step === 1) initAutocomplete(destStandardContainerRef.current, setDestination);
  };

  const handleKidsChange = (num: number) => {
    setKids(num);
    const updatedAges = [...kidsAges];
    if (num > kidsAges.length) {
      while (updatedAges.length < num) updatedAges.push(10);
    } else {
      updatedAges.splice(num);
    }
    setKidsAges(updatedAges);
  };

  const handleKidAgeChange = (index: number, age: number) => {
    const updatedAges = [...kidsAges];
    updatedAges[index] = age;
    setKidsAges(updatedAges);
  };

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };

  // --- INIZIO NUOVO BLOCCO SICURO ---
  const callGeminiClient = async (prompt: string, expectJson: boolean = false) => {
    const response = await fetch('/api/gemini', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, expectJson })
    });

    if (!response.ok) throw new Error('Risposta negativa dai sistemi di computazione linguistica.');
    const data = await response.json();
    return data.result;
  };
  // --- FINE NUOVO BLOCCO SICURO ---

   const handleValidateBudget = async () => {
    setLoadingBudget(true);
    setError(null);
    setBudgetAnalysis(null);
    setBudgetScore(null);

    const today = new Date().toLocaleDateString('it-IT');

    const prompt = `Agisci come un consulente di viaggio esperto e rigoroso. Analizza la fattibilità di questo viaggio considerando la data odierna (${today}) per valutare le tempistiche di prenotazione e il relativo impatto sui costi (es. tariffe last minute vs pianificazione a lungo termine):
    Partenza: ${origin}
    Destinazione: ${destination}
    Budget complessivo: ${budget} EUR
    Periodo: dal ${startDate} al ${endDate}
    Passeggeri: ${adults} adulti e ${kids} minorenni (età: ${kidsAges.join(', ')}).
    Note utente: ${description}

    Output obbligatorio: Restituisci STRETTAMENTE ESCLUSIVAMENTE un oggetto JSON valido con questa struttura:
    {
      "score": <numero intero da 0 a 100 che rappresenta il punteggio di fattibilità, dove 0 è impossibile e 100 è eccellente>,
      "analysis": "<testo dell'analisi di fattibilità concisa e professionale, massimo 150 parole, analitico, paragrafi brevi e puliti, senza formule confidenziali o simboli, a capo reali o altri caratteri che possano invalidare il JSON>"
    }`;

    try {
      const jsonString = await callGeminiClient(prompt, true);
      const data = JSON.parse(jsonString);
      
      setBudgetScore(data.score);
      setBudgetAnalysis(data.analysis);
      setWizardStep(4);
    } catch (err: any) {
      setError(err.message || 'Errore durante la computazione locale della fattibilità budget.');
    } finally {
      setLoadingBudget(false);
    }
  };

  const handleFetchTrivia = async () => {
    setLoadingTrivia(true);
    setTriviaArray([]);
    setTriviaIndex(0);
    const destName = destination.split(',')[0];
    
    const prompt = `Restituisci STRETTAMENTE ESCLUSIVAMENTE un array JSON valido contenente 3 stringhe. NON USARE CARATTERI CHE POSSONO COMPROMETTERE IL JSON come a capo, simboli, ecc. Ogni stringa deve essere una curiosità o un cenno storico interessante, insolito e professionalmente accurato su ${destName}. Stile editoriale e formale, in italiano, massimo 30 parole per stringa. Esempio di output desiderato: ["Curiosità 1...", "Curiosità 2...", "Curiosità 3..."]`;
    
    try {
      const jsonString = await callGeminiClient(prompt, true);
      const data = JSON.parse(jsonString);
      if (Array.isArray(data) && data.length > 0) {
        setTriviaArray(data);
      } else {
        setTriviaArray(['Analisi dei dettagli storici della destinazione completata.']);
      }
    } catch (err) {
      setTriviaArray(['Dettagli storici in fase di recupero...']);
    } finally {
      setLoadingTrivia(false);
    }
  };

  // --- INIZIO NUOVO BLOCCO SICURO ---
  const handleGenerateStandard = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!destination) {
      setError('Inserire la destinazione e selezionarla dal menu di autocompletamento.');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    handleFetchTrivia();

    try {
      // 1. Richiede il token temporaneo a Vercel
      const tokenRes = await fetch('/api/token');
      if (!tokenRes.ok) throw new Error('Errore nel rilascio del token di sicurezza.');
      const { token } = await tokenRes.json();

      // 2. Invia la richiesta diretta a Render con il token nell'header
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/genera-standard`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ destination, lang_code: 'IT' }),
      });

      if (!response.ok) throw new Error('Errore durante la generazione del documento PDF.');

      const blob = await response.blob();
      const destName = destination.split(',')[0].replace(/\s+/g, '_');
      downloadBlob(blob, `Guide_${destName}.pdf`);
      setSuccess(`Documento per ${destination} generato correttamente.`);
    } catch (err: any) {
      setError(err.message || 'Si è verificato un errore imprevisto.');
    } finally {
      setLoading(false);
    }
  };
  // --- FINE NUOVO BLOCCO SICURO ---

    // --- INIZIO NUOVO BLOCCO SICURO ---
  const handleGenerateWizard = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    handleFetchTrivia();

    try {
      // 1. Richiede il token temporaneo a Vercel
      const tokenRes = await fetch('/api/token');
      if (!tokenRes.ok) throw new Error('Errore nel rilascio del token di sicurezza.');
      const { token } = await tokenRes.json();

      // 2. Invia la richiesta diretta a Render con il token nell'header
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/genera-pdf`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          origin,
          destination,
          startDate,
          endDate,
          adults,
          kids,
          kidsAges,
          description,
          budget,
          budgetAnalysis,
          lang_code: 'IT',
        }),
      });

      if (!response.ok) throw new Error('Errore durante la compilazione dell’itinerario nel motore di backend.');

      const blob = await response.blob();
      const destName = destination.split(',')[0].replace(/\s+/g, '_');
      downloadBlob(blob, `Itinerary_${destName}.pdf`);
      setSuccess(`Piano di viaggio per ${destination} compilato ed esportato con successo.`);
    } catch (err: any) {
      setError(err.message || 'Si è verificato un errore durante la generazione dell’itinerario.');
    } finally {
      setLoading(false);
    }
  };
  // --- FINE NUOVO BLOCCO SICURO ---

  const nextWizardStep = () => {
    if (wizardStep === 1) {
      if (!origin || !destination) {
        setError('Inserire i dati di partenza e destinazione.');
        return;
      }
      setError(null);
      setWizardStep(2);
    } else if (wizardStep === 2) {
      if (!startDate || !endDate || !budget) {
        setError('Compilare le date ed il budget complessivo.');
        return;
      }
      const start = new Date(startDate);
      const end = new Date(endDate);
      const nights = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));

      if (nights > 40) {
        setError(`Durata non supportata (${nights} notti). Il limite massimo è di 40 notti.`);
        return;
      }
      if (nights <= 0) {
        setError('La data di ritorno deve essere successiva alla data di partenza.');
        return;
      }
      setError(null);
      setWizardStep(3);
    } else if (wizardStep === 3) {
      if (adults < 1) {
        setError('Il numero di adulti deve essere superiore a zero.');
        return;
      }
      handleValidateBudget();
    }
  };

  const prevWizardStep = () => {
    setError(null);
    if (wizardStep > 1) {
      setWizardStep((prev) => (prev - 1) as any);
    } else {
      setStep(0);
    }
  };

  return (
    <div className="min-h-screen bg-[#faf9f6] text-[#1a1a1a] font-sans antialiased">
      <Script
        src={`https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&loading=async`}
        onLoad={handleGoogleMapsLoad}
      />

      <header className="py-12 text-center border-b border-gray-200 bg-white">
        <div className="max-w-xl mx-auto px-4">
          <h1 className="text-3xl md:text-4xl font-bold text-[#2C3E50] tracking-wider uppercase">
            30SecondsToGuid<span className="text-[#E67E22]">e.</span>
          </h1>
          <p className="text-[#E67E22] text-xs font-semibold tracking-widest uppercase mt-3">
            Generazione editoriale di itinerari e guide
          </p>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-12">
        {error && !loading && (
          <div className="mb-6 p-4 bg-red-50 border-l-2 border-red-600 text-red-800 text-sm font-medium rounded-md">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-6 p-4 bg-green-50 border-l-2 border-green-600 text-green-800 text-sm font-medium rounded-md">
            {success}
          </div>
        )}

        {loading && (
          <div className="bg-white border border-gray-200 rounded-md p-8 shadow-sm space-y-8 animate-fadeIn">
            <div className="text-center space-y-3 py-4">
              <div className="w-8 h-8 border-2 border-[#E67E22] border-t-transparent rounded-full animate-spin mx-auto" />
              <h3 key={loadingMsgIndex} className="text-sm font-bold uppercase tracking-widest text-[#2C3E50] animate-fadeIn">
                {loadingMessages[loadingMsgIndex]}
              </h3>
              <p className="text-xs text-gray-500 max-w-md mx-auto leading-relaxed">
                L'architettura software sta elaborando i dati sul server dedicato. L'operazione richiederà circa un minuto.
              </p>
            </div>

            <div className="border-t border-b border-gray-100 py-6 min-h-[100px] flex flex-col justify-center text-center">
              {loadingTrivia ? (
                <div className="space-y-2 animate-pulse w-full max-w-md mx-auto">
                  <div className="h-3 bg-gray-200 rounded w-1/3 mx-auto"></div>
                  <div className="h-2 bg-gray-200 rounded w-full"></div>
                  <div className="h-2 bg-gray-200 rounded w-5/6 mx-auto"></div>
                </div>
              ) : (
                <div key={triviaIndex} className="animate-fadeIn">
                  <span className="text-[10px] font-bold uppercase tracking-widest text-gray-400 block mb-2">
                    Travel Insight
                  </span>
                  <p className="text-sm text-gray-700 leading-relaxed max-w-md mx-auto italic">
                    {triviaArray.length > 0 ? `"${triviaArray[triviaIndex]}"` : ''}
                  </p>
                </div>
              )}
            </div>

            <div className="bg-[#faf9f6] rounded-md p-6 border border-gray-100 space-y-2 text-center">
              <span className="text-[10px] font-bold uppercase tracking-widest text-gray-400 block">
                Partner Consigliato
              </span>
              <div key={carouselIndex} className="min-h-[60px] flex flex-col justify-center animate-fadeIn">
                <h4 className="text-sm font-bold text-[#2C3E50] uppercase tracking-tight">
                  {affiliateLinks[carouselIndex].provider}
                </h4>
                <p className="text-xs text-gray-600 mt-1">
                  {affiliateLinks[carouselIndex].label}
                </p>
                <a 
                  href={affiliateLinks[carouselIndex].url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[11px] font-bold uppercase tracking-wider text-[#E67E22] mt-2 inline-block hover:underline"
                >
                  Visualizza opzioni disponibili &rarr;
                </a>
              </div>
            </div>
          </div>
        )}

        {!loading && step === 0 && (
          <div className="space-y-8 animate-fadeIn">
            <div className="text-center py-4">
              <h2 className="text-sm font-bold uppercase tracking-widest text-gray-500">
                Seleziona la tipologia di documento
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <button
                onClick={() => setStep(1)}
                data-umami-event="Guida_Selected"
                className="p-8 bg-slate-50 border border-slate-200 hover:border-[#E67E22] rounded-md shadow-sm text-left transition group flex flex-col justify-between min-h-[200px]"
              >
                <div>
                  <span className="block font-bold text-lg text-[#2C3E50] tracking-tight group-hover:text-[#E67E22] transition uppercase">
                    Guida Standar<span className="text-[#E67E22]">d.</span>
                  </span>
                  <p className="text-sm text-gray-600 mt-3 leading-relaxed">
                    Guida della città: cenni storici, quartieri, attrazioni principali e cultura gastronomica. Per passare da zero a local in un minuto.
                  </p>
                </div>
                <span className="text-xs font-bold uppercase tracking-wider text-[#E67E22] mt-4 block">Procedi &rarr;</span>
              </button>

              <button
                onClick={() => { setStep(2); setWizardStep(1); }}
                data-umami-event="Wizard_Selected"
                className="p-8 bg-orange-50 border border-orange-200 hover:border-[#E67E22] rounded-md shadow-sm text-left transition group flex flex-col justify-between min-h-[200px]"
              >
                <div>
                  <span className="block font-bold text-lg text-[#2C3E50] tracking-tight group-hover:text-[#E67E22] transition uppercase">
                    Itinerary Wizar<span className="text-[#E67E22]">d.</span>
                  </span>
                  <p className="text-sm text-gray-600 mt-3 leading-relaxed">
                    Il tuo itinerario disegnato dal nostro Wizard e ottimizzato in base a budget, tempistiche e composizione del gruppo.
                  </p>
                </div>
                <span className="text-xs font-bold uppercase tracking-wider text-[#E67E22] mt-4 block">Procedi &rarr;</span>
              </button>
            </div>
          </div>
        )}

        {!loading && step === 1 && (
          <form onSubmit={handleGenerateStandard} className="bg-white border border-gray-200 rounded-md p-8 shadow-sm space-y-6 animate-fadeIn">
            <div>
              <label className="block text-xs font-bold uppercase tracking-widest text-gray-600 mb-3">
                Destinazione specifica
              </label>
              <div 
                ref={destStandardContainerRef} 
                className="w-full min-h-[48px] bg-white border border-gray-300 rounded-md flex items-center"
              />
            </div>

            <div className="flex gap-4 pt-4 border-t border-gray-100">
              <button
                type="button"
                onClick={() => { setStep(0); setDestination(''); setError(null); }}
                className="w-1/3 py-3 border border-gray-300 rounded-md text-xs font-bold uppercase tracking-wider text-gray-600 hover:bg-gray-50 transition"
              >
                Indietro
              </button>
              <button
                type="submit"
                data-umami-event="Guida_Start_Generate"
                className="w-2/3 py-3 bg-[#2C3E50] text-white text-xs font-bold uppercase tracking-wider rounded-md hover:bg-[#1a252f] transition"
              >
                Genera Guida PDF
              </button>
            </div>
          </form>
        )}

        {!loading && step === 2 && (
          <div className="bg-white border border-gray-200 rounded-md p-8 shadow-sm space-y-6 animate-fadeIn">
            <div className="flex justify-between items-center pb-4 border-b border-gray-100">
              <span className="text-xs font-bold uppercase tracking-widest text-gray-400">
                Fase {wizardStep} di 4
              </span>
              <span className="text-xs font-bold uppercase tracking-wider text-[#E67E22]">
                {wizardStep === 1 && 'Località'}
                {wizardStep === 2 && 'Pianificazione economica e temporale'}
                {wizardStep === 3 && 'Dettagli passeggeri'}
                {wizardStep === 4 && 'Analisi di fattibilità budget'}
              </span>
            </div>

            {wizardStep === 1 && (
              <div className="space-y-4 animate-fadeIn">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-widest text-gray-600 mb-2">Città di partenza</label>
                  <input
                    type="text"
                    placeholder="Es. Milano, Roma..."
                    value={origin}
                    onChange={(e) => setOrigin(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:border-[#E67E22] text-sm"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-widest text-gray-600 mb-2">Destinazione finale</label>
                  <input
                    type="text"
                    placeholder="Es. New York, Provenza..."
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:border-[#E67E22] text-sm"
                    required
                  />
                </div>
              </div>
            )}

            {wizardStep === 2 && (
              <div className="space-y-4 animate-fadeIn">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-widest text-gray-600 mb-2">Budget Totale</label>
                  <NumberStepper 
                    value={budget} 
                    onChange={setBudget} 
                    min={100} 
                    max={50000} 
                    step={100} 
                    prefix="€" 
                  />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-widest text-gray-600 mb-2">Data Partenza</label>
                    <input
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:border-[#E67E22] text-sm h-[48px]"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-widest text-gray-600 mb-2">Data Ritorno</label>
                    <input
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      min={startDate}
                      className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:border-[#E67E22] text-sm h-[48px]"
                      required
                    />
                  </div>
                </div>
              </div>
            )}

            {wizardStep === 3 && (
              <div className="space-y-4 animate-fadeIn">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-widest text-gray-600 mb-2">Numero Adulti</label>
                    <NumberStepper 
                      value={adults} 
                      onChange={setAdults} 
                      min={1} 
                      max={20} 
                      step={1} 
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-widest text-gray-600 mb-2">Numero Minorenni</label>
                    <NumberStepper 
                      value={kids} 
                      onChange={handleKidsChange} 
                      min={0} 
                      max={10} 
                      step={1} 
                    />
                  </div>
                </div>

                {kids > 0 && (
                  <div className="bg-gray-50 p-4 rounded-md border border-gray-200">
                    <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Età partecipanti minorenni</label>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      {kidsAges.map((age, index) => (
                        <div key={index}>
                          <label className="block text-xs text-gray-600 mb-1">Passeggero {index + 1}</label>
                          <NumberStepper 
                            value={age} 
                            onChange={(val) => handleKidAgeChange(index, val)} 
                            min={0} 
                            max={17} 
                            step={1} 
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <label className="block text-xs font-bold uppercase tracking-widest text-gray-600 mb-2">Note integrative (Opzionale)</label>
                  <textarea
                    placeholder="Indicazioni su ritmi dell'itinerario, interessi specifici o preferenze logistiche..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:border-[#E67E22] text-sm"
                  />
                </div>
              </div>
            )}

            {wizardStep === 4 && budgetAnalysis && (
              <div className="space-y-6 animate-fadeIn">
                
                {budgetScore !== null && (
                  <div className="border border-gray-200 rounded-md p-6 bg-white shadow-sm space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold uppercase tracking-widest text-gray-600">
                        Punteggio di Fattibilità Economica
                      </span>
                      <span className="text-2xl font-black text-[#2C3E50]">
                        {budgetScore}<span className="text-sm font-normal text-gray-500"> / 100</span>
                      </span>
                    </div>
                    
                    <div className="w-full bg-gray-100 rounded-full h-4 relative border border-gray-200 overflow-hidden">
                      <div 
                        className="absolute top-0 left-0 h-full rounded-full bg-gradient-to-r from-red-500 via-orange-400 via-yellow-400 to-green-500 transition-all duration-1000 ease-out"
                        style={{ width: `${budgetScore}%` }}
                      />
                    </div>
                    
                    <div className="flex justify-between text-[10px] font-bold uppercase tracking-wider text-gray-400 px-1">
                      <span>Rischio Alto</span>
                      <span className="hidden sm:inline">Incongruo</span>
                      <span className="hidden sm:inline">Equilibrato</span>
                      <span>Eccellente</span>
                    </div>
                  </div>
                )}

                <div className="bg-gray-50 border border-gray-200 rounded-md p-6 max-h-[300px] overflow-y-auto text-sm leading-relaxed text-gray-700 whitespace-pre-line font-mono border border-gray-100">
                  {budgetAnalysis}
                </div>
                <p className="text-xs text-gray-500 italic">
                  Il verdetto di fattibilità sopra riportato è stato elaborato istantaneamente tramite computazione statistica client-side. Procedere per formalizzare il documento finale.
                </p>
              </div>
            )}

            <div className="flex gap-4 pt-4 border-t border-gray-100">
              <button
                type="button"
                onClick={prevWizardStep}
                className="w-1/3 py-3 border border-gray-300 rounded-md text-xs font-bold uppercase tracking-wider text-gray-600 hover:bg-gray-50 transition"
                disabled={loadingBudget}
              >
                Indietro
              </button>
              
              {wizardStep < 4 ? (
                <button
                  type="button"
                  data-umami-event="Budget_generate"
                  onClick={nextWizardStep}
                  className="w-2/3 py-3 bg-[#2C3E50] text-white text-xs font-bold uppercase tracking-wider rounded-md hover:bg-[#1a252f] transition"
                  disabled={loadingBudget}
                >
                  {loadingBudget ? 'Analisi Budget in corso...' : wizardStep === 3 ? 'Invia per Valutazione' : 'Avanti'}
                </button>
              ) : (
                <button
                  type="button"
                  data-umami-event="Wizard_Start_Generate"
                  onClick={handleGenerateWizard}
                  className="w-2/3 py-3 bg-[#E67E22] text-white text-xs font-bold uppercase tracking-wider rounded-md hover:bg-[#d35400] transition"
                >
                  Genera Itinerario
                </button>
              )}
            </div>
          </div>
        )}

        {/* --- SEZIONE LINK ESTERNI IN EVIDENZA --- */}
        {!loading && (
          <div className="mt-12 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <a 
              href="https://blog.30secondstoguide.it" 
              target="_blank" 
              rel="noopener noreferrer" 
              className="p-6 bg-white border border-gray-200 rounded-md shadow-sm hover:shadow-md hover:border-[#E67E22] transition flex items-center justify-between group"
            >
              <div>
                <h3 className="text-sm font-bold text-[#2C3E50] uppercase tracking-wider group-hover:text-[#E67E22] transition">Travel Blog</h3>
                <p className="text-xs text-gray-500 mt-1">Esplora articoli e consigli di viaggio</p>
              </div>
              <span className="text-[#E67E22] text-xl font-bold">&rarr;</span>
            </a>
            <a 
              href="https://guide.30secondstoguide.it" 
              target="_blank" 
              rel="noopener noreferrer" 
              className="p-6 bg-white border border-gray-200 rounded-md shadow-sm hover:shadow-md hover:border-[#E67E22] transition flex items-center justify-between group"
            >
              <div>
                <h3 className="text-sm font-bold text-[#2C3E50] uppercase tracking-wider group-hover:text-[#E67E22] transition">Guide Pocket</h3>
                <p className="text-xs text-gray-500 mt-1">Tutte le edizioni digitali pronte</p>
              </div>
              <span className="text-[#E67E22] text-xl font-bold">&rarr;</span>
            </a>
          </div>
        )}

      </main>

      <footer className="max-w-2xl mx-auto px-4 pb-16 space-y-8 border-t border-gray-200 pt-12 text-xs text-gray-600">
        
        <div className="text-center sm:text-left border-b border-gray-100 pb-8">
          <Link href="/privacy" className="font-bold text-gray-800 uppercase tracking-wider text-xs hover:text-[#E67E22] transition">
            Note Legali e Privacy Policy
          </Link>
        </div>

        <div className="text-justify bg-white border border-gray-200 rounded-md p-6 shadow-sm">
          <h3 className="font-bold text-sm text-[#2C3E50] mb-3 uppercase tracking-wider">
            Infrastruttura del servizio
          </h3>
          <p className="leading-relaxed text-gray-600">
            <strong>30SecondsToGuide</strong> adotta un modello di computazione algoritmica per l'analisi e la strutturazione di piani di viaggio personalizzati in formato PDF. L'architettura software elabora i vettori di input relativi a budget, localizzazione e tempistiche per restituire una pianificazione logistica coerente.
          </p>
        </div>

        <div className="text-center text-xs text-gray-400 pt-4">
          &copy; {new Date().getFullYear()} 30SecondsToGuide. Tutti i diritti riservati.
        </div>
      </footer>
    </div>
  );
}