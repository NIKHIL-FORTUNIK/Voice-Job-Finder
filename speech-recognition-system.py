from flask import Flask, render_template, request, jsonify, session, make_response
import requests
import requests_cache
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import joblib
import threading
import os
import re
from flask_cors import CORS
from flask_mail import Mail, Message
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO


app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'timecapsulenation@gmail.com'
app.config['MAIL_PASSWORD'] = 'unzc xafh hpno qsjy'
app.config['MAIL_DEFAULT_SENDER'] = 'timecapsulenation@gmail.com'
 
mail = Mail(app)

# Cache configuration
requests_cache.install_cache('api_cache', backend='sqlite', expire_after=3600)

# Model loading
_MODEL = None
_MODEL_LOCK = threading.Lock()

def get_model():
    global _MODEL
    with _MODEL_LOCK:
        if _MODEL is None:
            _MODEL = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    return _MODEL

def fetch_data():
    """Fetches services from the API and refreshes cache if necessary."""
    try:
        response = requests.get("https://api.menrol.com/api/v1/getServices")
        data = response.json().get("all", []) if response.json().get("success") else []
        
        # Refresh cached data
        subcategories, embeddings = preprocess_data(data)
        joblib.dump(subcategories, 'cached_data.pkl')
        joblib.dump(embeddings, 'embeddings.pkl')
        
        return data
    except Exception as e:
        print(f"API Error: {str(e)}")
        return []
    
def generate_invoice_pdf(cart):
    """Generates a PDF invoice and returns it as a BytesIO object."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    # Register a font that supports the ₹ symbol
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    
    y_position = 750  # Start position on the page
   

    pdf.setFont("DejaVuSans", 16)
    pdf.drawString(72, y_position, "Service Invoice")
    y_position -= 40

    pdf.setFont("DejaVuSans", 12)  # Use DejaVuSans for proper ₹ support
    for idx, item in enumerate(cart):
        pdf.drawString(72, y_position, f"Item {idx+1}: {item['Service Name']}")
        pdf.drawString(72, y_position - 20, f"Category: {item['Service Category']}")
        pdf.drawString(72, y_position - 40, f"Workers: {item['Number of Workers']} | Days: {item['Service Duration (Days)']}")
        pdf.drawString(72, y_position - 60, f"Location: {item['Service Location']}")
        

        y_position -= 100
      

        if y_position < 100:
            pdf.showPage()
            y_position = 750

    pdf.setFont("DejaVuSans", 14)
    
    pdf.save()

    buffer.seek(0)  # Reset buffer position
    return buffer

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    try:
        data = request.json
        index = data.get('index')  # Get index from request

        # Debugging - Print received index
        print("Received index for removal:", index)

        cart = session.get('cart', [])

        # Debugging - Print cart before removal
        print("Cart before removal:", cart)

        # Ensure index is valid
        if index is None or not isinstance(index, int) or index < 0 or index >= len(cart):
            print("Invalid cart index:", index)  # Debugging
            return jsonify({"error": "Invalid cart index"}), 400

        # Remove item
        del cart[index]
        session['cart'] = cart
        session.modified = True

        # Debugging - Print cart after removal
        print("Cart after removal:", cart)

        return jsonify(success=True, cart=cart)
    except Exception as e:
        print("Error removing item from cart:", str(e))
        return jsonify({"error": str(e)}), 500


def preprocess_data(data):
    """Prepares data for similarity matching."""
    subcategories = []
    embeddings = []
    model = get_model()
    
    for category in data:
        for sub in category.get('subcategory', []):
            sub_data = {
                'title': sub.get('title', 'Untitled'),
                'description': sub.get('description', 'No description'),
                'category': category.get('category', 'Uncategorized'),
                'pricing': format_pricing(sub.get('pricing', []))
            }
            subcategories.append(sub_data)
            text = f"{sub_data['category']} {sub_data['title']} {sub_data['description']} {sub_data['pricing']}"
            embeddings.append(model.encode(text))
    
    return subcategories, np.array(embeddings)

def format_pricing(pricing_list):
    """Formats pricing details for display."""
    formatted_prices = [
        f"{pricing['pricingtype'].capitalize()}: ₹{pricing['from']} - ₹{pricing['to']}"
        for pricing in pricing_list if all(key in pricing for key in ['pricingtype', 'from', 'to'])
    ]
    return formatted_prices if formatted_prices else ["Pricing not available"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_invoice', methods=['POST'])
def send_invoice():
    try:
        data = request.json
        email = data.get('email', '').strip()

        if not email:
            return jsonify({"error": "Email is required"}), 400

        cart = session.get('cart', [])
        if not cart:
            return jsonify({"error": "Cart is empty"}), 400

        # Generate PDF invoice
        pdf_buffer = generate_invoice_pdf(cart)
        if pdf_buffer is None:
            return jsonify({"error": "Failed to generate invoice."}), 500

        # Create email message
        msg = Message("Your Service Invoice", recipients=[email])
        msg.body = "Thank you for your order. Please find your invoice attached."
        msg.attach("invoice.pdf", "application/pdf", pdf_buffer.getvalue())

        print(f"📧 Sending email to: {email}...")

        # Send email
        mail.send(msg)

        print(f"✅ Email sent successfully to {email}")

        # Clear cart after successful email
        session.pop('cart', None)

        return jsonify({"message": "Invoice sent successfully!"})
    
    except Exception as e:
        print("🚨 Email sending failed:", str(e))
        return jsonify({"error": f"Failed to send email. Error: {str(e)}"}), 500




@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    
    if data.get('new_session', False):
        session.clear()  # Clear session at new conversation start

    model = get_model()
    query_embed = model.encode(user_input)

    try:
        subcategories = joblib.load('cached_data.pkl')
        embeddings = joblib.load('embeddings.pkl')
    except FileNotFoundError:
        subcategories, embeddings = preprocess_data(fetch_data())

    scores = cosine_similarity([query_embed], embeddings)[0]
    best_matches = sorted(zip(subcategories, scores), key=lambda x: -x[1])[:3]

    if not best_matches or best_matches[0][1] < 0.3:
        return jsonify(response="Sorry, I can't help you with that."), 200
        
    return jsonify({
        "header": "Search Results:",
        "results": [{
            "number": idx + 1,
            "id": idx,
            "category": match['category'],
            "title": match['title'],
            "description": match['description'],
            "pricing": match['pricing']
        } for idx, (match, score) in enumerate(best_matches)],
        "next_step": "service_selection"
    })

@app.route('/select_service', methods=['POST'])
def select_service():
    """Handles service selection using title instead of index."""
    try:
        data = request.json
        selected_title = data.get('selected_title')  # Get title instead of index

        # Load available services
        subcategories = joblib.load('cached_data.pkl')

        # Find service by title
        selected_service = next((s for s in subcategories if s['title'] == selected_title), None)

        # If service not found, return error
        if not selected_service:
            print(f"Service not found: {selected_title}")
            return jsonify({"error": "Invalid service selection"}), 400

        # Debugging - Print selected service details
        print(f"Selected Service: {selected_service['title']} - {selected_service['category']}")

        # Clear old session data
        session.pop('selected_service', None)

        # Store selected service in session
        session['selected_service'] = {
            'title': selected_service['title'],
            'category': selected_service['category'],
            'pricing_details': selected_service['pricing']
        }

        return jsonify({
            "next_step": "pricing_type",
            "message": "Please select a pricing type:",
            "options": selected_service['pricing']
        })
    except Exception as e:
        print("Service selection error:", str(e))
        return jsonify({"error": str(e)}), 400



@app.route('/process_bill', methods=['POST'])
def process_bill():
    """Processes bill and adds the correct service to the cart, restricting different categories."""
    try:
        data = request.json
        selected_service = session.get('selected_service')

        if not selected_service:
            return jsonify({"error": "Session expired. Please start over."}), 400

        pricing_type = data.get('pricing_type')
        pricing_details = selected_service.get('pricing_details', [])

        selected_pricing = next((p for p in pricing_details if pricing_type in p), None)
        if not selected_pricing:
            return jsonify({"error": "Invalid pricing selection"}), 400

        workers = max(int(data.get('workers', 1)), 1)
        days = max(int(data.get('days', 1)), 1)
        location = data.get('location', '').strip()

        if not location:
            return jsonify({"error": "Location is required"}), 400

        # ✅ Store the correct price range in the cart
        bill_data = {
            "Service Name": selected_service['title'],
            "Service Category": selected_service['category'],
            "Pricing Plan": pricing_type,
            "Price Range": selected_pricing,
            "Number of Workers": workers,
            "Service Duration (Days)": days,
            "Service Location": location
        }

        # Ensure cart session exists
        if 'cart' not in session:
            session['cart'] = []

        # ✅ Check if the cart already has items
        if session['cart']:
            first_item_category = session['cart'][0]["Service Category"]
            if bill_data["Service Category"] != first_item_category:
                return jsonify({
                    "error": f"⚠️ You can only add services from the '{first_item_category}' category!"
                }), 400

        # Prevent duplicate entries
        for item in session['cart']:
            if item["Service Name"] == bill_data["Service Name"] and item["Pricing Plan"] == bill_data["Pricing Plan"]:
                return jsonify({"error": "⚠️ Item already in cart!"}), 400

        # ✅ Add new item to cart
        session['cart'].append(bill_data)
        session.modified = True

        print("Updated Cart:", session['cart'])

        return jsonify({"message": "✅ Item added to cart!"})
        
    except Exception as e:
        app.logger.error(f"Bill error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500






@app.route('/cart', methods=['GET'])
def get_cart():
    return jsonify(cart=session.get('cart', []))

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
