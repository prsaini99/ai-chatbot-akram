# AI Chatbot with Knowledge Base

A sophisticated AI chatbot that combines OpenAI's GPT models with a Retrieval-Augmented Generation (RAG) system to answer questions based on your own documents and knowledge base.

## 🎯 Features

- **🤖 AI Personality Management**: 5 different AI personalities (Sales Expert, Assistant, Support, Consultant, Educator)
- **📚 Knowledge Base Only Mode**: Answers strictly from your uploaded documents
- **📄 Document Processing**: Supports PDF, Word, TXT, CSV, JSON, and Markdown files
- **🔍 Semantic Search**: Uses OpenAI embeddings for intelligent document retrieval
- **⚡ Real-time Document Upload**: Add new documents through the web interface
- **📋 Source Citations**: Shows which documents were used to generate answers
- **⚙️ Custom System Prompts**: Create and manage your own AI personalities
- **🎭 Real-time Personality Switching**: Change AI behavior without restart

## 🚀 Quick Start (Local Development)

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_api_key_here
```

### 3. Run the Application

```bash
# Using the run script (recommended)
python3 run.py
```

### 4. Access the Application

Open your browser and go to: **http://localhost:5000**

## 🌐 Deploy to Vercel

### Prerequisites
- GitHub account with your code pushed
- Vercel account (free tier available)
- OpenAI API key

### Step 1: Import Project to Vercel

1. **Go to [Vercel Dashboard](https://vercel.com/dashboard)**
2. **Click "New Project"**
3. **Import your GitHub repository**
4. **Configure the following:**
   - Framework Preset: **Other**
   - Root Directory: **.**
   - Build Command: **(leave empty)**
   - Output Directory: **(leave empty)**

### Step 2: Set Environment Variables

In Vercel Dashboard → Your Project → Settings → Environment Variables, add:

```env
OPENAI_API_KEY=your_actual_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
MAX_TOKENS=500
TEMPERATURE=0.7
TOP_P=1.0
FREQUENCY_PENALTY=0
PRESENCE_PENALTY=0
KNOWLEDGE_BASE_DIR=./knowledge_base
EMBEDDINGS_CACHE_DIR=./embeddings_cache
CHUNK_SIZE=500
CHUNK_OVERLAP=50
MAX_CONTEXT_LENGTH=2000
SIMILARITY_THRESHOLD=0.3
PORT=5000
HOST=0.0.0.0
DEBUG=false
VERCEL=true
```

**⚠️ Important:** 
- Set all environment variables for **Production**, **Preview**, and **Development**
- Never commit your actual API key to GitHub - only set it in Vercel

### Step 3: Deploy

1. **Click "Deploy"** in Vercel
2. **Wait for deployment** (usually 1-2 minutes)
3. **Your app will be live** at `https://your-project-name.vercel.app`

### Step 4: Test Your Deployment

1. Visit your live URL
2. Try uploading a document
3. Ask questions about the document
4. Test different AI personalities

## 🔧 Project Structure

```
ai-chatbot-akram/
├── app.py                 # Main Flask application
├── run.py                 # Local startup script
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel deployment config
├── .vercelignore         # Files to ignore during deployment
├── .env.example          # Environment variables template
├── .env                  # Your local environment (not committed)
├── .gitignore           # Git ignore rules
├── api/
│   └── index.py          # Vercel serverless entry point
├── models/
│   └── knowledge_base.py # Document processing and retrieval
├── routes/
│   └── chat_routes.py    # API endpoints
├── templates/
│   └── index.html        # Web interface
├── knowledge_base/       # Your documents (local only)
└── embeddings_cache/     # Cached embeddings (local only)
```

## 🎭 AI Personalities

Choose from 5 different AI personalities in the Settings panel:

1. **🚀 Sales Expert** - Enthusiastic, persuasive, results-focused
2. **🤖 AI Assistant** - Professional, helpful, informative  
3. **🛠️ Technical Support** - Problem-solving, step-by-step guidance
4. **💼 Business Consultant** - Strategic, analytical, advisory
5. **📚 Educator** - Teaching-focused, explanatory

## 📝 Usage

### Adding Documents

**Method 1: Web Interface** (Works locally and on Vercel)
1. Click "Choose File" in the Knowledge Base panel
2. Select your file and click "Upload to Knowledge Base"
3. Supported formats: `.txt`, `.pdf`, `.docx`, `.csv`, `.json`, `.md`

**Method 2: File System** (Local development only)
1. Copy files to the `knowledge_base/` directory
2. Restart the application

### Managing AI Personalities

1. **Select a preset template** from the Settings panel
2. **Edit the system prompt** in the textarea
3. **Click "Test Only"** to try temporarily, or **"Save & Apply"** to make permanent
4. **Create custom prompts** by writing your own system instructions

## ⚙️ Configuration

Customize behavior through environment variables:

```env
# OpenAI Settings
OPENAI_MODEL=gpt-3.5-turbo    # or gpt-4
MAX_TOKENS=500                # Response length
TEMPERATURE=0.7               # Creativity (0-1)

# Knowledge Base Settings
CHUNK_SIZE=500               # Document chunk size
SIMILARITY_THRESHOLD=0.3     # Search sensitivity (lower = more results)
```

## 🚨 Important Notes for Vercel Deployment

### Limitations:
- **📁 File uploads are temporary** - documents don't persist between function calls
- **🔄 Knowledge base resets** on each deployment
- **⏱️ 30-second timeout** for serverless functions
- **💾 No persistent storage** - embeddings cache is temporary

### Recommended Solutions:
- **Use external storage** (AWS S3, Google Drive API) for persistent documents
- **Use a database** (MongoDB, Supabase) for embeddings cache
- **Upload documents via web interface** each session
- **Consider Vercel Pro** for longer function timeouts

## 🛠 Troubleshooting

### Vercel Deployment Issues

**Build fails with "Module not found":**
- Check `requirements.txt` includes all dependencies
- Ensure `api/index.py` exists and is correct

**"Invalid API Key" error:**
- Verify `OPENAI_API_KEY` is set in Vercel environment variables
- Check the key has proper permissions for both GPT and embeddings

**Function timeout:**
- Large documents may cause timeouts
- Try smaller files or upgrade to Vercel Pro

### Local Development Issues

**"Environment variable required" error:**
- Check `.env` file exists with `OPENAI_API_KEY`
- Ensure the API key is valid

**Slow responses:**
- First-time document processing takes time
- Subsequent queries use cached embeddings

## 📋 Development

### Running Locally with Vercel Environment

```bash
# Set Vercel flag to test serverless behavior
export VERCEL=true
python3 run.py
```

### Testing Before Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Test locally
vercel dev
```

## 🔐 Security Best Practices

- ✅ Never commit API keys to GitHub
- ✅ Use environment variables for secrets
- ✅ Set environment variables only in Vercel dashboard
- ✅ Regenerate API keys if compromised
- ✅ Use `.gitignore` to exclude sensitive files

## 📜 License

MIT License - Feel free to modify and use for your needs.

---

## 🆘 Support

If you encounter issues:

1. **Check Vercel deployment logs** in the dashboard
2. **Verify environment variables** are set correctly
3. **Test locally first** before deploying
4. **Check OpenAI API quota** and billing

**Happy chatting! 🎉**