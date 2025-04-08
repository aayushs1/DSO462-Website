from flask import Flask, render_template, request, jsonify, session
import os
from datetime import datetime, timedelta
import uuid
import random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gogoprint_secret_key_dev')

# Mock database using dictionaries
mock_db = {
    'chats': [],
    'messages': []
}

# Random interesting chat ideas for 3D printing
chat_ideas = [
    "Modern geometric lamp shade with customizable patterns",
    "Ergonomic pen holder with phone stand feature",
    "Modular desk organizer system with interlocking parts",
    "Custom watch stand with integrated charging cable management",
    "Adjustable laptop stand with cooling ventilation",
    "Floating wall shelf with hidden mounting brackets",
    "Minimalist phone amplifier stand (no electronics)",
    "Customizable planter with drainage system",
    "Mini trebuchet desktop toy with adjustable counterweight",
    "Articulated desk lamp with cable management",
    "Headphone stand with cable organizer",
    "Customizable name plate for desk",
    "Wall mounted controller holder with game storage",
    "Mechanical keyboard wrist rest with ergonomic curve",
    "Self-watering planter with water level indicator",
    "Desktop cable management system",
    "Acoustic phone amplifier (no electronics)",
    "Honeycomb wall organizer with modular attachments",
    "Bathroom toothbrush and toothpaste holder",
    "Gaming dice tower with intricate design"
]

# Realistic responses for 3D modeling requests
bot_responses = [
    "I've created a 3D model based on your specifications. The design emphasizes {feature} while maintaining a clean, modern aesthetic.",
    "Your 3D model is ready! I've included the {feature} you requested and optimized it for printing with minimal supports.",
    "Here's the 3D model you requested. I've designed it with {feature} and made sure it's stable when placed on a flat surface.",
    "I've generated a 3D model that matches your description. The {feature} should work exactly as you described, and I've added some subtle details to enhance the overall look.",
    "Your 3D model is complete! I've incorporated {feature} and made sure all dimensions are proportional. The design should print well on most FDM printers.",
    "Here's the customized 3D model with the {feature} you specified. I've optimized the geometry to minimize material usage while maintaining structural integrity.",
    "I've designed your 3D model with careful attention to the {feature}. The result is both functional and aesthetically pleasing.",
    "Your 3D model is ready for printing! I've focused on making the {feature} both practical and visually appealing."
]

# Features that might be highlighted in a 3D print
features = [
    "ergonomic grip", "honeycomb pattern", "snap-fit assembly", "rounded edges",
    "minimalist design", "geometric patterns", "modular connections", "hidden compartments",
    "customizable elements", "organic curves", "structural reinforcement", "ventilation slots",
    "interlocking mechanism", "adjustable components", "cable management", "drawer slides",
    "textured surface", "low-poly aesthetic", "functional hinges", "water drainage system"
]


# Initialize with sample data
def create_sample_chat_history():
    user_id = 'sample_user'
    chats = []
    messages = []

    # Create random timestamps within the last 30 days
    now = datetime.now()

    for i in range(10):
        # Random time in the past 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)

        chat_time = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

        # Create chat
        chat_id = str(uuid.uuid4())
        chat_title = random.choice(chat_ideas)

        chat = {
            'id': chat_id,
            '_id': chat_id,  # Add this line to mimic MongoDB ObjectId
            'title': chat_title,
            'user_id': user_id,
            'created_at': chat_time,
            'last_updated': chat_time
        }
        chats.append(chat)

        # Create conversation messages for this chat
        user_message = {
            'id': str(uuid.uuid4()),
            'chat_id': chat_id,
            'sender': 'user',
            'content': f"Can you create a {chat_title.lower()} for me? I need it to be functional and have a clean design.",
            'timestamp': chat_time
        }
        messages.append(user_message)

        # Bot response a minute later
        feature = random.choice(features)
        bot_response_template = random.choice(bot_responses)
        bot_response = bot_response_template.format(feature=feature)

        bot_message = {
            'id': str(uuid.uuid4()),
            'chat_id': chat_id,
            'sender': 'bot',
            'content': bot_response,
            'model_preview': True,
            'model_name': f"{chat_title.lower().replace(' ', '_')}.stl",
            'model_size': f"{random.randint(1, 5)}.{random.randint(1, 9)} MB",
            'timestamp': chat_time + timedelta(minutes=1)
        }
        messages.append(bot_message)

        # Sometimes add a follow-up question
        if random.random() > 0.6:  # 40% chance
            followup_time = chat_time + timedelta(minutes=random.randint(5, 30))
            followup_question = random.choice([
                "Can you make it a bit smaller?",
                "Could you add more details to the surface?",
                "Is it possible to make the walls thicker for better durability?",
                "Can you modify it to have a smoother finish?",
                "Would it be possible to add my initials to the design?",
                "Can you change the proportions to make it wider?",
                "I'd like it to have a more minimalist look. Can you simplify it?",
                "Could you make the edges more rounded?"
            ])

            user_followup = {
                'id': str(uuid.uuid4()),
                'chat_id': chat_id,
                'sender': 'user',
                'content': followup_question,
                'timestamp': followup_time
            }
            messages.append(user_followup)

            # Bot response to follow-up
            bot_followup_time = followup_time + timedelta(minutes=1)
            bot_followup = {
                'id': str(uuid.uuid4()),
                'chat_id': chat_id,
                'sender': 'bot',
                'content': f"Of course! I've updated the design. {random.choice([
                    'The modifications have been applied while maintaining the overall structure.',
                    'The adjustments have been made exactly as requested.',
                    'I\'ve implemented your changes and re - optimized the model.',
                                                                                'The design now incorporates your feedback while preserving functionality.'
                ])}",
                'model_preview': True,
                'model_name': f"{chat_title.lower().replace(' ', '_')}_v2.stl",
                'model_size': f"{random.randint(1, 5)}.{random.randint(1, 9)} MB",
                'timestamp': bot_followup_time
            }
            messages.append(bot_followup)

            # Update the last_updated time for the chat
            chat['last_updated'] = bot_followup_time

    # Sort chats by last_updated (most recent first)
    chats.sort(key=lambda x: x['last_updated'], reverse=True)

    return chats, messages


# Create and store sample data
sample_chats, sample_messages = create_sample_chat_history()
mock_db['chats'] = sample_chats
mock_db['messages'] = sample_messages


@app.route('/')
def index():
    # Generate a user ID if not in session
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session['user_name'] = "Guest User"
        session['user_email'] = "guest@example.com"

    # Get recent chats for user (or use sample data for demo)
    # No need to make copies or add _id, since we already added it in create_sample_chat_history
    recent_chats = mock_db['chats'][:5]  # Only show 5 most recent

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
            chat = c  # No need for a copy since we already have _id
            break

    if not chat:
        return "Chat not found", 404

    # Get messages for this chat
    messages = [msg for msg in mock_db['messages'] if msg.get('chat_id') == chat_id]

    # Sort messages by timestamp
    messages.sort(key=lambda x: x.get('timestamp'))

    # Get recent chats for sidebar
    recent_chats = mock_db['chats'][:5]  # Only show 5 most recent

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
        '_id': chat_id,  # Add this for template consistency
        'title': 'New Chat',
        'user_id': user_id,
        'created_at': datetime.now(),
        'last_updated': datetime.now()
    }

    mock_db['chats'].insert(0, new_chat)  # Add to the beginning of the list

    return jsonify({'chat_id': chat_id})


@app.route('/message/send', methods=['POST'])
def send_message():
    data = request.json
    chat_id = data.get('chat_id')
    message_text = data.get('message')

    if not chat_id or not message_text:
        return jsonify({'error': 'Missing required fields'}), 400

    # Insert user message
    current_time = datetime.now()
    user_message_id = str(uuid.uuid4())
    user_message = {
        'id': user_message_id,
        'chat_id': chat_id,
        'sender': 'user',
        'content': message_text,
        'timestamp': current_time
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
            chat['last_updated'] = current_time
            break

    # Create bot response
    feature = random.choice(features)
    bot_response_template = random.choice(bot_responses)
    bot_response_text = bot_response_template.format(feature=feature)

    bot_message_id = str(uuid.uuid4())
    bot_response = {
        'id': bot_message_id,
        'chat_id': chat_id,
        'sender': 'bot',
        'content': bot_response_text,
        'model_preview': True,
        'model_name': f"generated_model_{chat_id[:6]}.stl",
        'model_size': f"{random.randint(1, 5)}.{random.randint(1, 9)} MB",
        'timestamp': current_time + timedelta(seconds=2)
    }

    # Insert bot response
    mock_db['messages'].append(bot_response)

    # Update the timestamp for the chat
    for chat in mock_db['chats']:
        if chat['id'] == chat_id:
            chat['last_updated'] = current_time + timedelta(seconds=2)

            # Move this chat to the top of the list (most recent)
            mock_db['chats'].remove(chat)
            mock_db['chats'].insert(0, chat)
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
    Route to regenerate the sample data
    """
    global mock_db
    sample_chats, sample_messages = create_sample_chat_history()
    mock_db['chats'] = sample_chats
    mock_db['messages'] = sample_messages

    return jsonify({'status': 'Sample data regenerated successfully', 'chat_count': len(sample_chats)})


if __name__ == '__main__':
    app.run(debug=True, port=5001)