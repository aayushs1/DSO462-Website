from flask import Flask, render_template, request, jsonify, session
import os
from datetime import datetime
import uuid
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gogoprint_secret_key_dev')

# Mock database using dictionaries
mock_db = {
    'chats': [],
    'messages': []
}

# Pre-populate with some sample data
sample_chats = [
    {
        'id': '1',
        'title': 'Custom desk organizer with pen holders',
        'user_id': 'sample_user',
        'created_at': datetime.now(),
        'last_updated': datetime.now()
    },
    {
        'id': '2',
        'title': 'Minimalist smartphone stand design',
        'user_id': 'sample_user',
        'created_at': datetime.now(),
        'last_updated': datetime.now()
    },
    {
        'id': '3',
        'title': 'Geometric planter for succulents',
        'user_id': 'sample_user',
        'created_at': datetime.now(),
        'last_updated': datetime.now()
    },
    {
        'id': '4',
        'title': 'Custom doorknob with fingerprint pattern',
        'user_id': 'sample_user',
        'created_at': datetime.now(),
        'last_updated': datetime.now()
    },
    {
        'id': '5',
        'title': 'Tablet holder for kitchen with utensil hooks',
        'user_id': 'sample_user',
        'created_at': datetime.now(),
        'last_updated': datetime.now()
    }
]

for chat in sample_chats:
    mock_db['chats'].append(chat)


@app.route('/')
def index():
    # Generate a user ID if not in session
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session['user_name'] = "Guest User"
        session['user_email'] = "guest@example.com"

    # Get recent chats for user (or use sample data for demo)
    recent_chats = []
    for chat in mock_db['chats']:
        chat_copy = chat.copy()
        # Convert ObjectId to string for template
        chat_copy['_id'] = chat['id']
        recent_chats.append(chat_copy)

    return render_template('index.html',
                           recent_chats=recent_chats,
                           user_name=session.get('user_name'),
                           user_email=session.get('user_email'))


@app.route('/chat/<chat_id>')
def view_chat(chat_id):
    # Find the chat in mock DB
    chat = None
    for c in mock_db['chats']:
        if c['id'] == chat_id:
            chat = c.copy()
            chat['_id'] = chat['id']
            break

    if not chat:
        return "Chat not found", 404

    # Get messages for this chat
    messages = [msg for msg in mock_db['messages'] if msg.get('chat_id') == chat_id]

    # Get recent chats for sidebar
    recent_chats = []
    for c in mock_db['chats']:
        chat_copy = c.copy()
        chat_copy['_id'] = c['id']
        recent_chats.append(chat_copy)

    return render_template('chat.html',
                           chat=chat,
                           messages=messages,
                           recent_chats=recent_chats,
                           user_name=session.get('user_name'),
                           user_email=session.get('user_email'))


@app.route('/chat/new', methods=['POST'])
def new_chat():
    user_id = session.get('user_id')

    # Create a new chat ID
    chat_id = str(uuid.uuid4())

    # Create new chat
    new_chat = {
        'id': chat_id,
        'title': 'New Chat',
        'user_id': user_id,
        'created_at': datetime.now(),
        'last_updated': datetime.now()
    }

    mock_db['chats'].append(new_chat)

    return jsonify({'chat_id': chat_id})


@app.route('/message/send', methods=['POST'])
def send_message():
    data = request.json
    chat_id = data.get('chat_id')
    message_text = data.get('message')

    if not chat_id or not message_text:
        return jsonify({'error': 'Missing required fields'}), 400

    # Insert user message
    user_message_id = str(uuid.uuid4())
    user_message = {
        'id': user_message_id,
        'chat_id': chat_id,
        'sender': 'user',
        'content': message_text,
        'timestamp': datetime.now()
    }
    mock_db['messages'].append(user_message)

    # Update chat title if it's the first message
    for chat in mock_db['chats']:
        if chat['id'] == chat_id and chat['title'] == 'New Chat':
            # Use the first few words of the message as the chat title
            title = ' '.join(message_text.split()[:5])
            if len(title) > 30:
                title = title[:27] + '...'
            chat['title'] = title
            chat['last_updated'] = datetime.now()
            break

    # Create bot response
    bot_message_id = str(uuid.uuid4())
    bot_response = {
        'id': bot_message_id,
        'chat_id': chat_id,
        'sender': 'bot',
        'content': f"I've created a 3D model based on your request: \"{message_text}\"",
        'model_preview': True,
        'model_name': 'generated_model.stl',
        'model_size': '2.7 MB',
        'timestamp': datetime.now()
    }

    # Insert bot response
    mock_db['messages'].append(bot_response)

    # Update the timestamp for the chat
    for chat in mock_db['chats']:
        if chat['id'] == chat_id:
            chat['last_updated'] = datetime.now()
            break

    # Convert datetime objects to strings for JSON response
    bot_response_json = bot_response.copy()
    bot_response_json['timestamp'] = bot_response_json['timestamp'].strftime('%Y-%m-%d %H:%M:%S')

    return jsonify({
        'user_message_id': user_message_id,
        'bot_message_id': bot_message_id,
        'bot_response': bot_response_json
    })


@app.route('/populate-sample-data')
def populate_sample_data():
    """
    Route to populate the mock database with sample data for demonstration purposes.
    """
    user_id = session.get('user_id', 'demo_user')

    # Sample chat history
    sample_chats = [
        {
            'id': str(uuid.uuid4()),
            'title': 'Custom desk organizer with pen holders',
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_updated': datetime.now()
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Minimalist smartphone stand design',
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_updated': datetime.now()
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Geometric planter for succulents',
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_updated': datetime.now()
        }
    ]

    # Clear current chats and add new ones
    mock_db['chats'] = sample_chats

    return jsonify({'status': 'Sample data added successfully'})


if __name__ == '__main__':
    app.run(debug=True, port=5001)