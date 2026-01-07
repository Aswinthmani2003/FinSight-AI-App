from flask import Flask, render_template, request, jsonify, make_response
import os
import csv
import json
from groq import Groq
import uuid
import time
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'txt'}

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def parse_csv(filepath):
    """Parse CSV file and extract transactions"""
    transactions = []
    with open(filepath, 'r', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            transactions.append(dict(row))
    return transactions

def analyze_transactions_with_ai(transactions):
    """Use Groq AI to analyze and categorize transactions"""
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Prepare transaction data for analysis
    transaction_text = json.dumps(transactions[:50], indent=2)  # Limit to first 50 for demo
    
    prompt = f"""Analyze these bank transactions and provide:
1. Categorize each transaction into categories like: Food & Dining, Transportation, Shopping, Bills & Utilities, Entertainment, Healthcare, Income, Other
2. Calculate total spending by category
3. Identify spending patterns
4. Suggest a reasonable monthly budget based on the data
5. Provide 3-5 actionable financial insights

Transactions:
{transaction_text}

Return your analysis as JSON with this structure:
{{
    "categorized_transactions": [
        {{"description": "...", "amount": ..., "category": "...", "date": "..."}}
    ],
    "category_totals": {{"Food & Dining": ..., "Transportation": ...}},
    "insights": ["insight 1", "insight 2", ...],
    "suggested_budget": {{"Food & Dining": ..., "Transportation": ...}},
    "total_spending": ...
}}

Return ONLY the JSON, no other text."""
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.3-70b-versatile",  # Fast and accurate model
        temperature=0.5,
        max_tokens=4000,
    )
    
    response_text = chat_completion.choices[0].message.content
    
    # Try to extract JSON from the response
    try:
        # Look for JSON in code blocks or raw
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        else:
            json_str = response_text
        
        analysis = json.loads(json_str)
        return analysis
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Response text: {response_text}")
        return {
            "error": "Failed to parse AI response",
            "raw_response": response_text
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        import uuid, time

        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        file.save(filepath)

        try:
            transactions = parse_csv(filepath)
            analysis = analyze_transactions_with_ai(transactions)
            time.sleep(0.1)
            os.remove(filepath)
            return jsonify(analysis)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/analyze-manual', methods=['POST'])
def analyze_manual():
    """Analyze manually entered transactions"""
    data = request.get_json()
    transactions = data.get('transactions', [])
    
    if not transactions:
        return jsonify({'error': 'No transactions provided'}), 400
    
    try:
        analysis = analyze_transactions_with_ai(transactions)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export-pdf', methods=['POST'])
def export_pdf():
    data = request.get_json()
    analysis = data.get('analysis', {})

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    # ===== Title =====
    story.append(Paragraph(
        "<b>FinSight AI – Financial Analysis Report</b>",
        styles["Title"]
    ))
    story.append(Spacer(1, 20))

    # ===== Summary =====
    story.append(Paragraph("<b>Summary</b>", styles["Heading2"]))
    story.append(Spacer(1, 10))

    total_spending = abs(analysis.get("total_spending", 0))
    story.append(Paragraph(
        f"Total Monthly Spending: <b>${total_spending:.2f}</b>",
        styles["Normal"]
    ))
    story.append(Spacer(1, 15))

    # ===== Category Breakdown =====
    story.append(Paragraph("<b>Category Breakdown</b>", styles["Heading2"]))
    story.append(Spacer(1, 10))

    table_data = [["Category", "Amount ($)"]]

    for cat, amt in analysis.get("category_totals", {}).items():
        if cat != "Income":
            table_data.append([cat, f"{abs(amt):.2f}"])

    table = Table(table_data, colWidths=[250, 150])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    # ===== AI Insights =====
    story.append(Paragraph("<b>AI Insights</b>", styles["Heading2"]))
    story.append(Spacer(1, 10))

    for insight in analysis.get("insights", []):
        story.append(Paragraph(f"• {insight}", styles["Normal"]))
        story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)

    return make_response(
        buffer.read(),
        200,
        {
            "Content-Type": "application/pdf",
            "Content-Disposition": "attachment; filename=FinSight_Report.pdf"
        }
    )

@app.route('/chat', methods=['POST'])
def chat():
    print("✅ /chat endpoint hit")
    data = request.get_json()

    user_message = data.get('message', '').strip()
    analysis = data.get('analysis', {})

    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        context = json.dumps(analysis, indent=2)

        prompt = f"""
You are a personal financial assistant.

Here is the user's financial analysis data:
{context}

Answer the user's question clearly and concisely.
If numbers are available, use them exactly.

User question:
{user_message}
"""

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=500,
        )

        reply = chat_completion.choices[0].message.content.strip()

        return jsonify({"reply": reply})

    except Exception as e:
        print("Chat error:", e)
        return jsonify({"error": "Chat failed"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
