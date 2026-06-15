from functools import lru_cache
from typing import Optional
import logging

from app.domain.external.search import SearchEngine
from app.core.config import get_settings

logger = logging.getLogger(__name__)

@lru_cache()
def get_search_engine() -> Optional[SearchEngine]:
    """Get search engine instance based on configuration"""
    settings = get_settings()
    if settings.search_provider == "google":
        from app.infrastructure.external.search.google_search import GoogleSearchEngine
        if settings.google_search_api_key and settings.google_search_engine_id:
            logger.info("Initializing Google Search Engine")
            return GoogleSearchEngine(
                api_key=settings.google_search_api_key,
                cx=settings.google_search_engine_id
            )
        else:
            logger.warning("Google Search Engine not initialized: missing API key or engine ID")
    elif settings.search_provider == "baidu":
        from app.infrastructure.external.search.baidu_search import BaiduSearchEngine
        if settings.baidu_search_api_key:
            logger.info("Initializing Baidu Search Engine (API)")
            return BaiduSearchEngine(api_key=settings.baidu_search_api_key)
        else:
            logger.warning("Baidu Search Engine not initialized: missing API key (BAIDU_SEARCH_API_KEY)")
    elif settings.search_provider == "baidu_web":
        from app.infrastructure.external.search.baidu_web_search import BaiduWebSearchEngine
        logger.info("Initializing Baidu Web Search Engine (scraping)")
        return BaiduWebSearchEngine()
    elif settings.search_provider == "bing":
        from app.infrastructure.external.search.bing_search import BingSearchEngine
        if settings.bing_search_api_key:
            logger.info("Initializing Bing Search Engine (API)")
            return BingSearchEngine(api_key=settings.bing_search_api_key)
        else:
            logger.warning("Bing Search Engine not initialized: missing API key (BING_SEARCH_API_KEY)")
    elif settings.search_provider == "bing_web":
        from app.infrastructure.external.search.bing_web_search import BingWebSearchEngine
        logger.info("Initializing Bing Web Search Engine (scraping)")
        return BingWebSearchEngine()
    elif settings.search_provider == "tavily":
        from app.infrastructure.external.search.tavily_search import TavilySearchEngine
        if settings.tavily_api_key:
            logger.info("Initializing Tavily Search Engine")
            return TavilySearchEngine(api_key=settings.tavily_api_key)
        else:
            logger.warning("Tavily Search Engine not initialized: missing API key")
    else:
        logger.warning(f"Unknown search provider: {settings.search_provider}")
    
    return None 