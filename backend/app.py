from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from flask_session import Session
import os
import uuid  # To generate unique session IDs
from datetime import timedelta

# Import your model class
from model import myModel
from database import init_database, get_health_records, get_individual_records

app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:3000"}})



# Configure Flask-Session
app.config["SESSION_TYPE"] = "filesystem"  # Stores sessions in files (can be changed to Redis/DB)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecretkey")  # Change in production!
Session(app)

init_database()

# Dictionary to store chatbots per user session
chatbots = {}


def get_user_chatbot(session_id):
    """Retrieve or create a chatbot for the current session."""
    if session_id is None:
        raise KeyError
    if session_id not in chatbots:
        print(session_id, " chatbot created")
        chatbots[session_id] = myModel()  # Assign a chatbot instance
    return chatbots[session_id]

@app.route("/api/start-session", methods=["POST"])
def start_session():
    """Initialize a new chatbot session for the user."""
    try:
        data = request.get_json()
        username = data.get("username", "Guest")

        session_id = str(uuid.uuid4())  # Generate unique session ID
        session["session_id"] = session_id

        chatbots[session_id] = myModel()  # Create a chatbot for this session

        return jsonify({"sessionId": session_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/end-session", methods=["POST"])
def end_session():
    """Remove chatbot session when the user leaves."""
    try:
        data = request.get_json()
        session_id = data.get("sessionId")

        if session_id in chatbots:
            chatbots[session_id].end_service()
            del chatbots[session_id]

        return jsonify({"message": "Session ended"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for users to ask questions to their assigned chatbot."""
    try:
        data = request.get_json()
        question = data.get("question", "").strip()
        session_id = data.get("sessionId")

        if not question:
            return jsonify({"error": "Question cannot be empty"}), 400
        chatbot = get_user_chatbot(session_id)
        response = chatbot.chat(question)

        return jsonify({"question": question, "response": response})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/end-chat', methods=['POST'])
def end_chat():
    """API endpoint for users to ask questions to their assigned chatbot."""
    try:
        data = request.get_json()
        session_id = data.get("sessionId")
        name = data.get("name")
        if session_id not in chatbots or name is None:
            return jsonify({"error": "Invalid sessionId or name"}), 404
        chatbot = get_user_chatbot(session_id)
        assessment = chatbot.store_data(name)

        chatbots[session_id].end_service()
        del chatbots[session_id]
        return jsonify(assessment)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/data', methods=['GET'])
def get_all_health_data():
    """API endpoint to retrieve all health assessment data from the database."""
    try:
        records = get_health_records()
        return jsonify({"data": records}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health-analysis/<int:health_id>', methods=['GET'])
def get_health_analysis_by_id(health_id):
    """API endpoint to retrieve health analysis data for a specific health_id."""
    try:
        health_data = get_individual_records(health_id)

        if health_data:
            return jsonify({"health_analysis": health_data}), 200
        else:
            return jsonify({"error": f"No health analysis found for ID {health_id}"}), 404

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

FRONTEND_BUILD_PATH = os.path.abspath(os.path.join(os.getcwd(), "../frontend/build"))
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_static_files(path):
    """Serve React static files or fallback to index.html for React Router."""
    file_path = os.path.join(FRONTEND_BUILD_PATH, path)
    print(file_path)

    # If the requested file exists, serve it
    if os.path.exists(file_path):
        return send_from_directory(FRONTEND_BUILD_PATH, "index.html")

    # Otherwise, serve React's index.html (to handle client-side routing)
    return send_from_directory(FRONTEND_BUILD_PATH, "index.html")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
