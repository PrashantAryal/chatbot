
from datetime import datetime
from flask import Flask, request, render_template
from utils.validation import validate_email,validate_phone,extract_date
from ai_model import qa_chain

app = Flask(__name__)

# Storing chat history and user information
chat_history = []
user_info = {}
chat_state = 'idle' 


@app.route('/', methods=['GET', 'POST'])
def handle_query():
    global chat_history, user_info, chat_state
    if request.method == 'POST':
        query = request.form['query'].strip().lower()

        # Handle greetings
        greetings = {"hi", "hello", "good morning", "good evening"}
        if query in greetings:
            response = "Hi, How can I assist you?"
            chat_history.append({'query': query, 'response': response, 'sources': []})
            return render_template('index.html', chat_history=chat_history)

        # to schedule appointmet, triggering
        if "appointment" in query or "call"  in query or "meeting" in query:
            chat_state = 'collecting_date'
            response = "When would you like to schedule your appointment?"

        #collecting the user's details for appointment
        elif chat_state == 'collecting_date':
            date = extract_date(query)
            if date:
                user_info['date'] = date
                chat_state = 'collecting_name'  
                response = f"Can I have your name, please?"
        
        elif chat_state == 'collecting_name':
            user_info['name'] = query
            chat_state = 'collecting_phone' 
            response = "What's your phone number?"

        elif chat_state == 'collecting_phone':
            if not validate_phone(query):
                response = "Invalid phone number format. Please enter a valid phone number."
            else:
                user_info['phone'] = query
                chat_state = 'collecting_email'  
                response = "Could you provide your email address?"
        
        elif chat_state == 'collecting_email':
            if not validate_email(query):
                response = "Invalid email address. Please provide a valid email."
            else:
                user_info['email'] = query
                chat_state = 'idle'
                # response = f"Thank you {user_info['name']}, Your appointment is Confirmed.<br>--------------------------------------<br>Details:<br>Name: {user_info['name']}<br>Phone: {user_info['phone']}<br>Email: {user_info['email']}<br>Date: {user_info['date']}"
                response = f"""
                <div style='margin: 10px 0;'>
                    <p style='font-weight: bold; margin-bottom: 8px;'>✅ Appointment Confirmed</p>
                    <div style='background: #f5f5f5; padding: 10px; border-radius: 5px;'>
                        <p style='margin: 5px 0;'><b>Name:</b> {user_info['name']}</p>
                        <p style='margin: 5px 0;'><b>Phone:</b> {user_info['phone']}</p>
                        <p style='margin: 5px 0;'><b>Email:</b> {user_info['email']}</p>
                        <p style='margin: 5px 0;'><b>Date:</b> {user_info['date']}</p>
                    </div>
                    <p style='margin-top: 8px;'>Thank you!</p>
                </div>
                """
        else:
            # Process the query using the QA chain
            result  = qa_chain({"query": query})
            response = result['result']

        chat_history.append({'query': query, 'response': response, 'sources': []})
        
        return render_template('index.html', chat_history=chat_history)

    return render_template('index.html', chat_history=chat_history)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
