import asyncio
import os
from dotenv import load_dotenv
import csv
import io
from flask import Flask, render_template, request, jsonify, make_response
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

import agent
from models import db, Drug, SideEffectReport
from agent import local_tools, get_mcp_tools

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///drugs.db'

db.init_app(app)
agent.flask_app = app

with app.app_context():
    db.create_all()

mcp_tools = asyncio.run(get_mcp_tools())
all_tools = local_tools + mcp_tools

llm = ChatOpenAI(
    model="google/gemini-2.0-flash-001",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Side Effects Tracker"
    }
)

agent = create_agent(llm, all_tools, system_prompt='''You are a medical intelligence assistant specializing in drug side effects.
When using Slack always send messages to the channel #all-sideeffect.

CRITICAL INSTRUCTIONS:
1. For every drug analyzed, research a concise (1-2 sentence) medical description summary.
2. If a drug is new, use create_drug with the description.
3. If a drug exists but lacks a description (or has a poor one), use update_drug_description.
4. Categorize every side effect into exactly one of: Gastrointestinal, Neurological, Cardiovascular, Respiratory, Musculoskeletal, Immunological, Metabolic, General.
5. Assign every side effect a Severity Score from 1.0 to 10.0 (1=Mild, 10=Critical/Fatal).
6. DEMOGRAPHIC RESEARCH: You must specifically search for risk variations by Age and Gender. 
7. DRUG INTELLIGENCE: You must research and provide:
   - A concise 'SenseMed Pro Tip' (actionable advice for patients).
   - A 'Usage & Dosage Snapshot' (standard doses and administration method).
8. CRITICAL: If an existing side effect is missing a severity score or demographic risk multipliers, or if a drug is missing intelligence fields, you MUST update the record using the update tools.

PROCEDURE:
1. List all drugs in the database.
2. For each drug, check if it has a description and current side effects.
3. Research new side effects AND a medical description from the internet.
4. Update/Create drug metadata and side effect reports in the DB.
5. Send a slack message with the summary of updates.''')

def get_drugs_json():
    drugs = Drug.query.all()
    return [{
        'id': d.id,
        'name': d.drug_name,
        'description': d.description or "",
        'pro_tip': d.pro_tip or "Search initiated for clinical insights...",
        'dosage_snapshot': d.dosage_snapshot or "Guidelines pending AI review...",
        'side_effects': [{
            'name': s.side_effect_name,
            'category': s.side_effect_category or "General",
            'probability': round(s.side_effect_probability * 100, 1),
            'severity': s.side_effect_severity or 5.0,
            'demographics': s.side_effect_demographics or '{"Pediatric": 1.0, "Adult": 1.0, "Senior": 1.0, "Male": 1.0, "Female": 1.0}',
        } for s in d.side_effect_reports]
    } for d in drugs]

@app.route('/')
def home():
    drugs_data = get_drugs_json()
    return render_template('index.html', drugs_data=drugs_data)

@app.route('/api/drugs')
def get_drugs():
    return jsonify(get_drugs_json())

@app.route('/api/drugs/<int:id>', methods=['DELETE'])
def delete_drug(id):
    drug = Drug.query.get_or_404(id)
    db.session.delete(drug)
    db.session.commit()
    return jsonify({'status': 'deleted', 'drugs': get_drugs_json()})

@app.route('/api/drugs/<int:id>/csv')
def download_drug_csv(id):
    drug = Drug.query.get_or_404(id)
    
    # Create an in-memory string buffer for the CSV
    si = io.StringIO()
    cw = csv.writer(si)
    
    # Write Header
    cw.writerow(['Medicine Name', 'Description', 'Side Effect', 'Category', 'Probability (%)'])
    
    # Write Data
    if not drug.side_effect_reports:
        # If no side effects, just write the drug name and description
        cw.writerow([drug.drug_name, drug.description or "No description available", "N/A", "N/A", "N/A"])
    else:
        for idx, s in enumerate(drug.side_effect_reports):
            # Only repeat the drug name/description on the first row for a cleaner look, or repeat every row
            cw.writerow([
                drug.drug_name,
                drug.description or "",
                s.side_effect_name,
                s.side_effect_category or "General",
                f"{round(s.side_effect_probability * 100, 1)}%"
            ])
            
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename={drug.drug_name.replace(' ', '_')}_Report.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/query', methods=['POST'])
def query():
    try:
        user_query = request.json.get('query')
        result = asyncio.run(agent.ainvoke({'messages': user_query}))
        response = result['messages'][-1].content
        return jsonify({
            'response': response,
            'drugs': get_drugs_json()
        })
    except Exception as e:
        print(f"Error in query: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'response': "I encountered an error while processing your request. Please try again or check the server logs.",
            'drugs': get_drugs_json()
        }), 500


if __name__ == '__main__':
    app.run(debug=True)
