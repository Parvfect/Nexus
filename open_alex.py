import requests

def search_openalex(query, per_page=5):
    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per_page": per_page
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        return []

    data = response.json()
    return data["results"]

# Example usage
results = search_openalex("Attention is all you need")

for i, paper in enumerate(results, 1):
    #print(paper.keys())
    #print(dir(paper))
    #print(paper['title'])
    #print(paper['referenced_works'])
    print(paper.keys())
    print(paper['cited_by_count'])
    print(paper['primary_location'])
    print(paper['corresponding_author_ids'])
    
    