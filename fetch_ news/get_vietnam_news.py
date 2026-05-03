import requests
import time
import json
import sys

# Paste your own NYT API key here
API_KEY = "CsKc5OQzXVJGdllH3Yso6Jl0cZdlDQk7mCgWVnQqhKqQiZhO"

# Years we want to scan
START_YEAR = 1950
END_YEAR = 1980

vietnam_news = []

print(f"\n--- Scanning between {START_YEAR}-{END_YEAR} Starting ---")
print("Waiting 12 seconds between each request to avoid being blocked by NYT API limits...")
print("This process will take a long time (31 years * 12 months = 372 months, approx. 1.2 hours).\n")

total_months = (END_YEAR - START_YEAR + 1) * 12
completed_months = 0

for year in range(START_YEAR, END_YEAR + 1):
    for month in range(1, 13):
        url = f"https://api.nytimes.com/svc/archive/v1/{year}/{month}.json?api-key={API_KEY}"
        
        completed_months += 1
        percentage = int((completed_months / total_months) * 100)
        
        # Progress Bar Animation
        bar_length = 30
        filled_part = int((completed_months / total_months) * bar_length)
        bar = "█" * filled_part + "-" * (bar_length - filled_part)
        
        sys.stdout.write(f"\rProgress: [{bar}] {percentage}% | Year: {year} Month: {month} ({completed_months}/{total_months}) | Found: {len(vietnam_news)} ")
        sys.stdout.flush()

        try:
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if 'response' in data and 'docs' in data['response']:
                    for doc in data['response']['docs']:
                        if 'main' in doc['headline'] and doc['headline']['main']:
                            headline = doc['headline']['main']
                            date = doc['pub_date'][:10]
                            
                            if 'vietnam' in headline.lower():
                                vietnam_news.append({
                                    "date": date,
                                    "text": headline
                                })
            else:
                print(f"\n[!] Error: Year {year} month {month} could not be fetched. API Error Code: {response.status_code}")
                
            # No need to wait on the last step
            if completed_months != total_months:
                time.sleep(12)
                
        except Exception as e:
            print(f"\n[!] An error occurred: {e}")

# Saving data in JSON format
file_name = f"vietnam_news_{START_YEAR}_{END_YEAR}.json"
with open(file_name, "w", encoding="utf-8") as f:
    json.dump(vietnam_news, f, ensure_ascii=False, indent=2)

print(f"\n\n✅ Process Completed! Total {len(vietnam_news)} news found between the years {START_YEAR}-{END_YEAR}.")
print(f"Results saved to '{file_name}' file.")
