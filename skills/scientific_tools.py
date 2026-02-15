import arxiv
import requests
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ScientificResearchManager:
    """
    Manages search and retrieval of academic papers from ArXiv and Semantic Scholar.
    """
    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider
        self.client = arxiv.Client()

    def search_arxiv(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Searches ArXiv for papers on a given topic.
        """
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = []
        for result in self.client.results(search):
            results.append({
                "title": result.title,
                "authors": [a.name for a in result.authors],
                "summary": result.summary,
                "url": result.entry_id,
                "published": result.published.isoformat(),
                "category": result.primary_category
            })
        
        return results

    def search_semantic_scholar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Searches Semantic Scholar for papers and their impact metrics.
        """
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={limit}&fields=title,authors,abstract,url,citationCount,year"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []
                for paper in data.get("data", []):
                    results.append({
                        "title": paper.get("title"),
                        "authors": [a.get("name") for a in paper.get("authors", [])],
                        "summary": paper.get("abstract"),
                        "url": paper.get("url"),
                        "citations": paper.get("citationCount"),
                        "year": paper.get("year")
                    })
                return results
            else:
                logger.error(f"Semantic Scholar API error: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error searching Semantic Scholar: {e}")
            return []

    def synthesize_findings(self, papers: List[Dict[str, Any]]) -> str:
        """
        Synthesizes findings from a list of papers (optional helper for agents).
        """
        if not papers:
            return "No papers found to synthesize."
        
        summary = "Summary of research findings:\n\n"
        for i, paper in enumerate(papers):
            summary += f"{i+1}. {paper['title']} ({paper.get('year') or paper.get('published', '')})\n"
            summary += f"   Authors: {', '.join(paper['authors'][:3])}...\n"
            summary += f"   Snippet: {paper['summary'][:200]}...\n\n"
        
        return summary

if __name__ == "__main__":
    # Quick test
    manager = ScientificResearchManager()
    arxiv_results = manager.search_arxiv("Artificial General Intelligence", 2)
    print(f"ArXiv results: {len(arxiv_results)}")
    ss_results = manager.search_semantic_scholar("AGI alignment", 2)
    print(f"Semantic Scholar results: {len(ss_results)}")
