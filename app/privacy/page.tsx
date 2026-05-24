import Link from 'next/link';

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-[#faf9f6] text-[#1a1a1a] font-sans antialiased py-16 px-4">
      <div className="max-w-3xl mx-auto bg-white border border-gray-200 rounded-md p-8 md:p-12 shadow-sm">
        
        <h1 className="text-3xl md:text-4xl font-bold text-[#2C3E50] mb-8 border-b border-gray-200 pb-6 flex items-center gap-3">
          <span>🔒</span> Privacy Policy & Cookie
        </h1>

        <div className="space-y-10 text-[#2C3E50] leading-relaxed">
          
          <section>
            <h2 className="text-2xl font-bold mb-4">1. Chi siamo</h2>
            <p className="text-gray-700">
              Il titolare del trattamento dati è il gestore di <strong>30SecondsToGuide</strong>.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">2. Quali dati raccogliamo</h2>
            <p className="text-gray-700 mb-4">
              Questo sito utilizza infrastrutture in cloud e le API di <strong>Google Gemini</strong>.
            </p>
            <ul className="list-disc pl-5 space-y-3 text-gray-700 marker:text-[#2C3E50]">
              <li>
                <strong>Dati inseriti dall'utente:</strong> I dati inseriti (città, budget, date, passeggeri) vengono inviati a Google Gemini esclusivamente per generare la guida PDF. Vengono inoltre salvati in forma anonima a soli fini statistici interni. Non viene salvato alcun dato personale identificabile (come nome, email o indirizzo IP).
              </li>
              <li>
                <strong>Cookie:</strong> Utilizziamo solo cookie tecnici essenziali per il funzionamento della sessione. Non utilizziamo cookie di profilazione o tracciamento pubblicitario proprietari.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">3. Servizi Terzi</h2>
            <p className="text-gray-700">
              Il sito contiene link di affiliazione a terze parti (es. Heymondo, GetYourGuide, ecc.). Cliccando su tali link, l'utente viene reindirizzato su piattaforme esterne che potrebbero installare i propri cookie, per i quali 30SecondsToGuide non è responsabile.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">4. Diritti dell'utente</h2>
            <p className="text-gray-700">
              Dal momento che 30SecondsToGuide non richiede registrazione e non memorizza alcun dato personale identificativo, non conserviamo profili utente consultabili, modificabili o cancellabili. I dati generici di viaggio inseriti nell'applicazione sono totalmente anonimi e non riconducibili alla tua persona.
            </p>
          </section>

          <div className="pt-2">
            <p className="text-gray-500 italic text-sm">
              Ultimo aggiornamento: Maggio 2026
            </p>
          </div>

        </div>

        <div className="mt-10 pt-6">
          <Link 
            href="/" 
            className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded text-sm font-medium text-gray-700 hover:bg-gray-50 transition shadow-sm"
          >
            <span className="text-blue-500 text-lg leading-none">⬅</span> Torna alla Home
          </Link>
        </div>

      </div>
    </div>
  );
}