from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from app import db, limiter
from app.models.chat_log import ChatLog
from app.chatbot.engine import chatbot_engine
import time
import uuid

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/')
@login_required
def chat_interface():
    """Main chat interface"""
    return render_template('chat/interface.html', user=current_user)

@chat_bp.route('/send', methods=['POST'])
@login_required
@limiter.limit("30 per minute")
def send_message():
    """Handle chat message from user with intelligent chatbot"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Generate session ID if not exists
        if 'chat_session_id' not in session:
            session['chat_session_id'] = str(uuid.uuid4())
        
        # Process message with chatbot engine
        result = chatbot_engine.process_message(
            user_message=user_message,
            user_id=current_user.id,
            session_id=session['chat_session_id']
        )
        
        if result['success']:
            return jsonify({
                'response': result['response'],
                'intent': result['intent'],
                'confidence': result['confidence'],
                'response_time': result['response_time_ms'],
                'timestamp': time.time()
            })
        else:
            return jsonify({
                'error': result['response']
            }), 400
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'error': 'Something went wrong. Please try again.'}), 500

@chat_bp.route('/history')
@login_required
def chat_history():
    """Get user's chat history"""
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        chats = ChatLog.query.filter_by(user_id=current_user.id)\
                           .order_by(ChatLog.created_at.desc())\
                           .limit(limit)\
                           .offset(offset)\
                           .all()
        
        return jsonify({
            'chats': [chat.to_dict() for chat in chats],
            'total': current_user.chat_logs.count()
        })
        
    except Exception as e:
        print(f"Chat history error: {e}")
        return jsonify({'error': 'Failed to load chat history'}), 500

@chat_bp.route('/stats')
@login_required
def chat_stats():
    """Get user's conversation statistics"""
    try:
        stats = chatbot_engine.get_conversation_stats(current_user.id)
        return jsonify(stats)
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({'error': 'Failed to load statistics'}), 500

@chat_bp.route('/reload-intents', methods=['POST'])
@login_required
def reload_intents():
    """Reload chatbot intents (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        success = chatbot_engine.reload_intents()
        if success:
            return jsonify({'message': 'Intents reloaded successfully'})
        else:
            return jsonify({'error': 'Failed to reload intents'}), 500
    except Exception as e:
        print(f"Reload intents error: {e}")
        return jsonify({'error': 'Failed to reload intents'}), 500
