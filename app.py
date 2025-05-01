from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from datetime import datetime
import time
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

databaseLink = os.getenv("MONGO_URI")
app.config["MONGO_URI"] = f"{databaseLink}/noticeboard"

# Initialize PyMongo
try:
    mongo = PyMongo(app)
    mongo.cx.server_info()
    print("✅ MongoDB connected successfully")
except Exception as e:
    print("❌ MongoDB connection failed:", str(e))

def initialize_db():
    try:
        notices_collection = mongo.db.notices
        if not notices_collection.find_one({"_id": "notices_doc"}):
            notices_collection.insert_one(
                {
                    "_id": "notices_doc", 
                    "notices": []
                }
            
            )
            print("📦 Initialized notices_doc in DB")
    except Exception as e:
        print("❌ Failed to initialize DB:", str(e))

# PUT request to add a notice with date
@app.route('/notice', methods=['PUT'])
def add_notice():
    data = request.get_json()
    notice_title = data.get("title")
    notice = data.get("notice")
    labels = data.get("label", "general")  # still using `label` key for backward compatibility

    # Normalize labels to a list
    if isinstance(labels, str):
        labels = [label.strip() for label in labels.split(",") if label.strip()]
    elif not isinstance(labels, list):
        labels = ["general"]

    if not notice_title or not notice:
        return jsonify({"error": "Title & Notice required"}), 400

    formatted_date = datetime.now().strftime("%d-%m-%Y")
    notice_entry = {
        "title": notice_title,
        "notice": notice,
        "labels": labels,
        "dateAdded": formatted_date,
        "moment": int(time.time() * 10000)
    }

    mongo.db.notices.update_one(
        {"_id": "notices_doc"},
        {"$push": {"notices": notice_entry}},
        upsert=True
    )
    return jsonify({"message": "Notice added successfully"}), 200

# GET request to fetch all notices as array of [text, dateAdded], sorted by date (newest first)
@app.route('/notices', methods=['GET'])
def get_notices():
    doc = mongo.db.notices.find_one({"_id": "notices_doc"})
    if not doc or "notices" not in doc:
        return jsonify([]), 200

    sorted_notices = sorted(
        doc["notices"],
        key=lambda x: x.get("moment", 0),
        reverse=True
    )

    notice_list = [
        {
            "title": notice.get("title", ""),
            "notice": notice.get("notice", ""),
            "dateAdded": notice.get("dateAdded", ""),
            "labels": notice.get("labels", ["general"])
        }
        for notice in sorted_notices
    ]

    return jsonify(notice_list), 200

@app.route('/notices', methods=['DELETE'])
def delete_notices():
    data = request.get_json()
    titles = data.get("titles", [])
    
    if not titles:
        return jsonify({"error": "No notice titles provided"}), 400
    
    # Get the current notices document
    doc = mongo.db.notices.find_one({"_id": "notices_doc"})
    if not doc or "notices" not in doc:
        return jsonify({"error": "No notices found"}), 404
    
    # Filter out the notices with matching titles
    current_notices = doc["notices"]
    updated_notices = [notice for notice in current_notices 
                      if notice.get("title") not in titles]
    
    # Update the database with the filtered notices
    mongo.db.notices.update_one(
        {"_id": "notices_doc"},
        {"$set": {"notices": updated_notices}}
    )
    
    return jsonify({
        "message": f"Successfully deleted {len(current_notices) - len(updated_notices)} notice(s)",
        "deleted_count": len(current_notices) - len(updated_notices)
    }), 200

# Run the app
if __name__ == '__main__':
    with app.app_context():
        initialize_db()
