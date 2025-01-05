import requests
import json

def fetch_papers(query="machine learning", max_results=100):
    base_url = "https://api.openalex.org/works"
    params = {
        "filter": f"title.search:{query}",
        "per_page": 50
    }

    results = []
    page = 1

    while len(results) < max_results:
        print(f"Fetching page {page}...")
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print("Error fetching data:", response.text)
            break
        
        data = response.json()
        results.extend(data.get("results", []))
        
        # Stop if no more data
        if "next" not in data.get("meta", {}):
            break
        
        page += 1

    return results

def save_data(data, output_file):
    with open(output_file, "w") as f:
        json.dump(data, f)

if __name__ == "__main__":
    query = "machine learning"
    results = fetch_papers(query=query, max_results=100)
    save_data(results, "../data/raw_papers.json")
    print(f"Saved {len(results)} papers to ../data/raw_papers.json")
