import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 sm:p-12 bg-white">
      <div className="max-w-2xl w-full space-y-10 text-center">
        
        {/* Intestazione */}
        <h1 className="text-4xl font-bold text-slate-800">
          30SecondsToGuide
        </h1>
        
        {/* Box Avviso Manutenzione */}
        <div className="p-8 bg-orange-50 border border-orange-200 rounded-md shadow-sm">
          <h2 className="text-2xl font-semibold text-orange-800 mb-4">
            Aggiornamento di sistema in corso
          </h2>
          <p className="text-slate-700 leading-relaxed">
            Stiamo eseguendo una manutenzione straordinaria della nostra infrastruttura di intelligenza artificiale. 
            La generazione delle guide standard e il wizard per gli itinerari personalizzati sono temporaneamente sospesi. 
            Il servizio tornerà operativo a breve.
          </p>
        </div>

        {/* Link sempre attivi */}
        <div className="pt-6">
          <p className="text-slate-500 mb-4 text-sm uppercase tracking-wider font-semibold">
            Esplora i nostri contenuti
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {/* Assicurati che l'href corrisponda ai tuoi reali percorsi (es. /blog, https://tuoblog.it) */}
            <Link 
              href="/blog" 
              className="px-6 py-4 bg-slate-50 border border-slate-200 hover:border-slate-400 rounded-md transition text-slate-800 font-medium shadow-sm"
            >
              Visita il Blog
            </Link>
            <Link 
              href="/pocket" 
              className="px-6 py-4 bg-slate-50 border border-slate-200 hover:border-slate-400 rounded-md transition text-slate-800 font-medium shadow-sm"
            >
              Sfoglia le Guide Pocket
            </Link>
          </div>
        </div>

      </div>
    </main>
  );
}