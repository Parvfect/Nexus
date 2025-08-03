import requests
import fitz  # PyMuPDF


def bulk_retrieve_works(ids: list[str], extract_from_url: bool = True):
    """
    Bulk retrieves works based on openalex ids. Accepts both urls and pure ids

    Args:
        ids - List of open alex ids
    Returns:
        works : list[Works] - unformatted data object
    """
    if extract_from_url:
        ids = [url.rstrip('/').split('/')[-1] for url in ids]

    pipe_separated_ids = "|".join(ids)
    r = requests.get(
        f"https://api.openalex.org/works?filter=ids.openalex:{pipe_separated_ids}&per-page=50")
    
    if r.status_code == 200:
        works = r.json()['results']
    else:
        print(f"Error fetching works {i}: Status {r.status_code}")
        return None
    
    return works


def search_by_title(title_query: str, n_results: int = 50):
    """
    Search OpenAlex by a title query
    """
    
    url = "https://api.openalex.org/works"
    params = {
        "search": title_query,
        "per_page": n_results
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        return []

    data = response.json()
    return data["results"]


def extract_pdf_text_from_url(url, save_as="temp.pdf"):
    """
    Extract fulltext from pdf url"""

    response = requests.get(url)
    with open(save_as, "wb") as f:
        f.write(response.content)

    doc = fitz.open(save_as)
    full_text = []
    for page in doc:
        full_text.append(page.get_text())
    doc.close()

    return "\n\n".join(full_text)

