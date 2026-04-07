# Wikipedia Research Assistant

A Next.js chat application that uses MCP (Model Context Protocol) to create an AI-powered Wikipedia research assistant.

## Features

- 🔍 Search and research Wikipedia topics
- 🤖 AI-powered comprehensive reports using Claude
- 💬 Beautiful chat interface
- 🔄 Real-time streaming responses
- 📚 Multi-source Wikipedia content aggregation

## Architecture

The app uses a client-server MCP architecture:

1. **Next.js Frontend** (`app/`) - React-based chat UI
2. **API Route** (`app/api/chat/`) - Handles MCP client connection
3. **MCP Server** (`mcp-server/server.py`) - FastMCP server with Wikipedia tools
4. **Sampling Callback** - Delegates LLM calls to Claude API

## Setup

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- uv (Python package installer)
- Anthropic API key

### Installation

1. Install Node.js dependencies:

```bash
npm install
```

2. Install Python dependencies:

```bash
cd mcp-server
pip install -r requirements.txt
# or with uv:
uv pip install -r requirements.txt
```

3. Create `.env.local` file:

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

### Running the App

1. Start the development server:

```bash
npm run dev
```

2. Open [http://localhost:3000](http://localhost:3000)

### Code Quality

Run linting and formatting:

```bash
# Check for linting errors
npm run lint

# Format code with Prettier
npm run format
```

ESLint is configured with Next.js best practices including:

- TypeScript type checking
- React Hooks rules
- Core Web Vitals
- Custom rules for code quality

## How It Works

### MCP Sampling Flow

```
User Query → Next.js UI → API Route → MCP Client
                                          ↓
                                    MCP Server (server.py)
                                          ↓
                                  Wikipedia API Search
                                          ↓
                                  Sampling Request
                                          ↓
                                  Sampling Callback
                                          ↓
                                    Claude API
                                          ↓
                                  Research Report → User
```

The MCP server:

1. Receives research requests via tools
2. Fetches Wikipedia content
3. Makes sampling requests to delegate report generation to Claude
4. Returns comprehensive reports to the client

### Key Files

- `app/page.tsx` - Main chat UI component
- `app/api/chat/route.ts` - MCP client integration
- `mcp-server/server.py` - Wikipedia research MCP server
- `app/page.module.css` - Styling

## Example Queries

- "Research and write a report on geotechnical engineering"
- "What are the key discoveries in quantum computing?"
- "Explain the history and impact of the Renaissance"

## Technologies

- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **MCP SDK** - Model Context Protocol
- **FastMCP** - Python MCP framework
- **Claude (Anthropic)** - LLM for report generation
- **Wikipedia API** - Content source

## License

MIT
