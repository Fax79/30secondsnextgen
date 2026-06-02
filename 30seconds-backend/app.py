import os
import re
import urllib.parse
import io
import json
import gspread
import jwt
from datetime import datetime
from flask import Flask, request, send_file, jsonify, abort
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
from weasyprint import HTML
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

app = Flask(__name__)

# --- 1. CONFIGURAZIONE CORS RIGOROSA ---
CORS(app, resources={r"/*": {"origins": [
    "https://30secondstoguide.it",
    "https://www.30secondstoguide.it",
    "http://localhost:3000"
]}})

# --- 2. CONTROLLO AUTENTICAZIONE TRAMITE TOKEN ---
@app.before_request
def verify_token():
    # Escludi le richieste preflight CORS e le rotte di root/health
    if request.method == 'OPTIONS' or request.path == '/' or request.path == '/health':
        return
        
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Accesso negato. Token di sicurezza mancante."}), 401
        
    token = auth_header.split(" ")[1]
    
    try:
        secret_key = os.environ.get("JWT_SECRET_KEY")
        jwt.decode(token, secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Il token temporaneo è scaduto. Riprovare."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token di sicurezza non valido."}), 401

# --- CONFIGURAZIONE GOOGLE SHEETS ---
def get_gspread_client():
    creds_json = os.getenv('GCP_SERVICE_ACCOUNT')
    if not creds_json:
        print("ERRORE SHEETS: La variabile GCP_SERVICE_ACCOUNT è vuota o non trovata in Render!", flush=True)
        return None
    try:
        # Carica il JSON pulito senza modificarlo prima del parsing
        creds_dict = json.loads(creds_json)
        
        # Correggi i ritorni a capo all'interno della singola stringa della chiave privata, se necessario
        if 'private_key' in creds_dict:
            creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
            
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        print(f"ERRORE SHEETS AUTENTICAZIONE (Il JSON potrebbe essere formattato male): {e}", flush=True)
        return None

def log_to_sheets(data):
    client = get_gspread_client()
    if client:
        try:
            sheet = client.open("30Seconds_Stats").sheet1
            sheet.append_row(data)
            print("SHEETS SUCCESS: Riga salvata correttamente nel foglio Google!")
        except Exception as e:
            print(f"ERRORE SHEETS SCRITTURA (File non trovato o permessi mancanti): {e}")
    else:
        print("ERRORE SHEETS: Il salvataggio è stato annullato perché il client non si è avviato.")

# --- CONFIGURAZIONE API ---
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# ==========================================
# LINK TRACCIATI
# ==========================================
FLIGHT_LINK = "https://kiwi.tpx.lt/k6iWGXOK"
LUGGAGE_LINK = "https://radicalstorage.tpx.lt/fpjMovNW"
REIMB_LINK = "https://airhelp.tpx.lt/YS9ciIsW"
ESIM_LINK = "https://go.saily.site/aff_ad?campaign_id=2&aff_id=13541&hostNameId=23945&source=GUIDA"
RENTAL_LINK = "https://clk.tradedoubler.com/click?p=284745&a=3480952"
TRANSF_LINK = "https://tpx.lt/O5I4OrpX"
TAXI_LINK = "https://kiwitaxi.tpx.lt/KCeVs32Q"
TIQETS_LINK = "https://tiqets.tpx.lt/abHnK4vL"
INSURANCE_LINK = "https://heymondo.it/?utm_medium=Afiliado&utm_source=30SECONDSTOGUIDE&utm_campaign=PRINCIPAL&cod_descuento=30SECONDSTOGUIDE&ag_campaign=GUIDA&agencia=JzPWeAXXi7s0b94oPYh2FmTwaWKFpiCp1a8PkqOn&redirect=TEMPORAL"
TRAIN_LINK = "https://clk.tradedoubler.com/click?a(3480952)p(376991)ttid(13)url(https://www.thetrainline.com/it/porta-un-amico?situation=td-it&utm_source=td-it)"
GYG_LINK = "https://gyg.me/YAGbtbpK"
HOTEL_LINK = "https://www.expedia.com"
GUIDE_APP_URL = "https://www.30secondstoguide.it" 

# --- TESTI E TRADUZIONI PDF (UNIFICATO STANDARD + WIZARD) ---
LANGUAGES = {
    "IT": {
        "label": "Pocket Guide",
        "sub": "Guida turistica completa:<br>Itinerari, Storia e Cultura",
        "disc": "Questa guida è offerta gratuitamente. Se ti è utile, nell'ultima pagina trovi una selezione di sconti esclusivi per voli e hotel che ci aiutano a mantenere il servizio attivo. <strong>Buon viaggio!</strong>",
        "planner": "Travel Planner",
        "insight": "Travel Insight",
        "must": "Non partire senza",
        "gen": "WWW.30SECONDSTOGUIDE.IT",
        "footer_msg": "Questa guida è gratuita grazie ai nostri partner. Usando questi link supporti il nostro lavoro. Buon viaggio!",
        
        # Nuove chiavi Itinerary Wizard
        "months": {1: "Gennaio", 2: "Febbraio", 3: "Marzo", 4: "Aprile", 5: "Maggio", 6: "Giugno", 7: "Luglio", 8: "Agosto", 9: "Settembre", 10: "Ottobre", 11: "Novembre", 12: "Dicembre"},
        "pax_adults": "Adulti",
        "pax_kids": "Ragazzi",
        "pdf_title": "Travel Plan Esclusivo",
        "pdf_generated": "GENERATO CON www.30secondstoguide.it",
        "pdf_promo": "Approfondisci la conoscenza delle città del tuo itinerario, crea le tue guide qui.",
        "pdf_travellers": "Viaggiatori",
        "pdf_date": "Date",
        "pdf_budget_target": "Budget Target",
        "key_chapter": "CAPITOLO",
        "key_verdict": "VERDETTO",
        "key_day": "GIORNO",
        "ad_flight": "In {month} i prezzi aumentano? Inizia a monitorare ORA i migliori prezzi su Kiwi.com",
        "ad_esim": "eSim Saily: Internet immediato all'arrivo senza acquisto di SIM locali. 5$ di sconto con codice FABIOI3455",
        "ad_insur": "MAI senza Assicurazione Sanitaria: Clicca e sblocca il 10% DI SCONTO con Heymondo",
        "ad_hotel": "Stanze in Hotel quasi esaurite in {month}? Prenota ora su Expedia",
        "ad_transfer": "Transfer privati ad un prezzo WOW! da e per l'aeroporto",
        "ad_tiqets": "Non rischiare il tutto esaurito a {dest}. Assicurati il posto e le migliori offerte su Tiqets",
        "ad_car": "Viaggia in libertà e noleggia un auto: Tariffe esclusive con Sixt",
        "ad_train": "Treni: Prenota su Trainline",
        "ad_rest": "Esplora al miglior prezzo! Prenota su GetYourGuide"
    },
    "EN": {
        "label": "Pocket Guide",
        "sub": "Complete Travel Guide:<br>Itineraries, History and Culture",
        "disc": "This guide is free. If it's useful, on the last page you'll find a selection of exclusive discounts for flights and hotels that help us keep the service running. <strong>Safe travels!</strong>",
        "planner": "Travel Planner",
        "insight": "Travel Insight",
        "must": "Must have",
        "gen": "WWW.30SECONDSTOGUIDE.IT",
        "footer_msg": "This guide is free thanks to our partners. Using these links supports our work. Have a great trip!",
        
        # Nuove chiavi Itinerary Wizard
        "months": {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"},
        "pax_adults": "Adults",
        "pax_kids": "Teens/Kids",
        "pdf_title": "Exclusive Travel Plan",
        "pdf_generated": "GENERATED WITH www.30secondstoguide.it",
        "pdf_promo": "Deepen your knowledge of the cities in your itinerary, create your guides here.",
        "pdf_travellers": "Travelers",
        "pdf_date": "Dates",
        "pdf_budget_target": "Target Budget",
        "key_chapter": "CHAPTER",
        "key_verdict": "VERDICT",
        "key_day": "DAY",
        "ad_flight": "Prices rising in {month}? Book now on Kiwi.com",
        "ad_esim": "eSim Saily: Instant internet on arrival without buying local SIMs",
        "ad_insur": "NEVER without Health Insurance: Get 10% off HERE with Heymondo",
        "ad_hotel": "Hotel rooms almost sold out in {month}? Book now on Expedia",
        "ad_transfer": "Private transfers at WOW prices! to and from the airport",
        "ad_tiqets": "Don't risk sold out in {dest}. Secure spots and best deals on Tiqets",
        "ad_car": "Travel freely and rent a car: Exclusive rates with Sixt",
        "ad_train": "Trains: Book on Trainline",
        "ad_rest": "Discover at the best rate! Book on GetYourGuide"
    }
}

# --- MODELLI PROMPT (GUIDA STANDARD) ---
TESTO_MODELLO_IT = """
# [NOME CITTÀ]: Guida Esclusiva

## 1. L'Anima della Città
[Intro evocativa di 150 parole, comprensione profonda dell'anima dei luoghi].

## 2. Quartieri e Atmosfere
[Descrizione zone, individua il contrasto principale antico vs moderno, popolare vs esclusivo, riva destra vs riva sinistra, ecc].

### Confronto Zone
* **[zona 1 di cui sopra]:** [Descrizione atmosfera]
* **[zona 2 di cui sopra]:** [Descrizione atmosfera]
* **Chi ci va:** [Target turisti]

## 3. Dove dormire
[Migliori quartieri dove alloggiare per tipologia di turista/vacanza: in famiglia, in coppia, con un gruppo di amici, viaggiatori senior].

## 4. Gastronomia
[Cosa mangiare e dove, la tradizione gastronomica].

### Piatti Imperdibili
* **[Piatto 1]:** [Descrizione e ingredienti]
* **[Piatto 2]:** [Descrizione e ingredienti]
* **[il cibo tradizionale]:** [i migliori ristoranti, i più caratteristici, consigli per risparmiare]
* **[bevande tradizionali]:** [i migliori locali, i più caratteristici, consigli per risparmiare]

## 5. Attrazioni
* **[Monumento 1]:** [Descrizione, se presenti giorni e orari di apertura, prezzi biglietti]
* **[Monumento 2]:** [Descrizione, se presenti giorni e orari di apertura, prezzi biglietti]
* **[Monumento 3]:** [Descrizione, se presenti giorni e orari di apertura, prezzi biglietti]
* **[Monumento 4]:** [Descrizione, se presenti giorni e orari di apertura, prezzi biglietti]
* **[Monumento 5]:** [Descrizione, se presenti giorni e orari di apertura, prezzi biglietti]

## 6. I mercati
* **[Mercato 1]:** [Descrizione]
* **[Mercato 2]:** [Descrizione]

## 7. Calendario Culturale
[I principali festival, fiere, ricorrenze e feste della città].

## 8. Info Pratiche
* **Come arrivare:** [Info su compagnie aeree che servono l'aeroporto principale (tradizionali e low cost), voli dall'Italia (se la destinazione è all'estero), mezzi alternativi: treni/autobus)]
* **Trasporti:** [Info]
* **Sicurezza:** [Info]
* **Clima:** [Info sui migliori periodi per visitare la città]
* **Visti e requisiti:** [Info]
* **Fuso orario:** [Info]
* **Consigli utili:** [Info su valuta locale e prese elettriche, non usare mai simboli delle valute ma i loro codici, es. EUR, USD, GBP, ecc]

## 9. Itinerario 3 Giorni
* **Giorno 1:** [Mattina/Pomeriggio/Sera, pensa all'itinerario nell'ordine migliore per razionalizzare i tempi]
* **Giorno 2:** [Mattina/Pomeriggio/Sera, pensa all'itinerario nell'ordine migliore per razionalizzare i tempi]
* **Giorno 3:** [Mattina/Pomeriggio/Sera, pensa all'itinerario nell'ordine migliore per razionalizzare i tempi]

## 10. Itinerario 5 Giorni
* **Giorni 1-3:** Come sopra.
* **Giorno 4:** [Mattina/Pomeriggio/Sera, pensa all'itinerario nell'ordine migliore per razionalizzare i tempi]
* **Giorno 5:** [Mattina/Pomeriggio/Sera, pensa all'itinerario nell'ordine migliore per razionalizzare i tempi]

## 11. Se hai più tempo
* **Fuori dai sentieri battuti:** [Un quartiere meno turistico].
* **Gite fuori porta:** [Una o più gite di mezza giornata o di un giorno nei dintorni].

## 12. Conclusione
[Riflessione finale filosofica sul viaggio in questa città, descrivi l'essenza del viaggio].
"""

TESTO_MODELLO_EN = """
# [CITY NAME]: Exclusive Guide

## 1. The Soul of the City
[Evocative intro of 150 words, deep understanding of the soul of the places].

## 2. Neighborhoods and Atmospheres
[Zone description, identify the main contrast ancient vs modern, popular vs exclusive, right bank vs left bank, etc].

### Zone Comparison
* **[zone 1 mentioned above]:** [Atmosphere description]
* **[zone 2 mentioned above]:** [Atmosphere description]
* **Who goes there:** [Tourist target]

## 3. Where to sleep
[Best neighborhoods to stay for type of tourist/vacation: family, couple, group of friends, senior travelers].

## 4. Gastronomy
[What to eat and where, the gastronomic tradition].

### Unmissable Dishes
* **[Dish 1]:** [Description and ingredients]
* **[Dish 2]:** [Description and ingredients]
* **[traditional food]:** [best restaurants, most characteristic ones, tips to save money]
* **[traditional drinks]:** [best bars, most characteristic ones, tips to save money]

## 5. Attractions
* **[Monument 1]:** [Description, if present opening days and hours, ticket prices]
* **[Monument 2]:** [Description, if present opening days and hours, ticket prices]
* **[Monument 3]:** [Description, if present opening days and hours, ticket prices]
* **[Monument 4]:** [Description, if present opening days and hours, ticket prices]
* **[Monument 5]:** [Description, if present opening days and hours, ticket prices]

## 6. Markets
* **[Market 1]:** [Description]
* **[Market 2]:** [Description]

## 7. Cultural Calendar
[Main festivals, fairs, recurring events and city holidays].

## 8. Practical Info
* **Getting there:** [Info on airlines serving the main airport (legacy and low cost), flights from major hubs, alternative means: trains/buses)]
* **Transport:** [Info]
* **Safety:** [Info]
* **Climate:** [Info on best periods to visit]
* **Visas and requirements:** [Info]
* **Time zone:** [Info]
* **Useful tips:** [Info on local currency and power plugs, never use currency symbols but their codes, e.g. EUR, USD, GBP, etc]

## 9. 3-Day Itinerary
* **Day 1:** [Morning/Afternoon/Evening, think of the itinerary in the best order to rationalize time]
* **Day 2:** [Morning/Afternoon/Evening, think of the itinerary in the best order to rationalize time]
* **Day 3:** [Morning/Afternoon/Evening, think of the itinerary in the best order to rationalize time]

## 10. 5-Day Itinerary
* **Days 1-3:** As above.
* **Day 4:** [Morning/Afternoon/Evening, think of the itinerary in the best order to rationalize time]
* **Day 5:** [Morning/Afternoon/Evening, think of the itinerary in the best order to rationalize time]

## 11. If you have more time
* **Off the beaten path:** [A less touristy neighborhood].
* **Day trips:** [One or more half-day or full-day trips in the surroundings].

## 12. Conclusion
[Final philosophical reflection on the trip to this city, describe the essence of the journey].
"""

# ==========================================
# FUNZIONI COMUNI
# ==========================================
def inject_gyg_links(text_line, dest_name):
    tour_matches = re.findall(r'\[TOUR:\s*(.*?)\]', text_line)
    for tour in tour_matches:
        query_string = f"{tour} {dest_name}"
        query_encoded = urllib.parse.quote(query_string)
        search_link = f"https://www.getyourguide.it/s?q={query_encoded}&partner_id=UR2ZJHB&utm_medium=online_publisher"
        html_link = f"<a href='{search_link}' style='color:#e67e22; font-weight:bold; text-decoration:underline;'>{tour}</a>"
        text_line = text_line.replace(f"[TOUR: {tour}]", html_link)
    return text_line


# ==========================================
# 🧙‍♂️ PDF ENGINE (GUIDA STANDARD)
# ==========================================
def create_pdf(text, city, lang_code="IT"):
    city_clean = city.split(',')[0].strip()
    city_upper = city_clean.strip().upper()
    if len(city_upper) > 24:
        city_upper = city_upper[:21] + "..."
    
    if 12 < len(city_upper) <= 24 and " " in city_upper:
        words = city_upper.split()
        mid = len(words) // 2
        line1, line2 = " ".join(words[:mid]), " ".join(words[mid:])
        html_city = f"{line1}<br>{line2[:-1]}<span class='last-letter-dot'>{line2[-1]}.</span>"
    else:
        html_city = f"{city_upper[:-1]}<span class='last-letter-dot'>{city_upper[-1]}.</span>"

    strings = LANGUAGES[lang_code]
    formatted_body = ""
    lines = text.split('\n')
    
    if lines and lines[0].startswith('# '):
        lines = lines[1:]

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        line_clean = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line_clean)
        
        # Sostituzioni inline
        heymondo_link = "https://heymondo.it/?utm_medium=Afiliado&utm_source=30SECONDSTOGUIDE&utm_campaign=PRINCIPAL&cod_descuento=30SECONDSTOGUIDE&ag_campaign=GUIDACONTEXT&agencia=JzPWeAXXi7s0b94oPYh2FmTwaWKFpiCp1a8PkqOn&redirect=TEMPORAL"
        heymondo_html = f"<a href='{heymondo_link}' style='color:#e67e22; font-weight:bold; text-decoration:underline;'>Heymondo</a>"
        line_clean = re.sub(r'\bHeymondo\b', heymondo_html, line_clean, flags=re.IGNORECASE)

        saily_link = "https://go.saily.site/aff_c?offer_id=101&aff_id=13541&source=GUIDATEXT"
        saily_html = f"<a href='{saily_link}' style='color:#e67e22; font-weight:bold; text-decoration:underline;'>Saily</a>"
        line_clean = re.sub(r'\bSaily\b', saily_html, line_clean, flags=re.IGNORECASE)
        
        line_clean = inject_gyg_links(line_clean, city_clean)
        
        if line_clean.startswith('## '):
            title = line_clean.replace('## ', '')
            formatted_body += f"<h2 class='h2-title'>{title}</h2>"
            
            # Iniezione box dinamici
            if any(x in title.upper() for x in ["DORMIRE", "SLEEP", "HOTEL"]):
                formatted_body += f"""
                <div class="section-service-box">
                    <span class="service-tag">{strings["insight"]}</span>
                    <a href="{HOTEL_LINK}" class="service-cta">HOTEL<span class="last-letter-dot">S</span></a>
                    <div class="service-sub">Tariffe verificate per hotel e appartamenti.</div>
                </div>"""
            elif any(x in title.upper() for x in ["ARRIVARE", "GETTING", "VOLI", "TRASPORTI"]):
                formatted_body += f"""
                <div class="section-service-box">
                    <span class="service-tag">{strings["insight"]}</span>
                    <a href="{FLIGHT_LINK}" class="service-cta">FLIGHT<span class="last-letter-dot">S</span></a>
                    <div class="service-sub">Le migliori combinazioni di volo.</div>
                </div>"""
            elif any(x in title.upper() for x in ["ATTRAZIONI", "ATTRACTIONS", "MUSEI", "MUSEUMS"]):
                formatted_body += f"""
                <div class="section-service-box">
                    <span class="service-tag">{strings["insight"]}</span>
                    <a href="{TIQETS_LINK}" class="service-cta">TICKET<span class="last-letter-dot">S</span></a>
                    <div class="service-sub">Biglietti ufficiali saltafila.</div>
                </div>"""
            elif any(x in title.upper() for x in ["QUARTIERI", "ZONE", "NEIGHBORHOODS"]):
                formatted_body += f"""
                <div class="section-service-box">
                    <span class="service-tag">{strings["must"]}</span>
                    <a href="{INSURANCE_LINK}" class="service-cta">INSURANC<span class="last-letter-dot">E</span></a>
                    <div class="service-sub">Proteggi il tuo viaggio con Heymondo.</div>
                </div>"""    
            elif any(x in title.upper() for x in ["ANIMA", "SOUL"]):
                formatted_body += f"""
                <div class="section-service-box">
                    <span class="service-tag">{strings["must"]}</span>
                    <a href="{ESIM_LINK}" class="service-cta">INTERNE<span class="last-letter-dot">T</span></a>
                    <div class="service-sub">eSim internazionale Saily.</div>
                </div>"""
                
        elif line_clean.startswith('### '):
            title = line_clean.replace('### ', '')
            formatted_body += f"<h3 class='h3-title'>{title}</h3>"
        elif line_clean.startswith('* ') or line_clean.startswith('- '):
            formatted_body += f"<li>{line_clean[2:]}</li>"
        else:
            formatted_body += f"<p>{line_clean}</p>"

    html_template = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 25mm 20mm 30mm 20mm;
                background-color: #faf9f6;
                background-image: 
                    linear-gradient(rgba(26, 26, 26, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(26, 26, 26, 0.03) 1px, transparent 1px);
                background-size: 40px 40px;

                @bottom-left {{
                    content: "30SecondsToGuide";
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 14px;
                    font-weight: 800;
                    color: #e67e22;
                    padding-bottom: 5mm;
                }}
                @bottom-right {{
                    content: "{strings['gen']}";
                    font-family: monospace;
                    font-size: 11px;
                    color: #1a1a1a;
                    opacity: 0.8;
                    padding-bottom: 5mm;
                }}
            }}

            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #1a1a1a;
                line-height: 1.6;
                margin: 0;
                padding: 0;
            }}

            .cover-container {{
                page-break-after: always;
                position: relative;
                padding-top: 80px;
            }}
            .design-accent-l {{
                position: absolute;
                top: 40px; left: -15px;
                width: 120px; height: 200px;
                border-top: 12px solid #1a1a1a;
                border-left: 12px solid #1a1a1a;
                z-index: -1;
            }}
            .category-label {{
                font-size: 13px; font-weight: 800; letter-spacing: 5px;
                text-transform: uppercase; margin-bottom: 12px;
                background: #faf9f6; display: inline-block; padding-right: 10px;
            }}
            .city-name {{
                font-size: 65px; font-weight: 900; text-transform: uppercase;
                margin: 0; line-height: 0.95; letter-spacing: -2px;
                color: #e67e22;
            }}
            .last-letter-dot {{ color: #1a1a1a; }}
            .guide-subtitle {{
                font-size: 20px; margin-top: 20px; color: #7f8c8d;
                font-weight: 400; letter-spacing: 0.5px;
                background: #faf9f6; display: inline-block; padding: 2px 5px;
            }}
            .description-box {{
                margin-top: 45px; padding: 25px; background-color: #ffffff;
                border-left: 4px solid #1a1a1a; max-width: 460px; font-size: 14px;
                color: #555; box-shadow: 8px 8px 0px rgba(26, 26, 26, 0.05);
            }}

            .content-container {{
                page-break-after: always;
            }}
            .h2-title {{
                text-transform: uppercase; font-weight: 900; letter-spacing: -1px;
                color: #e67e22; margin-top: 40px; margin-bottom: 15px; border-bottom: 2px solid #1a1a1a; display: inline-block;
                page-break-after: avoid; 
            }}
            .h3-title {{ 
                font-weight: 800; color: #1a1a1a; margin-top: 30px; margin-bottom: 10px; 
                page-break-after: avoid; 
            }}
            p, li {{ font-size: 14px; color: #333; margin-bottom: 10px; text-align: justify; }}
            li {{ margin-left: 20px; }}
            
            strong {{ color: #000000; font-weight: bold; }}

            .section-service-box {{
                margin: 40px 0px; padding: 25px; position: relative;
                background-color: #ffffff;
                border: 1px solid rgba(26, 26, 26, 0.08);
                box-shadow: 8px 8px 0px rgba(26, 26, 26, 0.05);
                page-break-inside: avoid;
            }}
            .section-service-box::before {{
                content: ""; position: absolute; top: -6px; left: -6px;
                width: 40px; height: 40px;
                border-top: 8px solid #1a1a1a; border-left: 8px solid #1a1a1a;
            }}
            .service-tag {{
                font-size: 11px; font-weight: 800; letter-spacing: 4px;
                text-transform: uppercase; color: #1a1a1a; display: block; margin-bottom: 10px;
            }}
            .service-cta {{
                font-size: 30px; font-weight: 900; text-transform: uppercase;
                color: #e67e22; text-decoration: none; letter-spacing: -1.5px; line-height: 1; display: block;
            }}
            .service-cta::after {{ content: "."; color: #1a1a1a; }}
            .service-sub {{ font-size: 13px; color: #7f8c8d; margin-top: 8px; font-weight: 400; }}

            .partner-block {{ margin-bottom: 50px; position: relative; padding-left: 15px; page-break-inside: avoid; }}
            .offer-description {{ font-size: 15px; color: #7f8c8d; margin-top: 10px; max-width: 450px; background: #faf9f6; display: inline-block; }}

        </style>
    </head>
    <body>

        <div class="cover-container">
            <div class="design-accent-l"></div>
            <div class="category-label">{strings['label']}</div>
            <h1 class="city-name">{html_city}</h1>
            <div class="guide-subtitle">{strings['sub']}</div>
            <div class="description-box">{strings['disc']}</div>
        </div>

        <div class="content-container">
            {formatted_body}
        </div>

        <div class="cover-container" style="padding-top: 40px; page-break-after: avoid;">
            <div class="category-label">{strings['planner']}</div>
            
            <div class="partner-block" style="margin-top: 60px;">
                <div class="design-accent-l" style="top: -10px; left: -15px; width: 40px; height: 50px; border-width: 8px;"></div>
                <a href="{HOTEL_LINK}" class="service-cta" style="font-size: 40px; display: inline-block;">BOOKIN<span class="last-letter-dot">G</span></a>
                <div class="offer-description">Tariffe Smart selezionate per hotel e appartamenti nella tua destinazione.</div>
            </div>

            <div class="partner-block">
                <div class="design-accent-l" style="top: -10px; left: -15px; width: 40px; height: 50px; border-width: 8px;"></div>
                <a href="{FLIGHT_LINK}" class="service-cta" style="font-size: 40px; display: inline-block;">FLIGHT<span class="last-letter-dot">S</span></a>
                <div class="offer-description">Le migliori combinazioni di volo verificate per questa settimana.</div>
            </div>

            <div class="partner-block">
                <div class="design-accent-l" style="top: -10px; left: -15px; width: 40px; height: 50px; border-width: 8px;"></div>
                <a href="{TRAIN_LINK}" class="service-cta" style="font-size: 40px; display: inline-block;">TREN<span class="last-letter-dot">O</span></a>
                <div class="offer-description">Viaggi in treno? Approfitta del 10% di sconto riservato ai nostri lettori.</div>
            </div>

            <div class="partner-block">
                <div class="design-accent-l" style="top: -10px; left: -15px; width: 40px; height: 50px; border-width: 8px;"></div>
                <a href="{ESIM_LINK}" class="service-cta" style="font-size: 40px; display: inline-block;">INTERNE<span class="last-letter-dot">T</span></a>
                <div class="offer-description">Con Saily sei connesso da subito - Nuovo cliente? 5USD di sconto con codice FABIOI3455.</div>
            </div>            

            <div style="margin-top: 40px; font-size: 13px; color: #1a1a1a; font-style: italic; max-width: 350px; line-height: 1.6;">
                {strings['footer_msg']}
            </div>
        </div>

    </body>
    </html>
    """

    return HTML(string=html_template).write_pdf()

# ==========================================
# 🧙‍♂️ PDF ENGINE (ITINERARY WIZARD)
# ==========================================
def create_wizard_pdf(text, destination, meta_data, lang_code="IT"):
    ui = LANGUAGES.get(lang_code, LANGUAGES["IT"])

    def clean_text_for_pdf(text_input):
        if not text_input: return ""
        text_input = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text_input)
        return text_input

    city_clean = destination.split(',')[0].strip()
    dest_clean = clean_text_for_pdf(city_clean)
    month_clean = clean_text_for_pdf(meta_data.get('month_name', ''))

    # Titolo Copertina
    city_upper = dest_clean.strip().upper()
    if len(city_upper) > 24:
        city_upper = city_upper[:21] + "..."
    if 12 < len(city_upper) <= 24 and " " in city_upper:
        words = city_upper.split()
        mid = len(words) // 2
        line1, line2 = " ".join(words[:mid]), " ".join(words[mid:])
        html_city = f"{line1}<br>{line2[:-1]}<span class='last-letter-dot'>{line2[-1]}.</span>"
    else:
        html_city = f"{city_upper[:-1]}<span class='last-letter-dot'>{city_upper[-1]}.</span>"

    formatted_body = ""
    lines = text.split('\n')
    inserted_ch1 = inserted_ch2 = inserted_ch3 = inserted_ch4 = False

    TRIGGER_CH = f"## {ui.get('key_chapter', 'CAPITOLO')}"
    TRIGGER_VERDICT = ui.get('key_verdict', 'VERDETTO')

    def make_html_box(link, cta, sub):
        cta_html = f"{cta[:-1]}<span style='color: #1a1a1a;'>{cta[-1]}</span>"
        return f"""
        <div class="section-service-box">
            <span class="service-tag">LINK UTILI PER IL TUO VIAGGIO</span>
            <a href="{link}" target="_blank" class="service-cta">{cta_html}</a>
            <div class="service-sub">{sub}</div>
        </div>
        """

    for line in lines:
        clean_line = clean_text_for_pdf(line.strip())
        if not clean_line:
            continue
        
        # Sostituzioni dirette partner come da frontend
        heymondo_link = "https://heymondo.it/?utm_medium=Afiliado&utm_source=30SECONDSTOGUIDE&utm_campaign=PRINCIPAL&cod_descuento=30SECONDSTOGUIDE&ag_campaign=WIZARDCONTEXT&agencia=JzPWeAXXi7s0b94oPYh2FmTwaWKFpiCp1a8PkqOn&redirect=TEMPORAL"
        heymondo_html = f"<a href='{heymondo_link}' style='color:#e67e22; font-weight:bold; text-decoration:underline;'>Heymondo</a>"
        clean_line = re.sub(r'\bHeymondo\b', heymondo_html, clean_line, flags=re.IGNORECASE)

        kiwi_link = "https://kiwi.tpx.lt/k6iWGXOK"
        kiwi_html = f"<a href='{kiwi_link}' style='color:#e67e22; font-weight:bold; text-decoration:underline;'>Kiwi</a>"
        clean_line = re.sub(r'\bKiwi(?:\.com)?\b', kiwi_html, clean_line, flags=re.IGNORECASE)
        
        saily_link = "https://go.saily.site/aff_c?offer_id=101&aff_id=13541&source=WIZARDTEXT"
        saily_html = f"<a href='{saily_link}' style='color:#e67e22; font-weight:bold; text-decoration:underline;'>Saily</a>"
        clean_line = re.sub(r'\bSaily\b', saily_html, clean_line, flags=re.IGNORECASE)

        treno_link = "https://clk.tradedoubler.com/click?a(3480952)p(376991)ttid(13)url(https://www.thetrainline.com/it/porta-un-amico?situation=td-it&utm_source=td-it)"
        treno_html = f"<a href='{treno_link}' style='color:#e67e22; font-weight:bold; text-decoration:underline;'>treno</a>"
        clean_line = re.sub(r'\btreno\b', treno_html, clean_line, flags=re.IGNORECASE)
        
        clean_line = inject_gyg_links(clean_line, destination)
        line_upper = clean_line.upper()
        
        # Logica iniezione annunci
        if f"{TRIGGER_CH} 2" in line_upper and not inserted_ch1:
            formatted_body += make_html_box(FLIGHT_LINK, "FLIGHTS", ui.get("ad_flight", "").format(month=month_clean))
            formatted_body += make_html_box(ESIM_LINK, "INTERNET", ui.get("ad_esim", ""))
            formatted_body += make_html_box(INSURANCE_LINK, "INSURANCE", ui.get("ad_insur", ""))
            inserted_ch1 = True
        elif f"{TRIGGER_CH} 3" in line_upper and not inserted_ch2:
            formatted_body += make_html_box(HOTEL_LINK, "HOTEL", ui.get("ad_hotel", "").format(month=month_clean))
            formatted_body += make_html_box(TRANSF_LINK, "TRANSFER", ui.get("ad_transfer", ""))
            inserted_ch2 = True
        elif f"{TRIGGER_CH} 4" in line_upper and not inserted_ch3:
            formatted_body += make_html_box(TIQETS_LINK, "TICKETS", ui.get("ad_tiqets", "").format(dest=dest_clean))
            formatted_body += make_html_box(RENTAL_LINK, "RENTAL CAR", ui.get("ad_car", ""))
            formatted_body += make_html_box(TRAIN_LINK, "TRAIN", ui.get("ad_train", ""))
            inserted_ch3 = True
        elif f"{TRIGGER_CH} 5" in line_upper and not inserted_ch4:
            formatted_body += make_html_box(GYG_LINK, "TOURS", ui.get("ad_rest", ""))
            inserted_ch4 = True

        # Parsing Elementi Markdown
        if clean_line.startswith('## '):
            formatted_body += f"<h2 class='h2-title'>{clean_line.replace('## ', '')}</h2>"
        elif clean_line.startswith('### '):
            formatted_body += f"<h3 class='h3-title'>{clean_line.replace('### ', '')}</h3>"
        elif TRIGGER_VERDICT in line_upper:
            verdict_text = clean_line.replace('#', '').strip()
            formatted_body += f"<div class='verdict-box'>{verdict_text}</div>"
        elif clean_line.startswith('* ') or clean_line.startswith('- '):
            formatted_body += f"<li>{clean_line[2:]}</li>"
        elif re.match(r'^\d+\.', clean_line):
            formatted_body += f"<p><strong>{clean_line}</strong></p>"
        elif clean_line.startswith('# '):
            continue 
        else:
            formatted_body += f"<p>{clean_line}</p>"

    html_template = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 25mm 20mm 30mm 20mm;
                background-color: #faf9f6;
                background-image: 
                    linear-gradient(rgba(26, 26, 26, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(26, 26, 26, 0.03) 1px, transparent 1px);
                background-size: 40px 40px;

                @bottom-left {{
                    content: "30SecondsToGuide";
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 14px;
                    font-weight: 800;
                    color: #e67e22;
                    padding-bottom: 5mm;
                }}
                @bottom-right {{
                    content: "{ui.get('pdf_generated', '')}";
                    font-family: monospace;
                    font-size: 11px;
                    color: #1a1a1a;
                    opacity: 0.8;
                    padding-bottom: 5mm;
                }}
            }}

            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #1a1a1a;
                line-height: 1.6;
                margin: 0;
                padding: 0;
            }}

            .cover-container {{
                page-break-after: always;
                position: relative;
                padding-top: 80px;
            }}
            .design-accent-l {{
                position: absolute;
                top: 40px; left: -15px;
                width: 120px; height: 200px;
                border-top: 12px solid #1a1a1a;
                border-left: 12px solid #1a1a1a;
                z-index: -1;
            }}
            .category-label {{
                font-size: 13px; font-weight: 800; letter-spacing: 5px;
                text-transform: uppercase; margin-bottom: 12px;
                background: #faf9f6; display: inline-block; padding-right: 10px;
            }}
            .city-name {{
                font-size: 65px; font-weight: 900; text-transform: uppercase;
                margin: 0; line-height: 0.95; letter-spacing: -2px;
                color: #e67e22;
            }}
            .last-letter-dot {{ color: #1a1a1a; }}
            
            .description-box {{
                margin-top: 145px; padding: 25px; background-color: #ffffff;
                border-left: 4px solid #1a1a1a; max-width: 460px; font-size: 14px;
                color: #555; box-shadow: 8px 8px 0px rgba(26, 26, 26, 0.05);
            }}

            .content-container {{
                page-break-after: always;
            }}
            .h2-title {{
                text-transform: uppercase; font-weight: 900; letter-spacing: -1px;
                color: #e67e22; margin-top: 40px; margin-bottom: 15px; border-bottom: 2px solid #1a1a1a; display: inline-block;
                page-break-after: avoid; 
            }}
            .h3-title {{ 
                font-weight: 800; color: #1a1a1a; margin-top: 30px; margin-bottom: 10px; 
                page-break-after: avoid; 
            }}
            p, li {{ font-size: 14px; color: #333; margin-bottom: 10px; text-align: justify; }}
            li {{ margin-left: 20px; }}
            strong {{ color: #000000; font-weight: bold; }}

            .verdict-box {{
                margin: 30px 0; padding: 15px; background-color: #f8f9fa; 
                border-left: 5px solid #e67e22; font-weight: bold; color: #2c3e50;
            }}

            .section-service-box {{
                margin: 40px 0px; padding: 25px; position: relative;
                background-color: #ffffff;
                border: 1px solid rgba(26, 26, 26, 0.08);
                box-shadow: 8px 8px 0px rgba(26, 26, 26, 0.05);
                page-break-inside: avoid;
            }}
            .section-service-box::before {{
                content: ""; position: absolute; top: -6px; left: -6px;
                width: 40px; height: 40px;
                border-top: 8px solid #1a1a1a; border-left: 8px solid #1a1a1a;
            }}
            .service-tag {{
                font-size: 11px; font-weight: 800; letter-spacing: 4px;
                text-transform: uppercase; color: #1a1a1a; display: block; margin-bottom: 10px;
            }}
            .service-cta {{
                font-size: 30px; font-weight: 900; text-transform: uppercase;
                color: #e67e22; text-decoration: none; letter-spacing: -1.5px; line-height: 1; display: block;
            }}
            .service-cta::after {{ content: "."; color: #1a1a1a; }}
            .service-sub {{ font-size: 13px; color: #7f8c8d; margin-top: 8px; font-weight: 400; }}

        </style>
    </head>
    <body>

        <div class="cover-container">
            <div class="design-accent-l"></div>
            <div class="category-label">{ui.get('pdf_title', '')}</div>
            <h1 class="city-name">{html_city}</h1>
            <div class="description-box">
                <strong>{ui.get('pdf_date', '')}:</strong> {meta_data.get('dates', '')}<br>
                <strong>{ui.get('pdf_travellers', '')}:</strong> {meta_data.get('pax', '')}<br>
                <strong>{ui.get('pdf_budget_target', '')}:</strong> {meta_data.get('budget', '')}
            </div>
            
            <div style="margin-top: 60px; text-align: center;">
                <a href="{GUIDE_APP_URL}" style="display:inline-block; padding:15px 25px; background-color:#e67e22; color:white; text-decoration:none; font-weight:bold; border-radius:5px;">
                    {ui.get('pdf_promo', '')}
                </a>
            </div>
        </div>

        <div class="content-container">
            {formatted_body}
        </div>

    </body>
    </html>
    """

    return HTML(string=html_template).write_pdf()

# ==========================================
# ROTTA: /genera-standard (GUIDA POCKET)
# ==========================================
@app.route('/genera-standard', methods=['POST'])
def genera_standard():
    data = request.json
    city_name = data.get('destination')
    # lang_code = data.get('lang_code', 'IT') # Forzato a IT
    lang_code = "IT"

    if not city_name:
        return jsonify({"error": "Destinazione mancante"}), 400

    city_clean = city_name.split(',')[0].strip()

    try:
        today_str = datetime.now().strftime("%d/%m/%Y")
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        if lang_code == "IT":
            sys_instruct = "Sei uno scrittore di viaggi esperto (stile Lonely Planet/National Geographic). Scrivi una guida DETTAGLIATA e con le informazioni più aggiornate a {today_str} per:"
            base_prompt = TESTO_MODELLO_IT
            rules = """
            1. NON USARE MAI TABELLE MARKDOWN (niente righe con | |).
            2. Se devi fare un confronto, usa elenchi puntati descrittivi.
            3. Usa ESATTAMENTE la struttura seguente.
            4. Scrivi paragrafi ricchi e lunghi.
            5. CONTESTO TEMPORALE: Hai l'obbligo di utilizzare le informazioni macroeconomiche e geopolitiche aggiornate alla data {today_str} (es. Verifica accuratamente i recenti ingressi nell'Eurozona, la documentazione necessaria all'ingresso nel paese, ecc).
            6. Quando suggerisci un'escursione, un'attrazione, un tour o un museo specifico, SOLO E SOLTANTO SE SEI RAGIONEVOLMENTE CERTO CHE SI POSSA PRENOTARE TRAMITE GETYOURGUIDE ALLORA devi racchiudere il nome ESATTAMENTE in questo tag: [TOUR: Nome Attrazione]. Esempio: Ti consiglio di visitare il [TOUR: Colusseo].
            """
        else:
            sys_instruct = "You are an expert travel writer (Lonely Planet/National Geographic style). Write a DETAILED guide for:"
            base_prompt = TESTO_MODELLO_EN
            rules = """
            1. NEVER USE MARKDOWN TABLES (no lines with | |).
            2. If you need to make a comparison, use descriptive bullet points.
            3. Use EXACTLY the following structure.
            4. Write rich and long paragraphs.
            5. If a nation, region, or geographic area is entered, produce the guide for the main city, add a premise before chapter 1 listing other cities urging to make separate guides, also suggest using the "ITINERARY WIZARD" button found on the site.
            6. If a word or phrase is entered that is not a geographical place, answer jokingly but synthetically, do not use the guide structure.
            7. When you suggest a specific excursion, attraction, tour, or museum, ONLY IF YOU ARE REASONABLY SURE IT CAN BE BOOKED VIA GETYOURGUIDE, you MUST enclose the name EXACTLY in this tag: [TOUR: Attraction Name]. Example: I recommend visiting the [TOUR: Colosseum].
            """
        
        full_prompt = f"""
        {sys_instruct} {city_name}.
        
        RULES:
        {rules}
        
        MODEL:
        {base_prompt}
        """
        
        response = model.generate_content(full_prompt)
        markdown_content = response.text
        
        pdf_bytes = create_pdf(markdown_content, city_name, lang_code)
        
        timestamp = datetime.now().strftime("%d/%m %H:%M")
        # Array di 9 elementi per allineamento colonne
        log_to_sheets([timestamp, city_clean, "GUIDE_ONLY", "-", "-", "-", "-", "IT", "-"])
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Guide_{city_clean.replace(' ', '_')}.pdf"
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# ROTTA: /genera-pdf (ITINERARY WIZARD)
# ==========================================
@app.route('/genera-pdf', methods=['POST'])
def genera_pdf():
    data = request.json
    origin = data.get('origin', '')
    destination = data.get('destination', '')
    start_date = data.get('startDate', '')
    end_date = data.get('endDate', '')
    adults = data.get('adults', 2)
    kids = data.get('kids', 0)
    kids_ages = data.get('kidsAges', [])
    description = data.get('description', '')
    budget = data.get('budget', 0)
    budget_analysis = data.get('budgetAnalysis', '')
    # lang_code = data.get('lang_code', 'IT') # Forzato a IT
    lang_code = "IT"

    if not destination:
        return jsonify({"error": "Destinazione mancante"}), 400

    city_clean = destination.split(',')[0].strip()

    try:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            duration_check = (end_dt - start_dt).days
            mese_partenza = LANGUAGES.get(lang_code, LANGUAGES["IT"]).get("months", {}).get(start_dt.month, "")
            dates_formatted = f"{start_dt.strftime('%d/%m')} - {end_dt.strftime('%d/%m/%Y')}"
        except Exception:
            duration_check = 3
            mese_partenza = ""
            dates_formatted = f"{start_date} - {end_date}"

        ui = LANGUAGES.get(lang_code, LANGUAGES["IT"])
        pax_desc = f"{adults} {ui.get('pax_adults', 'Adulti')}"
        today_str = datetime.now().strftime("%d/%m/%Y")
        if kids > 0:
            pax_desc += f", {kids} {ui.get('pax_kids', 'Ragazzi')} ({', '.join(map(str, kids_ages))})"

        model = genai.GenerativeModel("gemini-2.5-flash")

        if lang_code == "IT":
            sys_prompt = "Agisci come un Travel Planner Senior. Non pianifichi solo un viaggio, pianifichi un viaggio su misura che massimizza il valore del budget. ATTENZIONE ALLA COERENZA CON LA DATA DI OGGI, CHE E' {today_str}, RISPETTO AI SUGGERIMENTI CHE DAI (es. se il volo è tra un mese non sugggerire di prenotare 6 mesi prima o monitorare i voli 24 mesi prima)."
            rules_lang = "Usa SOLO l'alfabeto Latino/Italiano. Quando suggerisci un'escursione, un'attrazione, un tour o un museo specifico, SOLO E SOLTANTO SE SEI RAGIONEVOLMENTE CERTO CHE SI POSSA PRENOTARE TRAMITE GETYOURGUIDE ALLORA devi racchiudere il nome ESATTAMENTE in questo tag: [TOUR: Nome Attrazione]. Esempio: Ti consiglio di visitare il [TOUR: Colosseo]."
            structure = f"""
            # {destination.upper()}: [Sottotitolo]
            **IL VERDETTO SUL BUDGET: € {budget}** (Stato: Lusso/Più che adeguato/Sufficiente/Stretto/Impossibile)
            ## CAPITOLO 1: LA PREPARAZIONE (Voli, eSim, Assicurazione)
            [Info trasporti ottimizza orari dei voli consultando google flights dagli aeroporti più vicini o più efficientemente utilizzabili da {origin}, reperisci gli ultimi prezzi da google flight se hai date precise e suggerisci Kiwi per la prenotazione sfruttando i travel hack. Utilizza il mezzo di trasporto più razionale in linea con la durata del viaggio, il budget e se ci sono possiblità concrete di utilizzare mezzi alternativi all'aereo. Come eSim consiglia sempre Saily (NON per Italia/UE dove esiste roaming as at home), per l'assicurazione Heymondo con sconto 10%]
            ## CAPITOLO 2: DOVE DORMIRE (Strategie alloggio)
            ## CAPITOLO 3: L'ITINERARIO GIORNO PER GIORNO (Dettagliato)
            [Itinerario ottimizzato, razionalizza gli spostamenti in base alla distanza, a seconda del mezzo di trasporto massimizza le tappe con il tempo a disposizione. Prediligi attrazioni su Tiqets e Getyourguide. Scoperta del territorio]
            ## CAPITOLO 4: COSA MANGIARE
            [Piatti tipici, ristoranti (verifica su Tripadvisor i migliori per la fascia di prezzo compatibile con il budget e dai riferimenti puntuali), suggerisci i posti migliori per lo street food]
            ## CAPITOLO 5: CALENDARIO CULTURALE
            [Festival e ricorrenze]
            ## CAPITOLO 6: CONTO ECONOMICO FINALE
            [includi sempre Voli internazionali se il viaggio li necessita per la stima del budget]
            ## CAPITOLO 7: INFORMAZIONI PRATICHE
            ## CAPITOLO 8: CONCLUSIONE
            """
        else:
            sys_prompt = "Act as a Senior Travel Planner. You don't just plan a trip, you plan a tailor-made trip that maximizes budget value."
            rules_lang = "Use ONLY Latin/English alphabet. When you suggest a specific excursion, attraction, tour, or museum, you MUST enclose the name EXACTLY in this tag: [TOUR: Attraction Name]. Example: I recommend visiting the [TOUR: Colosseum]."
            structure = f"""
            # {destination.upper()}: [Subtitle]
            **THE VERDICT ON BUDGET: € {budget}** (Status: Luxury/More than adequate/Sufficient/Tight/Impossible)
            ## CHAPTER 1: PREPARATION (Flights, eSim, Insurance)
            [Transport info, Saily eSim, Heymondo insurance 10% off]
            ## CHAPTER 2: WHERE TO SLEEP (Accommodation strategies)
            ## CHAPTER 3: DAY BY DAY ITINERARY (Detailed)
            ## CHAPTER 4: WHAT TO EAT
            ## CHAPTER 5: CULTURAL CALENDAR
            ## CHAPTER 6: FINAL FINANCIAL BREAKDOWN
            ## CHAPTER 7: PRACTICAL INFORMATION
            ## CHAPTER 8: CONCLUSION
            """

        prompt = f"""
        {sys_prompt}
        Razionalizza il tempo, visita quanti più posti possibili con {duration_check} notti a disposizione.
        Valuta la densità degli impegni giornalieri perché siano fattibili. Presta attenzione ad essere razionale negli spostamenti per massimizzare il tempo a disposizione.
        Tieni conto delle NOTE UTENTE per personalizzare l'esperienza, ma NON ripeterle esplicitamente.
        Crea un "Travel Plan" esclusivo per: {destination}.
        
        DATI:
        - Durata: {duration_check} notti ({start_date} - {end_date})
        - Data odierna di elaborazione (usa questa come riferimento temporale attuale): {today_str}
        - Gruppo: {pax_desc}
        - Budget: € {budget}
        - NOTE UTENTE: {description if description else "Nessuna nota"}
        
        REGOLE TASSATIVE:
        1. {rules_lang} 2. TRASLITTERA i nomi locali. 3. Simboli Valute: EUR, USD.
        4. USA intelligentemente il grassetto markdown (**) per evidenziare i giorni (es. **Giorno 1:**), i nomi dei luoghi, degli hotel, delle attrazioni e dei ristoranti, per rendere la lettura del documento molto più facile e scansionabile.
        5. VIETATO USARE LISTE ANNIDATE. 6. PREZZI IN EURO CON SEPARATORE MIGLIAIA.
        7. USA DURATA {duration_check}, non ricalcolare. 8. NON SCRIVERE I TUOI PENSIERI INTERNI.
        
        STRUTTURA TITOLI (Usa ESATTAMENTE questi):
        {structure}
        """
        
        response = model.generate_content(prompt)
        markdown_content = response.text

        meta_data = {
            "dates": dates_formatted,
            "pax": pax_desc,
            "budget": f"EUR {budget}",
            "month_name": mese_partenza
        }
        
        pdf_bytes = create_wizard_pdf(markdown_content, destination, meta_data, lang_code)
        
        timestamp = datetime.now().strftime("%d/%m %H:%M")
        ages_str = ", ".join(map(str, kids_ages)) if kids > 0 else "-"
        # Array di 9 elementi per allineamento colonne
        log_to_sheets([timestamp, city_clean, budget, duration_check, adults, kids, ages_str, "IT", origin])
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Itinerary_{city_clean.replace(' ', '_')}.pdf"
        )
        
    except Exception as e:
        print(f"Errore Wizard: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)