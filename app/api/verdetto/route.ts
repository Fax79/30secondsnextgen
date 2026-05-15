import { GoogleGenerativeAI } from "@google/generative-ai";
import { NextResponse } from "next/server";

const genAI = new GoogleGenerativeAI("AIzaSyDGSTduAoQ60cVm9d_DjUKdslTz9SsHb3s");

export async function POST(req: Request) {
  try {
    const { 
      origin, 
      destination, 
      startDate, 
      endDate, 
      adults, 
      kids, 
      kidsAges, 
      description, 
      budget 
    } = await req.json();

    // Calcolo notti per dare contesto a Gemini
    const start = new Date(startDate);
    const end = new Date(endDate);
    const nights = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));

    const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

    const prompt = `
      Agisci come un Travel Planner Senior esperto in analisi dei costi (No-Bullshit).
      Valuta la fattibilità del seguente viaggio:
      
      DATI DEL VIAGGIO:
      - Da: ${origin}
      - A: ${destination}
      - Periodo: dal ${startDate} al ${endDate} (${nights} notti)
      - Passeggeri: ${adults} adulti e ${kids} bambini (Età: ${kidsAges.join(", ")})
      - Budget Totale: €${budget}
      - Richieste Extra dell'utente: "${description}"

      REGOLE DI VALUTAZIONE:
      1. Sii brutale e realistico. Se l'utente chiede lusso/business con budget bassi, il verdetto deve essere ROSSO.
      2. Considera i prezzi attuali dei voli internazionali (es. Milano-Tokyo Business costa min. 2500€ a persona).
      3. Se il budget è matematicamente insufficiente per coprire anche solo i voli o gli hotel richiesti, boccia senza pietà.

      RISPONDI ESCLUSIVAMENTE IN FORMATO JSON:
      {
        "status": "verde" | "giallo" | "rosso",
        "title": "Titolo breve e impattante",
        "reason": "Spiegazione tecnica di max 25 parole che giustifichi i costi."
      }
    `;

    const result = await model.generateContent(prompt);
    const responseText = result.response.text();
    
    // Pulizia da eventuali markdown se Gemini li include per errore
    const cleanJson = responseText.replace(/```json|```/g, "").trim();
    return NextResponse.json(JSON.parse(cleanJson));

  } catch (error) {
    console.error("ERRORE API:", error);
    return NextResponse.json({ 
      status: "rosso", 
      title: "Errore Tecnico", 
      reason: "Impossibile contattare Gemini." 
    }, { status: 500 });
  }
}