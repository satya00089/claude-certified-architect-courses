from mcp.server.fastmcp import FastMCP, Context
from mcp.types import SamplingMessage, TextContent
import httpx
import json

mcp = FastMCP(name="Wikipedia Research Assistant")


async def search_wikipedia(query: str) -> list:
    """Search Wikipedia for a topic."""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": 5,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        return data.get("query", {}).get("search", [])


async def get_wikipedia_content(title: str) -> str:
    """Get the content of a Wikipedia article."""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": title,
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
        "format": "json",
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        
        for page in pages.values():
            if "extract" in page:
                return page["extract"]
        
        return "Content not found."


@mcp.tool()
async def research_topic(topic: str, ctx: Context):
    """Research a topic on Wikipedia and create a comprehensive report."""
    
    # Search for relevant articles
    search_results = await search_wikipedia(topic)
    
    if not search_results:
        return "No Wikipedia articles found for this topic."
    
    # Get content from top results
    articles_content = []
    for result in search_results[:3]:  # Top 3 results
        title = result["title"]
        content = await get_wikipedia_content(title)
        articles_content.append(f"=== {title} ===\n\n{content}")
    
    combined_content = "\n\n".join(articles_content)
    
    # Use Claude to create a comprehensive report
    prompt = f"""
Based on the following Wikipedia content about "{topic}", please create a comprehensive research report. 
Include:
1. An overview/introduction
2. Key points and important information
3. Historical context (if relevant)
4. Current significance or applications
5. A brief conclusion

Wikipedia Content:
{combined_content}

Please provide a well-structured, informative report.
"""

    result = await ctx.session.create_message(
        messages=[
            SamplingMessage(
                role="user", content=TextContent(type="text", text=prompt)
            )
        ],
        max_tokens=4000,
        system_prompt="You are a helpful research assistant specializing in creating comprehensive, well-structured reports from Wikipedia content. Be informative, accurate, and engaging.",
    )

    if result.content.type == "text":
        return result.content.text
    else:
        raise ValueError("Research failed")


if __name__ == "__main__":
    mcp.run(transport="stdio")
