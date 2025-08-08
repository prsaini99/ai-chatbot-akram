# AI Chatbot with Knowledge Base

A sophisticated AI chatbot that combines OpenAI's GPT models with a Retrieval-Augmented Generation (RAG) system to answer questions based on your own documents and knowledge base.

## Features

- **Hybrid Intelligence**: Combines GPT's general knowledge with your specific documents
- **Document Processing**: Supports PDF, Word, TXT, CSV, JSON, and Markdown files
- **Semantic Search**: Uses OpenAI embeddings for intelligent document retrieval
- **Three Chat Modes**: Hybrid, Knowledge Base Only, and General Chat
- **Real-time Document Upload**: Add new documents through the web interface
- **Source Citations**: Shows which documents were used to generate answers

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt

# Optional: Install python-dotenv for .env file support
pip install python-dotenv
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_api_key_here
```

### 3. Add Documents (Optional)

Place your documents in the `knowledge_base/` folder:
- Supported formats: .txt, .pdf, .docx, .csv, .json, .md
- Documents will be automatically processed on startup

### 4. Run the Application

```bash
# Using the run script (recommended)
python run.py

# Or run directly
python app.py
```

### 5. Access the Application

Open your browser and go to: http://localhost:5000

## Project Structure

```
ai-chatbot-akram/
├── app.py                 # Main Flask application
├── run.py                 # Startup script with checks
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── models/
│   └── knowledge_base.py  # Document processing and retrieval
├── routes/
│   └── chat_routes.py     # API endpoints
├── templates/
│   └── index.html         # Web interface
├── knowledge_base/        # Your documents go here
└── embeddings_cache/      # Cached embeddings (auto-created)
```

## Usage

### Chat Modes

1. **Hybrid Mode** (Default): Uses both knowledge base and general AI knowledge
2. **Knowledge Base Only**: Answers strictly from your documents
3. **General Chat**: Standard GPT conversation without document context

### Adding Documents

**Method 1: Web Interface**
1. Click "Add Document" in the Knowledge Base panel
2. Select your file and click "Upload to Knowledge Base"

**Method 2: File System**
1. Copy files to the `knowledge_base/` directory
2. Restart the application

### Supported File Types

- `.txt` - Plain text files
- `.pdf` - PDF documents
- `.docx` - Microsoft Word documents
- `.csv` - Comma-separated values
- `.json` - JSON data files
- `.md` - Markdown files

## Configuration

Edit the `.env` file to customize settings:

```env
# OpenAI Settings
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-3.5-turbo
MAX_TOKENS=500
TEMPERATURE=0.7

# Knowledge Base Settings
CHUNK_SIZE=500
CHUNK_OVERLAP=50
SIMILARITY_THRESHOLD=0.7
```

## How It Works

1. **Document Processing**: Documents are extracted, chunked, and converted to embeddings
2. **Query Processing**: User questions are matched against document embeddings
3. **Context Generation**: Relevant document chunks are included in the AI prompt
4. **Response Generation**: AI generates answers with source citations

## Troubleshooting

### Common Issues

**"Invalid API Key" Error**
- Verify your OpenAI API key in `.env`
- Ensure the key has access to both GPT and embedding models

**Slow First Response**
- Initial embedding generation takes time
- Subsequent queries use cached embeddings

**Documents Not Found**
- Check files are in `knowledge_base/` directory
- Verify file extension is supported
- Restart application after adding files

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python app.py
```

### Adding New File Types

Edit `models/knowledge_base.py` and add support in the `_extract_text` method.

## License

MIT License - Feel free to modify and use for your needs.