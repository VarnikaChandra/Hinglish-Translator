import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI  # Import the new OpenAI client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder="../frontend/build", static_url_path="")
CORS(app)  # Optional: Enable CORS if you need it

# Initialize OpenAI client with your API key
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Serve React frontend
@app.route('/')
def serve_react_app():
    """Serve the React app."""
    return send_from_directory(app.static_folder, 'index.html')
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/translate', methods=['POST'])
def translate_to_hinglish():
    data = request.get_json()
    english_text = data.get('text', '')

    if not english_text:
        return jsonify({"error": "No text provided"}), 400

    try:
        # Start a streaming request
        stream = client.chat.completions.create(
            model="gpt-4o",  # Use the correct model
            messages=[
                {"role": "system", "content": "Translate the following to Hinglish."},
                {"role": "user", "content": english_text}
            ],
            stream=True,
        )

        # Prepare to collect the response chunks
        hinglish_translation = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                hinglish_translation += chunk.choices[0].delta.content  # Append each chunk
        
        return jsonify({"hinglish": hinglish_translation.strip()})  # Return the complete translation
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Redirect 404 errors to React app
@app.errorhandler(404)
def not_found(e):
    """Redirect 404 errors to React app."""
    return send_from_directory(app.static_folder, 'index.html')

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)  # Update the port if needed
