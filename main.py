import os
import re
import logging
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO)

class SearchAgents:
    @staticmethod
    def crypto_asset(query: str) -> str:
        """Handle cryptocurrency prices with validation."""
        try:
            coin_id = query.strip().lower()
            # Allow coin names that can include hyphens (e.g., "bitcoin-cash")
            if not re.match(r'^[a-z\-]+$', coin_id):
                return "Invalid cryptocurrency format - use names like 'bitcoin' not symbols."
            
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                error_message = response.json().get("error", "Unknown error")
                return f"Crypto API Error: {error_message}"
            
            data = response.json()
            if coin_id not in data:
                return f"Unknown cryptocurrency: {coin_id}"
            
            price = data[coin_id].get('usd')
            if price is None:
                return f"Price data not available for {coin_id}"
            return f"{coin_id.capitalize()}: ${price}"
        except Exception as e:
            logging.exception("Error fetching cryptocurrency data")
            return f"Crypto Error: {str(e)}"

    @staticmethod
    def stock_asset(symbol: str) -> str:
        """Handle stock market data."""
        try:
            symbol = symbol.strip().upper()
            api_key = os.getenv('ALPHAVANTAGE_API_KEY')
            if not api_key:
                return "Stock API Error: Missing API key."
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
            response = requests.get(url, timeout=10)
            data = response.json()
            quote = data.get("Global Quote")
            if not quote or "05. price" not in quote:
                return f"Stock data not available for {symbol}."
            return f"{symbol}: ${quote['05. price']}"
        except Exception as e:
            logging.exception("Error fetching stock data")
            return f"Stock API Error: {str(e)}"

    @staticmethod
    def weather_asset(location: str) -> str:
        """Handle weather data with improved error handling."""
        try:
            location = location.strip()
            api_key = os.getenv('OPENWEATHER_API_KEY')
            if not api_key:
                return "Weather Error: Missing API key."
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                error_message = response.json().get("message", "Unknown error")
                return f"Weather Error: {error_message}"
            data = response.json()
            temp = data.get('main', {}).get('temp')
            weather_desc = data.get('weather', [{}])[0].get('description', '').capitalize()
            city_name = data.get('name', location)
            if temp is None or not weather_desc:
                return "Incomplete weather data received."
            return f"{city_name}: {temp}°C, {weather_desc}"
        except Exception as e:
            logging.exception("Error fetching weather data")
            return f"Weather Error: {str(e)}"

    @staticmethod
    def web_asset(query: str):
        """Handle general web searches."""
        try:
            google_api_key = os.getenv("GOOGLE_API_KEY")
            search_engine_id = os.getenv("SEARCH_ENGINE_ID")
            if not google_api_key or not search_engine_id:
                return "Web Search Error: Missing Google API key or Search Engine ID."
            url = f"https://www.googleapis.com/customsearch/v1?key={google_api_key}&cx={search_engine_id}&q={query}"
            response = requests.get(url, timeout=10)
            results = response.json()
            items = results.get("items", [])
            return [
                {
                    "title": item.get("title", "No Title"),
                    "link": item.get("link", "No Link"),
                    "snippet": item.get("snippet", "")
                } for item in items[:3]
            ]
        except Exception as e:
            logging.exception("Error during web search")
            return f"Web Search Error: {str(e)}"


def query_llm(prompt: str) -> str:
    """Interface with local LLM through LM Studio."""
    llm_endpoint = "http://localhost:1234/v1/chat/completions"
    system_msg = """You are a routing assistant. Format responses STRICTLY as:
    [agent_type] query

    Available agents:
    - crypto_asset: Cryptocurrency prices (e.g., "[crypto_asset] ethereum")
    - stock_asset: Stock prices (e.g., "[stock_asset] tsla")
    - weather_asset: Weather (e.g., "[weather_asset] tokyo")
    - web_asset: Web searches (e.g., "[web_asset] pixel 9 reviews")

    If unsure, provide a general answer. NEVER include text outside brackets!"""
    
    try:
        response = requests.post(
            llm_endpoint,
            json={
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 100
            },
            timeout=10
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return content
    except Exception as e:
        logging.exception("LLM query error")
        return f"LLM Error: {str(e)}"


def summarize_results(query: str, results) -> str:
    """Summarize web search results using local LLM."""
    llm_endpoint = "http://localhost:1234/v1/chat/completions"
    context = "\n".join([f"{r['title']}: {r['snippet']}" for r in results])
    try:
        response = requests.post(
            llm_endpoint,
            json={
                "messages": [
                    {"role": "system", "content": f"Summarize web results about {query} in 3 concise points"},
                    {"role": "user", "content": context}
                ],
                "temperature": 0.3,
                "max_tokens": 300
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logging.exception("Summarization error")
        return f"Summarization Error: {str(e)}"


def parse_llm_response(response: str):
    """
    Parse LLM response expecting the format:
    [agent_type] query
    Returns a tuple of (agent_type, query) if the pattern is matched;
    otherwise, returns (None, response).
    """
    pattern = r'^\[(\w+)\]\s*(.+)$'
    match = re.match(pattern, response.strip())
    if match:
        return match.group(1), match.group(2)
    return None, response


def main():
    agents = SearchAgents()
    valid_agents = ["crypto_asset", "stock_asset", "weather_asset", "web_asset"]
    print("Search Agent System Initialized. Type 'exit' to quit.")
    
    while True:
        user_input = input("\nUser: ").strip()
        if user_input.lower() in ['exit', 'quit']:
            break
        
        llm_response = query_llm(user_input)
        agent_type, query = parse_llm_response(llm_response)

        # Clean and validate query
        query = query.split('(')[0].strip().lower() if query else ""
        
        if agent_type:
            try:
                # Validate agent type
                if agent_type not in valid_agents:
                    print(f"Assistant: Unknown agent type: {agent_type}")
                    continue
                
                if agent_type == "web_asset":
                    results = agents.web_asset(query)
                    if isinstance(results, str):
                        print(f"Assistant: {results}")
                    elif not results:
                        print("Assistant: No relevant results found.")
                    else:
                        summary = summarize_results(query, results)
                        print(f"Assistant: Here's what I found about {query}:")
                        print(summary)
                        print("\nSources:")
                        for idx, result in enumerate(results, 1):
                            print(f"{idx}. {result['title']}\n   {result['link']}")
                else:
                    method = getattr(agents, agent_type)
                    result = method(query)
                    print(f"Assistant: {result}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Assistant: Network error - {str(e)}")
            except KeyError as e:
                print(f"Assistant: Data parsing error - missing {str(e)}")
            except Exception as e:
                print(f"Assistant: Unexpected error - {str(e)}")
        else:
            # Handle general responses
            print(f"Assistant: {llm_response}")

def parse_llm_response(response):
    """Improved response parser with format validation"""
    try:
        if response.startswith('[') and ']' in response:
            agent_part, _, query = response.partition(']')
            agent_type = agent_part[1:].strip()
            return agent_type, query.strip()
        
        # Fallback: Check for agent patterns without brackets
        for agent in ["crypto_asset", "stock_asset", "weather_asset", "web_asset"]:
            if response.lower().startswith(agent + " "):
                return agent, response[len(agent)+1:].strip()
                
        return None, response
    except Exception as e:
        logging.error(f"Parse error: {str(e)}")
        return None, response


if __name__ == "__main__":
    main()