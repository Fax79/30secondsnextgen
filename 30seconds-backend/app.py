import os
import re
import urllib.parse
import io
import json
import gspread
from datetime import datetime
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
from weasyprint import HTML
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

app = Flask(__name__)
CORS(app)

# --- CONFIGURAZIONE GOOGLE SHEETS ---
def get_gspread_client():
    creds_json = os.getenv('GCP_SERVICE_ACCOUNT')
    if not creds_json:
        return None
    try:
        creds_json = creds_json.replace('\\n', '\n')
        creds_dict = json.loads(creds_json)
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except:
        return None

def log_to_sheets(data):
    client = get_gspread_client()
    if client:
        try:
            sheet = client.open("30Seconds_Stats").sheet1
            sheet.append_row(data)
        except Exception as e:
            print(f"Errore logging Sheets: {e}")

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

# --- TESTI E TRADUZIONI PDF ---
LANGUAGES = {
    "IT": {
        "label": "Pocket Guide",
        "sub": "Guida turistica completa:<br>Itinerari, Storia e Cultura",
        "disc": "Questa guida è offerta gratuitamente. Se ti è utile, nell'ultima pagina trovi una selezione di sconti exclusivi per voli e hotel che ci aiutano a mantenere il servizio attivo. <strong>Buon viaggio!</strong>",
        "planner": "Travel Planner",
        "insight": "Travel Insight",
        "must": "Non partire senza",
        "gen": "WWW.30SECONDSTOGUIDE.IT",
        "footer_msg": "Questa guida è gratuita grazie ai nostri partner. Usando questi link supporti il nostro lavoro. Buon viaggio!"
    },
    "EN": {
        "label": "Pocket Guide",
        "sub": "Complete Travel Guide:<br>Itineraries, History and Culture",
        "disc": "This guide is free. If it's useful, on the last page you'll find a selection of exclusive discounts for flights and hotels that help us keep the service running. <strong>Safe travels!</strong>",
        "planner": "Travel Planner",
        "insight": "Travel Insight",
        "must": "Must have",
        "gen": "WWW.30SECONDSTOGUIDE.IT",
        "footer_msg": "This guide is free thanks to our partners. Using these links supports our work. Have a great trip!"
    }
}

# --- MODELLI PROMPT ---
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
* **[il cibo tradicional]:** [i migliori ristoranti, i più caratteristici, consigli per risparmiare]
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

def inject_gyg_links(text_line, dest_name):
    tour_matches = re.findall(r'\[TOUR:\s*(.*?)\]', text_line)
    for tour in tour_matches:
        query_string = f"{tour} {dest_name}"
        query_encoded = urllib.parse.quote(query_string)
        search_link = f"https://www.getyourguide.it/s?q={query_encoded}&partner_id=UR2ZJHB&utm_medium=online_publisher"
        html_link = f"<a href='{search_link}' style='color:#e67e22; font-weight:bold; text-decoration:underline;'>{tour}</a>"
        text_line = text_line.replace(f"[TOUR: {tour}]", html_link)
    return text_line

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
# ROTTA: /genera-standard
# ==========================================
@app.route('/genera-standard', methods=['POST'])
def genera_standard():
    data = request.json
    city_name = data.get('destination')
    lang_code = data.get('lang_code', 'IT')

    if not city_name:
        return jsonify({"error": "Destinazione mancante"}), 400

    city_clean = city_name.split(',')[0].strip()

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        if lang_code == "IT":
            sys_instruct = "Sei uno scrittore di viaggi esperto (stile Lonely Planet/National Geographic). Scrivi una guida DETTAGLIATA per:"
            base_prompt = TESTO_MODELLO_IT
            rules = """
            1. NON USARE MAI TABELLE MARKDOWN (niente righe con | |).
            2. Se devi fare un confronto, usa elenchi puntati descrittivi.
            3. Usa ESATTAMENTE la struttura seguente.
            4. Scrivi paragrafi ricchi e lunghi.
            5. Se viene inserita una nazione, una regione, un'area geografica produci la guida per la città principale, aggiungi una premessa prima del capitolo 1 in cui elenchi eventuali altre città esortando a fare guide separate, suggerisci anche di utilizzare il bottone dell'"ITINERARY WIZARD" che trovano nel sito.
            6. Se viene inserita un parola o una frase che non sono luoghi geografici rispondi in modo scherzoso ma sintetico, non usare la struttura della guida.
            7. Quando suggerisci un'escursione, un'attrazione, un tour o un museo specifico, SOLO E SOLTANTO SE SEI RAGIONEVOLMENTE CERTO CHE SI POSSA PRENOTARE TRAMITE GETYOURGUIDE ALLORA devi racchiudere il nome ESATTAMENTE in questo tag: [TOUR: Nome Attrazione]. Esempio: Ti consiglio di visitare il [TOUR: Colusseo].
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
        
        # Generazione del timestamp corretto e popolamento foglio
        timestamp = datetime.now().strftime("%d/%m %H:%M")
        log_to_sheets([timestamp, city_clean, "GUIDE_ONLY", "----", lang_code])
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Guide_{city_clean.replace(' ', '_')}.pdf"
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)