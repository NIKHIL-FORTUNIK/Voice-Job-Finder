# VOICE-JOB-FINDER
# AI-Powered Speech Recognition System

## Overview
This project is an AI-powered speech recognition system that enables users to search for services using voice commands. The system supports both Hindi and English and leverages Natural Language Processing (NLP) to accurately interpret queries. It features a responsive web interface, an optimized backend, and efficient data handling for seamless service retrieval.

## Features
### 🔹 Speech Recognition
- Supports **Hindi** and **English**.
- Uses **Web Speech API** for real-time voice input processing.

### 🔹 Natural Language Processing (NLP)
- Employs **BERT-based Sentence Transformers** for accurate job title and category matching.
- Handles both **voice and text-based queries** efficiently.

### 🔹 Service Search
- Retrieves relevant job details such as:
  - **Title** of the service.
  - **Category** (e.g., Plumber, Electrician, Carpenter, etc.).
  - **Pricing** information.
  - **Service description**.
- Allows category-based searches, displaying all related job titles.

### 🔹 Invoice Generation
- Generates professional **PDF invoices** for service bookings.
- Uses **ReportLab** to create invoices dynamically.
- Sends invoices to users via **email**.

### 🔹 Cart Management
- Users can **add, view, and remove** services from the cart.
- Restricts users to selecting services from only one category at a time.

### 🔹 Modern UI
- **Interactive chatbot-like interface** for ease of use.
- Supports both **voice and text-based** search.
- Provides a **dark/light mode** toggle.

### 🔹 Security Measures
- Implements **Flask-CORS** to prevent unauthorized cross-origin requests.
- Uses **session-based authentication** for cart management.
- Secure email communication with **TLS encryption**.

### 🔹 Performance Optimization
- Caches API responses using **Requests-Cache** for faster service retrieval.
- Utilizes **Joblib** for model persistence and quick loading.
- Lightweight UI with optimized JavaScript to enhance user experience.

## HTML File Components
The **frontend** of this project is built using `index.html`, which contains various components:

### 🔹 Chat Interface
- **Chat container**: Displays messages between the user and the AI assistant.
- **Chat input box**: Allows text-based input and displays results.
- **Voice recognition button**: Enables real-time speech input.

### 🔹 Service Selection UI
- Users can select services from dynamically generated options.
- Each service includes a **title, description, category, and pricing details**.
- Uses **radio buttons** for selecting a pricing plan.

### 🔹 Cart System
- **Cart modal**: Shows selected services with details such as pricing and service duration.
- **Remove item button**: Allows users to delete items from the cart.
- **Checkout button**: Proceeds with the final invoice generation.

### 🔹 Invoice Download Section
- Provides users with a button to **download invoices**.
- The invoice is automatically generated as a **PDF** and emailed to the user.

## Working of the System
1. **User Interaction**:
   - The user opens the web application and is greeted with a chatbot-like interface.
   - They can either use **voice input** via the microphone button 🎤 or **text input**.

2. **Speech Recognition & NLP Processing**:
   - If using voice, the **Web Speech API** converts speech into text.
   - The **BERT-based NLP model** processes the input and identifies the relevant job category and title.

3. **Service Retrieval**:
   - The system queries an external **API (https://api.************)** to fetch available services.
   - If a **category is mentioned** (e.g., "Plumber"), all services under that category are displayed.
   - If a **specific job title** is mentioned (e.g., "Drain Specialist"), it directly retrieves that service’s details.

4. **User Selection & Cart Management**:
   - The user selects a service and **chooses a pricing plan**.
   - Additional details like **number of workers, duration, and location** are entered.
   - The service is **added to the cart**, ensuring category restrictions are maintained.

5. **Invoice Generation & Checkout**:
   - Users can review their cart and proceed to checkout.
   - The system generates a **PDF invoice** using **ReportLab** and emails it to the user via **Flask-Mail**.
   - The cart is cleared upon successful order completion.

6. **Session Management & Security**:
   - The system maintains a session to track user selections.
   - **CORS policies and TLS encryption** ensure data security.

## Technologies Used
### 📌 Backend:
- **Flask** (Web framework)
- **Flask-CORS** (Cross-Origin Resource Sharing)
- **Flask-Mail** (Email support)
- **Sentence Transformers** (NLP Model for text similarity)
- **Requests-Cache** (Optimized API request caching)
- **Joblib** (Model and data persistence)
- **ReportLab** (PDF generation for invoices)

### 📌 Frontend:
- **HTML, CSS, JavaScript**
- **Font Awesome Icons** (UI enhancements)
- **Google Fonts** (Better typography)

### 📌 NLP Model:
- **Paraphrase-Multilingual-MiniLM-L12-v2** (for multilingual query understanding)

### 📌 Speech Recognition:
- **Web Speech API** (JavaScript-based speech-to-text conversion)

### 📌 Database:
- **In-memory session storage** (Caching service data for faster retrieval)

## Installation Guide
### Prerequisites
Ensure you have **Python 3** and **Flask** installed before proceeding.

### 🚀 Steps to Set Up
1. **Clone the Repository**:
   ```sh
   git clone https://github.com/NIKHIL-FORTUNIK/speech-recognition-system.git
   cd speech-recognition-system
   ```
2. **Install Dependencies**:
   ```sh
   pip install flask requests numpy joblib flask-cors flask-mail sentence-transformers requests-cache reportlab
   ```
3. **Run the Flask Server**:
   ```sh
   python speech-recognition-system.py
   ```
4. **Open the Web App**:
   - Visit **`http://127.0.0.1:5000`** in your web browser.

## Usage Guide
1. Click the **microphone button** 🎤 and speak your query.
2. The system will **process your request** and display relevant services.
3. Select a service and choose a **pricing plan**.
4. Enter job details like **workers, duration, and location**.
5. **Add the service to your cart** and proceed to checkout.
6. Receive your **invoice via email** 📧.

## Contributing
Contributions are welcome! If you’d like to improve this project, feel free to submit a pull request.

### Steps to Contribute:
1. **Fork the repository**.
2. Create a **new branch**.
3. Make your changes and **commit**.
4. Push to your branch and **open a pull request**.

## License
This project is **open-source** under the **MIT License**.

## Contact Information
👤 **Developer:** Nikhil (GitHub: [NIKHIL-FORTUNIK](https://github.com/NIKHIL-FORTUNIK))
📧 **Email:** fortunikfreelancer1@gmail.com

If you have any queries, feel free to **reach out!** 🚀

