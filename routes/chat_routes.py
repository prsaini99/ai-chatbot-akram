import os
import json
import openai
from flask import Blueprint, request, jsonify, render_template
from models.knowledge_base import KnowledgeBase
from config import Config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Create blueprint
chat_bp = Blueprint('chat', __name__)

# Initialize knowledge base (will be set by app.py)
knowledge_base = None

# Global system prompt storage
current_system_prompt = None
current_template = 'salesperson'
prompt_last_updated = datetime.now()

def init_routes(kb_instance):
    """Initialize routes with knowledge base instance"""
    global knowledge_base
    knowledge_base = kb_instance

@chat_bp.route('/')
def index():
    """Serve the chat interface"""
    return render_template('index.html')

@chat_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

@chat_bp.route('/kb-stats')
def kb_stats():
    """Get knowledge base statistics"""
    if not knowledge_base:
        return jsonify({'error': 'Knowledge base not initialized'}), 500
    
    # Group metadata by filename to get document details
    document_info = {}
    for metadata in knowledge_base.metadata:
        filename = metadata['filename']
        if filename not in document_info:
            document_info[filename] = {
                'filename': filename,
                'type': metadata['type'],
                'chunks': 0
            }
        document_info[filename]['chunks'] += 1
    
    # Convert to list and sort by filename
    documents_list = sorted(document_info.values(), key=lambda x: x['filename'])
    
    return jsonify({
        'document_count': len(document_info),
        'chunk_count': len(knowledge_base.documents),
        'status': 'Ready' if knowledge_base.documents else 'Empty',
        'documents': documents_list
    })

@chat_bp.route('/upload', methods=['POST'])
def upload_document():
    """Upload a document to the knowledge base"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Save file to knowledge base directory
        file_path = os.path.join(Config.KNOWLEDGE_BASE_DIR, file.filename)
        file.save(file_path)
        
        # Reload knowledge base
        knowledge_base.load_knowledge_base()
        
        return jsonify({'success': True, 'message': 'Document uploaded successfully'})
    
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint with RAG support"""
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_id = data.get('conversation_id', 'default')
        mode = data.get('mode', 'hybrid')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Search knowledge base for relevant context
        context = ""
        sources = []
        
        # Always search knowledge base since we only support kb_only mode
        if knowledge_base and knowledge_base.documents:
            logger.info(f"Searching knowledge base with query: {user_message}")
            logger.info(f"Knowledge base has {len(knowledge_base.documents)} documents")
            search_results = knowledge_base.search(user_message, top_k=3)
            logger.info(f"Search results found: {len(search_results)} matches")
            
            if search_results:
                context_parts = []
                for doc, metadata, similarity in search_results:
                    logger.info(f"Using document: {metadata['filename']} with similarity: {similarity:.3f}")
                    context_parts.append(f"[Source: {metadata['filename']}]\n{doc}")
                    sources.append(metadata)
                
                context = "\n\n".join(context_parts)
                logger.info(f"Context length: {len(context)} characters")
            else:
                logger.warning("No relevant documents found in knowledge base")
        
        # Prepare messages for OpenAI
        messages = []
        
        # Use dynamic system prompt (always kb_only mode)
        system_prompt = get_system_prompt('kb_only', context)
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        messages.append({"role": "user", "content": user_message})
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model=Config.OPENAI_MODEL,
            messages=messages,
            max_tokens=Config.MAX_TOKENS,
            temperature=Config.TEMPERATURE,
            top_p=Config.TOP_P,
            frequency_penalty=Config.FREQUENCY_PENALTY,
            presence_penalty=Config.PRESENCE_PENALTY
        )
        
        bot_response = response.choices[0].message.content
        
        return jsonify({
            'response': bot_response,
            'conversation_id': conversation_id,
            'sources': sources if sources else None
        })
        
    except openai.error.RateLimitError:
        return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
    except openai.error.AuthenticationError:
        return jsonify({'error': 'Invalid API key. Please check your configuration.'}), 401
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'An error occurred processing your request.'}), 500

# System Prompt Templates (Knowledge Base Only Mode)
PROMPT_TEMPLATES = {
    'salesperson': """You are an enthusiastic and knowledgeable sales expert who absolutely loves helping customers. Your personality is warm, engaging, and persuasive - like the best salesperson who genuinely cares about finding the perfect solution for each customer.

PERSONALITY TRAITS:
- Speak conversationally and naturally, like you're chatting with a friend
- Be genuinely excited about the products and services you're discussing
- Use persuasive language that highlights benefits and value
- Address concerns proactively and turn them into selling points
- Always look for opportunities to upsell or cross-sell naturally
- Create urgency when appropriate (limited offers, high demand, etc.)
- Use social proof and success stories when relevant
- Be confident and assertive, but never pushy

COMMUNICATION STYLE:
- Start responses with engaging phrases like "Great question!" or "I'm so glad you asked!"
- Use power words: amazing, incredible, exclusive, proven, guaranteed, revolutionary
- Paint vivid pictures of how the product/service will improve their life
- Ask engaging questions to understand their needs better
- End with compelling calls-to-action

IMPORTANT: You can ONLY use information from the provided context. If something isn't in the context, say "Let me connect you with our specialist for those details" or "I'd love to get you more information on that!"

Context from our product catalog:
{context}

Remember: You're not just answering questions - you're creating an irresistible desire for what we offer!""",
    
    'assistant': """You are a professional AI assistant that provides information based strictly on the provided knowledge base.

GUIDELINES:
- Only use information from the provided context
- If information isn't available in the context, clearly state this
- Always cite the source document when providing information
- Maintain a professional and helpful tone
- Structure responses clearly and logically

Context from knowledge base:
{context}

If the answer cannot be found in the above context, please inform the user that the information is not available in the current knowledge base.""",
    
    'support': """You are a technical support specialist who provides assistance based on the available documentation and troubleshooting guides.

GUIDELINES:
- Focus on practical, actionable solutions
- Use only information from the provided context
- If specific troubleshooting steps aren't documented, indicate this clearly
- Maintain a helpful and patient tone
- Structure solutions in clear, numbered steps

Technical documentation and support information:
{context}

If the solution isn't covered in the available documentation, please indicate that additional technical resources may be needed.""",
    
    'consultant': """You are a business consultant providing strategic advice based on the available business intelligence and documentation.

METHODOLOGY:
- Analyze available data and documentation thoroughly
- Provide strategic insights based on documented information
- Only make recommendations supported by the provided context
- Indicate when additional analysis or data would be beneficial
- Focus on actionable business strategies

Business intelligence and strategic information:
{context}

Base your consulting recommendations strictly on the information provided above. If additional data is needed for proper analysis, please indicate this.""",
    
    'educator': """You are an educator providing instruction based on the available educational materials and curriculum.

TEACHING GUIDELINES:
- Base all instruction on the provided educational content
- Structure lessons logically and progressively
- Use examples and explanations from the available materials
- If information isn't covered in the materials, indicate this clearly
- Focus on helping students understand and apply the concepts

Educational content and curriculum:
{context}

Provide instruction based strictly on the educational materials provided above."""
}

@chat_bp.route('/get-template-prompt', methods=['POST'])
def get_template_prompt():
    """Get the system prompt for a specific template"""
    try:
        data = request.json
        template_id = data.get('template', 'salesperson')
        
        if template_id in PROMPT_TEMPLATES:
            prompt = PROMPT_TEMPLATES[template_id]
            return jsonify({
                'success': True,
                'prompt': prompt.replace('{context}', '[Context will be inserted here]')
            })
        else:
            return jsonify({'success': False, 'error': 'Template not found'}), 404
            
    except Exception as e:
        logger.error(f"Error getting template prompt: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/save-system-prompt', methods=['POST'])
def save_system_prompt():
    """Save and apply a custom system prompt"""
    try:
        global current_system_prompt, current_template, prompt_last_updated
        
        data = request.json
        custom_prompt = data.get('prompt', '').strip()
        template_id = data.get('template', 'custom')
        save_permanently = data.get('save', False)
        
        if not custom_prompt:
            return jsonify({'success': False, 'error': 'System prompt cannot be empty'}), 400
        
        # Apply the custom prompt
        current_system_prompt = custom_prompt
        current_template = template_id
        prompt_last_updated = datetime.now()
        
        # Save to file if requested
        if save_permanently:
            try:
                prompt_data = {
                    'prompt': custom_prompt,
                    'template': template_id,
                    'last_updated': prompt_last_updated.isoformat()
                }
                
                os.makedirs('settings', exist_ok=True)
                with open('settings/system_prompt.json', 'w') as f:
                    json.dump(prompt_data, f, indent=2)
                    
            except Exception as e:
                logger.warning(f"Failed to save prompt to file: {e}")
        
        return jsonify({
            'success': True,
            'message': 'System prompt applied successfully',
            'template': template_id,
            'last_updated': prompt_last_updated.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error saving system prompt: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/get-current-prompt')
def get_current_prompt():
    """Get information about the currently active system prompt"""
    try:
        return jsonify({
            'success': True,
            'template': current_template,
            'has_custom_prompt': current_system_prompt is not None,
            'last_updated': prompt_last_updated.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting current prompt info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/reset-system-prompt', methods=['POST'])
def reset_system_prompt():
    """Reset to default system prompt"""
    try:
        global current_system_prompt, current_template, prompt_last_updated
        
        current_system_prompt = None
        current_template = 'salesperson'
        prompt_last_updated = datetime.now()
        
        # Remove saved file if it exists
        try:
            if os.path.exists('settings/system_prompt.json'):
                os.remove('settings/system_prompt.json')
        except Exception as e:
            logger.warning(f"Failed to remove saved prompt file: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Reset to default system prompt',
            'template': current_template,
            'last_updated': prompt_last_updated.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error resetting system prompt: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def get_system_prompt(mode, context=""):
    """Get the appropriate system prompt based on template and context"""
    global current_system_prompt, current_template
    
    # If there's a custom system prompt, use it
    if current_system_prompt:
        return current_system_prompt.replace('{context}', context)
    
    # Otherwise use template-based prompts (always kb_only mode)
    template_prompt = PROMPT_TEMPLATES.get(current_template, PROMPT_TEMPLATES['salesperson'])
    return template_prompt.replace('{context}', context)