import requests

def search_crossref_by_title(title):
    url = "https://api.crossref.org/works"
    params = {
        "query.title": title,
        "rows": 1,  # Limit to 1 best match
        "select": "title,author,DOI,publisher,issued,URL"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        items = response.json()["message"]["items"]
        if items:
            paper = items
            return paper
        else:
            print("No matching paper found.")
            return None
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# Example usage
title = "Motif Caller: Sequence Reconstruction for motif-based dna storage"
paper = search_crossref_by_title(title)

if paper:
    for paper_ in paper:
        print("Title:", paper_["title"][0])
        print(paper_.keys())
    #print("DOI:", paper["DOI"])
    #print("URL:", paper.get("URL"))
    #print("Publisher:", paper.get("publisher"))
    #print("Authors:", ", ".join(f"{a.get('given', '')} {a.get('family', '')}" for a in paper.get("author", [])))
    #print("Year:", paper["issued"]["date-parts"][0][0])
