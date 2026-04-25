import os

from langchain.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient

from models import db, Drug, SideEffectReport

GATEWAY_URL='https://api.arcade.dev/mcp/gw_3CUNEVuhDV08GWAjdZMley5KDB2'

flask_app = None

@tool
def list_drugs() -> list[str]:
    """List all drugs in the database"""
    with flask_app.app_context():
        drugs = [drug.drug_name for drug in Drug.query.all()]
        return str(drugs)


@tool
def create_drug(drug_name: str, description: str = None, pro_tip: str = None, dosage_snapshot: str = None) -> str:
    """Create a new drug in the database. 
    IMPORTANT: Always use list_drugs first to check if the drug already exists before creating.
    Provide a concise (1-2 sentence) medical description, a SenseMed Pro Tip, and a Dosage Snapshot."""
    with flask_app.app_context():
        existing = Drug.query.filter_by(drug_name=drug_name).first()
        if existing:
            return f"Drug '{drug_name}' already exists with ID {existing.id}"
        drug = Drug(
            drug_name=drug_name, 
            description=description,
            pro_tip=pro_tip,
            dosage_snapshot=dosage_snapshot
        )
        db.session.add(drug)
        db.session.commit()
        return f"Drug '{drug_name}' created with ID {drug.id}"


@tool
def update_drug_description(drug_name: str, description: str) -> str:
    """Update the medical description for an existing drug.
    Use this if you find a better or missing description for a drug already in the database."""
    with flask_app.app_context():
        drug = Drug.query.filter_by(drug_name=drug_name).first()
        if not drug:
            return f"Drug '{drug_name}' not found"
        
        drug.description = description
        db.session.commit()
        return f"Description updated for '{drug_name}'"


@tool
def update_drug_intelligence(drug_name: str, pro_tip: str = None, dosage_snapshot: str = None, description: str = None) -> str:
    """Update advanced drug intelligence fields.
    pro_tip: A short, actionable 'SenseMed Pro Tip' (e.g. 'Take with largest meal of the day').
    dosage_snapshot: Concise dosage and administration info (e.g. '500mg-2000mg daily, Oral').
    description: Optional updated medical overview."""
    with flask_app.app_context():
        drug = Drug.query.filter_by(drug_name=drug_name).first()
        if not drug:
            return f"Drug '{drug_name}' not found"
        
        if pro_tip: drug.pro_tip = pro_tip
        if dosage_snapshot: drug.dosage_snapshot = dosage_snapshot
        if description: drug.description = description
        
        db.session.commit()
        return f"Intelligence updated for '{drug_name}'"

@tool
def create_side_effect(drug_name: str, side_effect_name: str, probability: float, severity: float, category: str = "General", demographics: str = None) -> str:
    """Create a new side effect report. 
    Probability: 0.0 to 1.0
    Severity: 1.0 to 10.0
    Demographics: JSON string of risk multipliers e.g. '{"Pediatric": 0.5, "Adult": 1.0, "Senior": 1.8, "Male": 1.0, "Female": 1.2}'
    Categories: Gastrointestinal, Neurological, Cardiovascular, Respiratory, Musculoskeletal, Immunological, Metabolic, General.
    IMPORTANT: Always use list_side_effects first."""
    with flask_app.app_context():
        drug = Drug.query.filter_by(drug_name=drug_name).first()
        if not drug:
            return f"Drug '{drug_name}' not found"
        
        existing = SideEffectReport.query.filter_by(drug_id=drug.id, side_effect_name=side_effect_name).first()
        if existing:
            return f"Side effect '{side_effect_name}' already exists for '{drug_name}'"
        
        report = SideEffectReport(
            side_effect_name=side_effect_name,
            side_effect_category=category,
            side_effect_probability=probability,
            side_effect_severity=severity,
            side_effect_demographics=demographics,
            drug_id=drug.id
        )

        db.session.add(report)
        db.session.commit()
        return f"Side effect '{side_effect_name}' added to '{drug_name}' (Prob: {probability}, Sev: {severity})"


@tool
def update_side_effect_severity(drug_name: str, side_effect_name: str, severity: float) -> str:
    """Update the severity score (1.0 - 10.0) for an existing side effect."""
    with flask_app.app_context():
        drug = Drug.query.filter_by(drug_name=drug_name).first()
        if not drug:
            return f"Drug '{drug_name}' not found"
        
        report = SideEffectReport.query.filter_by(drug_id=drug.id, side_effect_name=side_effect_name).first()
        if not report:
            return f"Side effect '{side_effect_name}' not found for '{drug_name}'"
        
        report.side_effect_severity = severity
        db.session.commit()
        return f"Severity updated for '{side_effect_name}' to {severity}"


@tool
def update_side_effect_demographics(drug_name: str, side_effect_name: str, demographics: str) -> str:
    """Update demographic risk multipliers (JSON string) for a side effect.
    Example: '{"Pediatric": 0.8, "Adult": 1.0, "Senior": 1.5}'"""
    with flask_app.app_context():
        drug = Drug.query.filter_by(drug_name=drug_name).first()
        if not drug:
            return f"Drug '{drug_name}' not found"
        
        report = SideEffectReport.query.filter_by(drug_id=drug.id, side_effect_name=side_effect_name).first()
        if not report:
            return f"Side effect '{side_effect_name}' not found for '{drug_name}'"
        
        report.side_effect_demographics = demographics
        db.session.commit()
        return f"Demographics updated for '{side_effect_name}'"


@tool
def list_side_effects(drug_name: str) -> list[dict]:
    """List all side effects for a specific drug"""
    with flask_app.app_context():
        drug = Drug.query.filter_by(drug_name=drug_name).first()
        if not drug:
            return f"Drug '{drug_name}' not found"
        
        results = [
            {
                "name": report.side_effect_name,
                "category": report.side_effect_category or "General",
                "probability": report.side_effect_probability,
                "severity": report.side_effect_severity or 5.0,
                "demographics": report.side_effect_demographics or '{"Pediatric": 1.0, "Adult": 1.0, "Senior": 1.0, "Male": 1.0, "Female": 1.0}',
            }
            for report in drug.side_effect_reports
        ]
        return str(results)


async def get_mcp_tools():
    client = MultiServerMCPClient(
        {
            'arcade': {
                'transport': 'http',
                'url': GATEWAY_URL,
                'headers': {
                    'Authorization': f'Bearer {os.getenv("ARCADE_API_KEY")}',
                    'Arcade-User-ID': os.getenv('ARCADE_USER_ID')
                }
            }
        }
    )

    return await client.get_tools()


local_tools = [list_drugs, list_side_effects, create_drug, create_side_effect, update_drug_description, update_drug_intelligence, update_side_effect_severity, update_side_effect_demographics]