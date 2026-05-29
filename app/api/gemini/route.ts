import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { prompt, expectJson } = body;

    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) {
      console.error("Chiave API Gemini mancante sul server Vercel.");
      return NextResponse.json(
        { error: "Errore di configurazione API sul server." },
        { status: 500 }
      );
    }

    if (!prompt) {
      return NextResponse.json(
        { error: "Prompt mancante nella richiesta." },
        { status: 400 }
      );
    }

    // Costruisce il payload per l'API di Google
    const payload: any = {
      contents: [{ parts: [{ text: prompt }] }],
    };

    // Forza la risposta in formato JSON se richiesto
    if (expectJson) {
      payload.generationConfig = { responseMimeType: "application/json" };
    }

    // Esegue la chiamata all'infrastruttura Google in modo sicuro
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.text();
      console.error("Errore dall'API Gemini:", errorData);
      return NextResponse.json(
        { error: "Errore durante l'elaborazione dell'AI." },
        { status: response.status }
      );
    }

    const data = await response.json();
    const textResponse = data.candidates[0].content.parts[0].text;

    return NextResponse.json({ result: textResponse }, { status: 200 });

  } catch (error: any) {
    console.error("Errore critico nella Route Handler Gemini:", error);
    return NextResponse.json(
      { error: "Si è verificato un errore interno del server." },
      { status: 500 }
    );
  }
}