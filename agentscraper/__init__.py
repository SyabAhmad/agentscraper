"""
AgentScraper: Agent-based Google scraping with LLM integration.
"""

from typing import Dict, Any, Optional
from .config import Config
from .llm.groq import GroqProvider
from .agent.TitleAgent import TitleAgent
from .scrapers.GoogleScraper import GoogleScraper

__version__ = "0.1.0"

class AgentScraper:
    """Main AgentScraper class."""
    
    def __init__(self, llm_provider: str = "groq", llm_api_key: Optional[str] = None, 
                 use_selenium: bool = True, chrome_path: Optional[str] = None, edge_path: Optional[str] = None):
        """
        Initialize AgentScraper.
        
        Args:
            llm_provider (str): LLM provider to use. Currently only "groq" is supported.
            llm_api_key (str, optional): API key for the LLM provider.
            use_selenium (bool): Whether to use Selenium for scraping.
            chrome_path (str, optional): Path to Chrome binary.
            edge_path (str, optional): Path to Edge binary.
        """
        self.config = Config(llm_provider=llm_provider, llm_api_key=llm_api_key)
        
        # Initialize LLM provider
        provider_settings = self.config.get_provider_settings()
        if llm_provider == "groq":
            self.llm = GroqProvider(**provider_settings)
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")
            
        # Initialize scraper
        self.scraper = GoogleScraper(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", 
            timeout=self.config.timeout,
            use_selenium=use_selenium,
            chrome_path=chrome_path,
            edge_path=edge_path
        )
        
    def extract_titles(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """
        Extract titles from Google search results using the agent.
        
        Args:
            query (str): Search query.
            num_results (int): Number of results to request.
            
        Returns:
            Dict[str, Any]: Dictionary containing extracted titles.
        """
        # Get search results
        print(f"Searching Google for: {query}")
        html_content = self.scraper.search(query, num_results)
        
        # Always use the agent approach with LLM
        print("Using agent to analyze content...")
        agent = TitleAgent(self.llm)
        agent_results = agent.process(html_content)
        
        # If agent doesn't find titles, try direct extraction as fallback
        if len(agent_results["titles"]) == 0:
            print("Agent didn't find any titles, trying direct extraction...")
            direct_titles = self.scraper.extract_titles(html_content)
            if direct_titles:
                return {
                    "titles": direct_titles,
                    "count": len(direct_titles),
                    "method": "direct (fallback)"
                }
    
        # Return agent results (even if empty)
        return agent_results
        
    def extract_content(self, query: str, content_type: str, num_results: int = 10) -> Dict[str, Any]:
        """
        Extract specific content from Google search results.
        
        Args:
            query (str): Search query.
            content_type (str): Type of content to extract (faqs, descriptions, etc.)
            num_results (int): Number of results to request.
            
        Returns:
            Dict[str, Any]: Dictionary containing extracted content.
        """
        # Get search results
        print(f"Searching Google for: {query}")
        html_content = self.scraper.search(query, num_results)
        
        # For now, just extract titles as a fallback
        if content_type != "titles":
            print(f"Extraction type '{content_type}' not yet implemented, falling back to titles")
            return self.extract_titles(query, num_results)
        
        # In the future, you can add specialized agents for different content types
        # e.g., FAQAgent, DescriptionAgent, etc.
        
        return {
            "message": f"Extraction of {content_type} is not yet implemented",
            "titles": self.extract_titles(query, num_results)["titles"]
        }