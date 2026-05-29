import { NextResponse } from 'next/server';
import { SignJWT } from 'jose';

export async function GET() {
  try {
    const secret = process.env.JWT_SECRET_KEY;
    if (!secret) {
      return NextResponse.json({ error: 'Chiave segreta mancante nella configurazione.' }, { status: 500 });
    }

    const encoder = new TextEncoder();
    
    // Genera un token firmato valido per 3 minuti
    const token = await new SignJWT({ authorized: true })
      .setProtectedHeader({ alg: 'HS256' })
      .setIssuedAt()
      .setExpirationTime('3m') 
      .sign(encoder.encode(secret));

    return NextResponse.json({ token });
  } catch (error) {
    return NextResponse.json({ error: 'Errore durante la generazione del token di sicurezza.' }, { status: 500 });
  }
}