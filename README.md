# Search Agents

A powerful Python-based search agent system that integrates multiple specialized agents for handling different types of queries. The system uses various APIs to provide real-time information about cryptocurrencies, stocks, weather, and general web searches.

## Features

- **Cryptocurrency Agent**: Get real-time prices for various cryptocurrencies
- **Stock Market Agent**: Fetch current stock prices and market data
- **Weather Agent**: Get weather information for any location
- **Web Search Agent**: Perform web searches with intelligent result summarization
- **Local LLM Integration**: Uses LM Studio for natural language processing and query routing

## Prerequisites

- Python 3.x
- LM Studio running locally (for LLM functionality)
- API keys for the following services:
  - Alpha Vantage (for stock data)
  - OpenWeather (for weather data)
  - Google Custom Search (for web searches)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env-example` to `.env`
   - Fill in your API keys in the `.env` file:
     ```
     ALPHAVANTAGE_API_KEY=your_key_here
     OPENWEATHER_API_KEY=your_key_here
     GOOGLE_API_KEY=your_key_here
     SEARCH_ENGINE_ID=your_search_engine_id
     ```

## Usage

1. Start LM Studio and ensure it's running on `http://localhost:1234`

2. Run the main script:

```bash
python main.py
```

3. Enter your queries in natural language. The system will automatically route them to the appropriate agent. Examples:

   - "What's the price of Bitcoin?"
   - "How's the weather in Tokyo?"
   - "What's the current price of Tesla stock?"
   - "Tell me about the latest iPhone"

4. Type 'exit' or 'quit' to end the session

## Available Agents

### Crypto Asset Agent

- Handles cryptocurrency price queries
- Uses CoinGecko API
- Example: "What's the price of ethereum?"

### Stock Asset Agent

- Provides real-time stock market data
- Uses Alpha Vantage API
- Example: "What's the current price of AAPL?"

### Weather Asset Agent

- Delivers weather information for locations
- Uses OpenWeather API
- Example: "What's the weather in New York?"

### Web Asset Agent

- Performs web searches with result summarization
- Uses Google Custom Search API
- Example: "Tell me about quantum computing"

## Error Handling

The system includes comprehensive error handling for:

- API failures
- Invalid inputs
- Network issues
- Missing API keys
- Data parsing errors

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
