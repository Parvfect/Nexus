
from typing import Any

class Author:
    name: str
    affiliation: str

class Paper:
    title: str
    authors : list[Author]
    cited_by_doi : list[Author]
    cited_by_papers: list[Any]

    
    

