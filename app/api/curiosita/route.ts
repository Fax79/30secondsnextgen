import { GoogleGenerativeAI } from "@google/generative-ai";
import { NextResponse } from "next/server";

const genAI = new GoogleGenerativeAI(process.env.GOOGLE_GENERATIVE_AI_API_KEY || "");

export async function POST(req: Request) {
  try {
    const { destination } = await req.json();
    const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" });

    const prompt = `Genera una singola curiosità in italiano affascinante e brevissima su ${destination}. 
    Focus su cultura, storia o aneddoti artistici. 
    Stile editoriale raffinato (stile Lonely Planet). 
    Massimo 15 parole. Non usare introduzioni tipo "Ecco la curiosità".`;

    const result = await model.generateContent(prompt);
    const text = result.response.text().trim();

    return NextResponse.json({ curiosity: text });
  } catch (error) {
    return NextResponse.json({ curiosity: "Collioure è il luogo dove la luce ha ispirato la nascita del Fauvismo." });
  }
}