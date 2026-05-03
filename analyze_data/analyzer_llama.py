import json
import random
import time
import requests
from tqdm import tqdm

# --- SETTINGS ---
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3" # We are using the Llama 3 8B model
EVENTS_FILE = "../fetch_ news/events.json"  # events.json is in the fetch_ news folder
OUTPUT_FILE = "ohlc_data.json"               # output stays in the same analyze_data folder

session = requests.Session()

def analyze_with_llama(text):
    """Sends the news text to Llama 3 and gets a sentiment score between -100 and +100."""
    
    prompt = f"""You are a highly intelligent 1968 military intelligence officer analyzing news events related to the Vietnam War. 
Read the following news event and rate it on a scale from -100 to 100.
-100 means extreme war escalation, combat, violence, bombings, assassinations, or military aggression.
100 means extreme peace, ceasefires, diplomacy, troop withdrawals, anti-war protests, or de-escalation.
0 means neutral.

CRITICAL INSTRUCTION: You MUST output ONLY a single integer between -100 and 100. Do not output any other text, explanations, or punctuation.

News: {text}"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0, # For exact and clear answers
            "num_predict": 4,   # Stop immediately after 4 words since it will only produce a number (Speeds up tremendously)
            "num_ctx": 256      # Narrow context window (Relieves GPU memory and speeds up)
        }
    }
    
    try:
        response = session.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        response_text = result.get("response", "").strip()
        
        # Try to extract only the number
        # Sometimes AI stubbornly says "The score is -50", so we clean it
        cleaned_text = ''.join(c for c in response_text if c.isdigit() or c == '-')
        if cleaned_text == '' or cleaned_text == '-':
            score = 0
        else:
            score = int(cleaned_text)
            
        # Prevent it from exceeding boundaries
        score = max(-100, min(100, score))
        return score
        
    except Exception as e:
        # If Ollama is off or an error occurs, return 0
        return 0

def main():
    print("1/3: Reading news from 'events.json' file...")
    try:
        with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
            events = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {EVENTS_FILE} not found!")
        return

    # Are we going to process all data for testing? Or limited?
    # Processing all data (13763 items).
    
    print(f"2/3: Sentiment Analysis Starting with Llama 3 Model... (Total: {len(events)} News)")
    print("NOTE: Make sure Ollama is open in the background and the 'llama3' model is installed.")
    
    processed_data = []
    starting_price = 1000.0 # Stock starting price
    current_price = starting_price
    
    start_time = time.time()
    
    # Progress bar (tqdm)
    for event in tqdm(events, desc="Processing Data", unit="news", dynamic_ncols=True):
        text = event['text']
        date = event['date']
        
        # 1. AI Analysis (Request sent to Llama 3)
        score = analyze_with_llama(text)
        
        # 2. Labeling (For UI)
        if score > 0:
            ui_label = "PRO-PEACE"
        elif score < 0:
            ui_label = "PRO-WAR"
        else:
            ui_label = "NEUTRAL"
            
        # 3. CANDLE ALGORITHM (Linear / Additive)
        open_price = current_price
        
        # Price change proportional to score (+/- 5 points max daily individual change)
        price_change_amount = (score / 100) * random.uniform(1.0, 5.0)
        close_price = open_price + price_change_amount
        
        # Wicks
        volatility = abs(score / 100) * random.uniform(1.0, 3.0)
        high_price = max(open_price, close_price) + volatility
        low_price = min(open_price, close_price) - volatility
        
        volume = int(abs(score) * random.uniform(50, 200))
        if volume == 0: volume = random.randint(10, 50)
        
        processed_data.append({
            "time": date,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "volume": volume,
            "text": text,
            "ai_label": ui_label,
            "ai_confidence": float(abs(score)), # We are now showing the severity score directly instead of the confidence score
            "sentiment_index": float(score)
        })
        
        current_price = close_price # Continues in a chain

    end_time = time.time()
    
    print("\n3/3: Stock data being saved in JSON format...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=4)
        
    print(f"Process completed! Total {len(events)} news processed with Llama 3 in {round(end_time - start_time, 2)} seconds.")
    print(f"File '{OUTPUT_FILE}' updated. You can view the results from the terminal.")

if __name__ == "__main__":
    # Check if Ollama server is open
    try:
        requests.get("http://localhost:11434/")
    except requests.exceptions.ConnectionError:
        print("[!] ERROR: Ollama is not running in the background!")
        print("Please start Ollama and make sure you run 'ollama run llama3' in the terminal once.")
        exit(1)
        
    main()
