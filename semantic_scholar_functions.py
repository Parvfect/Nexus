
import requests
from utils import read_api_key
from text_extraction import extract_pdf_text_from_url
from data_members import SemanticNode, Graph
import logging
import regex as re


S2_API_KEY = read_api_key()


def search_for_paper(paper_title, limit=20):
    rsp = requests.get(
        'https://api.semanticscholar.org/graph/v1/paper/search',
        headers={'X-API-KEY': S2_API_KEY},
        params={'query': paper_title, 'limit': str(limit)}
    )

    if rsp.status_code == 200:
        logging.info("Search for paper %s successful", paper_title)
        return rsp.json()
    else:
        logging.error(
            "Search for paper returned status %s for query %s",
            rsp.status_code, paper_title
        )
        return None

def retrieve_paper(paper_id):

    rsp = requests.get(
        f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}',
        headers={'X-API-KEY': S2_API_KEY},
        params={'fields': 'title,url,year,authors,openAccessPdf,references,externalIds,referenceCount,fieldsOfStudy,s2FieldsOfStudy,journal,tldr,externalIds'})
    
    if rsp.status_code == 200:
        logging.info("Retrieving paper %s successful", paper_id)
        return rsp.json()
    else:
        logging.error(
            "Retrieving paper returned status %s for query %s",
            rsp.status_code, paper_id
        )
        return None
    

def bulk_retrieve_papers(paper_ids):

    rsp = requests.post(
    'https://api.semanticscholar.org/graph/v1/paper/batch',
    headers={'X-API-KEY': S2_API_KEY},
    params={'fields': 'referenceCount,citationCount,title,authors,openAccessPdf,externalIds,corpusId,year,influentialCitationCount,fieldsOfStudy,s2FieldsOfStudy,journal,authors,references,tldr'},
    json={"ids": paper_ids}
    )

    if rsp.status_code == 200:
        logging.info("Retriving bulk papers  for %s papers successful", len(paper_ids))
        return rsp.json()
    else:
        logging.error(
            "Retrieving bulk papers returned status %s for %s papers",
            rsp.status_code, len(paper_ids)
        )
        return None


def get_paper_pdf_urls(paper_objects):

    pdf_urls = []
    pattern = r"https?://[^\s,]+"  # matches http or https until a space or comma
    failure_counter = 0
    for i in paper_objects:
        try:
            pdf = i.get('openAccessPdf', {})
            url_candidate = pdf.get('url')
            if url_candidate and 'email' not in url_candidate:
                url = url_candidate
            else:
                disclaimer = i['openAccessPdf']['disclaimer']
                url = re.findall(pattern, disclaimer)[0]
                if 'email' in url:
                    url = ''
                if '/abs/' in url:  # Replacing arxiv abs pages to pdf
                    url = url.replace('/abs/', '/pdf/')
        except Exception as e:
            logging.error('Error in extracting pdf url for %s', i)
            failure_counter += 1
            url = ''

        pdf_urls.append(url)

    logging.info("Finished extracting pdf urls with %s failures", failure_counter)

    return pdf_urls


def create_connected_graph(work, relevance_search=False):
    # Given primary work - main node information, get the bulk references, extract pdf for all and create the connected graph

    reference_ids = [i['paperId'] for i in work['references']]

    reference_papers = bulk_retrieve_papers(paper_ids=reference_ids)

    paper_objects = [work] + reference_papers

    paper_urls = get_paper_pdf_urls(reference_papers)


    papers = [i for i in papers if i]

    nodes = [SemanticNode(i) for i in papers]

    pdf_urls = get_paper_pdf_urls(paper_objects=paper_objects)

    if relevance_search:
        fulltexts = [extract_pdf_text_from_url(i) for i in pdf_urls]

    # And then create the connected graph

    return