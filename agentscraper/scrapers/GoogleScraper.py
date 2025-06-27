"""Google scraper module using Selenium for better results."""

import time
import random
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List
import urllib.parse
import sys
import os

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    selenium_available = True
except ImportError:
    selenium_available = False

class GoogleScraper:
    """Scraper for Google search results."""
    
    def __init__(self, user_agent: str = None, timeout: int = 30, use_selenium: bool = True, 
                 chrome_path: str = None, edge_path: str = None):
        """
        Initialize the Google scraper.
        
        Args:
            user_agent (str): The User-Agent header to use.
            timeout (int): Request timeout in seconds.
            use_selenium (bool): Whether to use Selenium for scraping.
            chrome_path (str): Path to Chrome binary (optional).
            edge_path (str): Path to Edge binary (optional).
        """
        self.timeout = timeout
        # Only use Selenium if it's available and requested
        self.use_selenium = use_selenium and selenium_available
        self.chrome_path = chrome_path
        self.edge_path = edge_path
        
        if not user_agent:
            self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        else:
            self.user_agent = user_agent
            
        # Headers for requests method
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate", 
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "Referer": "https://www.google.com/"
        }
        
    def _initialize_selenium(self):
        """Initialize Selenium WebDriver with Chrome or Edge."""
        # Try Chrome first
        driver = self._initialize_chrome()
        
        # If Chrome initialization failed, try Edge
        if driver is None:
            print("Chrome initialization failed, trying Microsoft Edge...")
            driver = self._initialize_edge()
            
        return driver
        
    def _initialize_chrome(self):
        """Initialize Chrome WebDriver."""
        try:
            options = ChromeOptions()
            options.add_argument(f"user-agent={self.user_agent}")
            options.add_argument("--headless=new")  # New headless mode
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            # Set Chrome binary path if provided
            if self.chrome_path and os.path.exists(self.chrome_path):
                print(f"Using Chrome binary at: {self.chrome_path}")
                options.binary_location = self.chrome_path
                
            # Try with ChromeDriverManager for auto-downloading the driver
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            
            # Disable webdriver flags
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("Successfully initialized Chrome WebDriver")
            return driver
            
        except Exception as e:
            print(f"Chrome initialization failed: {e}")
            return None
            
    def _initialize_edge(self):
        """Initialize Edge WebDriver."""
        try:
            options = EdgeOptions()
            options.add_argument(f"user-agent={self.user_agent}")
            options.add_argument("--headless=new")  # New headless mode
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            # Set Edge binary path if provided
            if self.edge_path and os.path.exists(self.edge_path):
                print(f"Using Edge binary at: {self.edge_path}")
                options.binary_location = self.edge_path
                
            # Try with EdgeDriverManager for auto-downloading the driver
            driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
            
            # Disable webdriver flags
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("Successfully initialized Edge WebDriver")
            return driver
            
        except Exception as e:
            print(f"Edge initialization failed: {e}")
            return None
            
    def search(self, query: str, num_results: int = 10) -> str:
        """
        Perform a Google search and return the raw HTML.
        
        Args:
            query (str): The search query.
            num_results (int): Number of results to request.
            
        Returns:
            str: The raw HTML response.
        """
        if self.use_selenium:
            html_content = self._search_with_selenium(query, num_results)
            if html_content:
                return html_content
            # If selenium fails, fall back to requests
            print("Selenium failed, falling back to requests...")
            
        return self._search_with_requests(query, num_results)
    
    def _search_with_requests(self, query: str, num_results: int = 10) -> str:
        """Search using requests library."""
        escaped_query = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={escaped_query}&num={num_results}"
        
        # Add a small random delay to seem more human-like
        time.sleep(random.uniform(0.5, 2.0))
        
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        
        return response.text
    
    def _search_with_selenium(self, query: str, num_results: int = 10) -> str:
        """Search using Selenium WebDriver."""
        try:
            driver = self._initialize_selenium()
            escaped_query = urllib.parse.quote_plus(query)
            url = f"https://www.google.com/search?q={escaped_query}&num={num_results}"
            
            driver.get(url)
            
            # Wait for page to load (search results)
            WebDriverWait(driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.g, div[jscontroller]"))
            )
            
            # Add some random wait to emulate human behavior
            time.sleep(random.uniform(1, 3))
            
            # Get the page source
            page_source = driver.page_source
            
            # Close the browser
            driver.quit()
            
            return page_source
        except Exception as e:
            print(f"Selenium error: {e}")
            # Fall back to requests
            return self._search_with_requests(query, num_results)
        
    def extract_titles(self, html_content: str) -> List[str]:
        """
        Extract titles directly from HTML using BeautifulSoup.
        
        Args:
            html_content (str): HTML content from search results
            
        Returns:
            List[str]: List of titles
        """
        titles = []
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Google usually puts titles in h3 tags
        for heading in soup.find_all('h3'):
            if heading.text.strip():
                titles.append(heading.text.strip())
        
        # Look for titles in result containers (different Google formats)
        for result in soup.select('div.g'):
            # Try to find title within result
            h3 = result.select_one('h3')
            if h3 and h3.text.strip():
                titles.append(h3.text.strip())
                
        # Get titles from other possible locations
        for elem in soup.select('a[href^="/url"]'):
            h3 = elem.select_one('h3')
            if h3 and h3.text.strip() and h3.text.strip() not in titles:
                titles.append(h3.text.strip())
                
        # Filter out very short titles and duplicates
        clean_titles = []
        for title in titles:
            if title and len(title) > 5 and title not in clean_titles:
                clean_titles.append(title)
                
        return clean_titles