"""
AI Loan Eligibility Checker - Flask Backend
Advanced BFSI Financial Decision Assistant
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import json
import requests
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static',
    static_url_path='/static'
)

# Enable CORS for API requests
CORS(app)

# ============================================================
# CONFIGURATION
# ============================================================

CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GOOGLE_SHEETS_ENDPOINT = os.getenv('GOOGLE_SHEETS_ENDPOINT')
AI_PROVIDER = os.getenv('AI_PROVIDER', 'claude').lower()

# ============================================================
# ELIGIBILITY RULES ENGINE
# ============================================================

class EligibilityEngine:
    """Deterministic loan eligibility rule engine"""
    
    # Business Rules Constants
    MIN_SALARY = 30000
    MIN_CREDIT_SCORE = 700
    MAX_EXISTING_EMI = 20000
    MIN_AGE = 21
    LOAN_MULTIPLIER = 20
    
    @staticmethod
    def validate_inputs(data):
        """Validate input data"""
        errors = {}
        
        # Name validation
        if not data.get('name') or len(str(data.get('name', '')).strip()) < 2:
            errors['name'] = 'Name is required (minimum 2 characters)'
        
        # Salary validation
        try:
            salary = float(data.get('salary', 0))
            if salary <= 0:
                errors['salary'] = 'Salary must be greater than 0'
        except (ValueError, TypeError):
            errors['salary'] = 'Invalid salary format'
        
        # Credit score validation
        try:
            score = float(data.get('credit_score', 0))
            if score < 300 or score > 900:
                errors['credit_score'] = 'Credit score must be between 300 and 900'
        except (ValueError, TypeError):
            errors['credit_score'] = 'Invalid credit score format'
        
        # Existing EMI validation
        try:
            emi = float(data.get('existing_emi', 0))
            if emi < 0:
                errors['existing_emi'] = 'Existing EMI cannot be negative'
        except (ValueError, TypeError):
            errors['existing_emi'] = 'Invalid EMI format'
        
        # Age validation
        try:
            age = int(data.get('age', 0))
            if age <= 0 or age > 120:
                errors['age'] = 'Age must be a valid positive number'
        except (ValueError, TypeError):
            errors['age'] = 'Invalid age format'
        
        return errors
    
    @staticmethod
    def check_eligibility(name, salary, credit_score, existing_emi, age):
        """
        Check loan eligibility based on business rules
        Returns: (is_eligible, conditions_passed, conditions_failed)
        """
        conditions_passed = []
        conditions_failed = []
        
        # Rule 1: Salary > 30,000
        if salary > EligibilityEngine.MIN_SALARY:
            conditions_passed.append({
                'rule': 'Monthly Salary',
                'requirement': f'> ₹{EligibilityEngine.MIN_SALARY:,.0f}',
                'value': f'₹{salary:,.0f}',
                'status': 'PASSED'
            })
        else:
            conditions_failed.append({
                'rule': 'Monthly Salary',
                'requirement': f'> ₹{EligibilityEngine.MIN_SALARY:,.0f}',
                'value': f'₹{salary:,.0f}',
                'status': 'FAILED',
                'advice': 'Increase your monthly income to qualify for a loan'
            })
        
        # Rule 2: Credit Score > 700
        if credit_score > EligibilityEngine.MIN_CREDIT_SCORE:
            conditions_passed.append({
                'rule': 'Credit Score',
                'requirement': f'> {EligibilityEngine.MIN_CREDIT_SCORE}',
                'value': f'{credit_score}',
                'status': 'PASSED'
            })
        else:
            conditions_failed.append({
                'rule': 'Credit Score',
                'requirement': f'> {EligibilityEngine.MIN_CREDIT_SCORE}',
                'value': f'{credit_score}',
                'status': 'FAILED',
                'advice': 'Work on improving your credit score through timely repayments'
            })
        
        # Rule 3: Existing EMI < 20,000
        if existing_emi < EligibilityEngine.MAX_EXISTING_EMI:
            conditions_passed.append({
                'rule': 'Existing EMI',
                'requirement': f'< ₹{EligibilityEngine.MAX_EXISTING_EMI:,.0f}',
                'value': f'₹{existing_emi:,.0f}',
                'status': 'PASSED'
            })
        else:
            conditions_failed.append({
                'rule': 'Existing EMI',
                'requirement': f'< ₹{EligibilityEngine.MAX_EXISTING_EMI:,.0f}',
                'value': f'₹{existing_emi:,.0f}',
                'status': 'FAILED',
                'advice': 'Reduce your existing EMI obligations'
            })
        
        # Rule 4: Age >= 21
        if age >= EligibilityEngine.MIN_AGE:
            conditions_passed.append({
                'rule': 'Age',
                'requirement': f'>= {EligibilityEngine.MIN_AGE} years',
                'value': f'{age} years',
                'status': 'PASSED'
            })
        else:
            conditions_failed.append({
                'rule': 'Age',
                'requirement': f'>= {EligibilityEngine.MIN_AGE} years',
                'value': f'{age} years',
                'status': 'FAILED',
                'advice': 'You must be at least 21 years old to apply for a loan'
            })
        
        # Final Eligibility Decision
        is_eligible = len(conditions_failed) == 0
        
        return is_eligible, conditions_passed, conditions_failed
    
    @staticmethod
    def calculate_eligible_loan_amount(salary):
        """Calculate eligible loan amount: Salary × 20"""
        return salary * EligibilityEngine.LOAN_MULTIPLIER
    
    @staticmethod
    def classify_risk(salary, credit_score, existing_emi, age, is_eligible):
        """Classify risk level based on financial parameters"""
        if not is_eligible:
            return 'HIGH RISK', 'Does not meet eligibility criteria'
        
        risk_score = 0
        
        # Credit score impact
        if credit_score >= 750:
            risk_score += 0
        elif credit_score >= 700:
            risk_score += 1
        else:
            risk_score += 3
        
        # EMI-to-salary ratio
        emi_ratio = existing_emi / salary if salary > 0 else 1
        if emi_ratio < 0.2:
            risk_score += 0
        elif emi_ratio < 0.4:
            risk_score += 1
        else:
            risk_score += 2
        
        # Age factor
        if age >= 25 and age <= 55:
            risk_score += 0
        else:
            risk_score += 1
        
        # Salary level
        if salary >= 100000:
            risk_score += 0
        elif salary >= 50000:
            risk_score += 1
        else:
            risk_score += 2
        
        # Determine risk classification
        if risk_score <= 1:
            return 'LOW RISK', 'Strong financial profile with good repayment capacity'
        elif risk_score <= 3:
            return 'MODERATE RISK', 'Acceptable financial profile with reasonable repayment capacity'
        else:
            return 'HIGH RISK', 'Higher risk profile requiring careful consideration'

# ============================================================
# AI PROVIDER INTEGRATION
# ============================================================

class AIProvider:
    """Abstract AI provider for financial analysis"""
    
    @staticmethod
    def get_provider():
        """Get configured AI provider"""
        if AI_PROVIDER == 'groq' and GROQ_API_KEY:
            return GroqProvider()
        elif AI_PROVIDER == 'claude' and CLAUDE_API_KEY:
            return ClaudeProvider()
        else:
            return LocalProvider()
    
    def analyze(self, data, eligibility_result):
        """Analyze financial data and provide recommendations"""
        raise NotImplementedError


class ClaudeProvider(AIProvider):
    """Claude AI integration via Anthropic API"""
    
    def analyze(self, data, eligibility_result):
        """Get financial analysis from Claude"""
        try:
            prompt = self._build_prompt(data, eligibility_result)
            
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': CLAUDE_API_KEY,
                'anthropic-version': '2023-06-01'
            }
            
            payload = {
                'model': 'claude-3-5-sonnet-20241022',
                'max_tokens': 500,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            }
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['content'][0]['text']
            else:
                logger.error(f'Claude API error: {response.status_code}')
                return LocalProvider().analyze(data, eligibility_result)
                
        except Exception as e:
            logger.error(f'Claude API exception: {str(e)}')
            return LocalProvider().analyze(data, eligibility_result)
    
    def _build_prompt(self, data, eligibility_result):
        """Build Claude prompt for financial analysis"""
        return f"""You are an expert financial advisor. Analyze this loan application and provide brief, actionable guidance.

Applicant: {data['name']}
Monthly Salary: ₹{data['salary']:,.0f}
Credit Score: {data['credit_score']}
Existing EMI: ₹{data['existing_emi']:,.0f}
Age: {data['age']}

Eligibility: {"ELIGIBLE" if eligibility_result['eligible'] else "NOT ELIGIBLE"}
Risk Level: {eligibility_result['risk_classification']}

Provide:
1. Brief financial profile summary (2 sentences)
2. If eligible: Key strengths and how to maximize loan benefits
3. If not eligible: Specific steps to improve eligibility
4. One personalized financial tip

Keep response concise and professional."""


class GroqProvider(AIProvider):
    """Groq API integration for fast inference"""
    
    def analyze(self, data, eligibility_result):
        """Get financial analysis from Groq"""
        try:
            prompt = self._build_prompt(data, eligibility_result)
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {GROQ_API_KEY}'
            }
            
            payload = {
                'model': 'mixtral-8x7b-32768',
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.7,
                'max_tokens': 500
            }
            
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f'Groq API error: {response.status_code}')
                return LocalProvider().analyze(data, eligibility_result)
                
        except Exception as e:
            logger.error(f'Groq API exception: {str(e)}')
            return LocalProvider().analyze(data, eligibility_result)
    
    def _build_prompt(self, data, eligibility_result):
        """Build Groq prompt for financial analysis"""
        return f"""You are an expert financial advisor. Analyze this loan application and provide brief, actionable guidance.

Applicant: {data['name']}
Monthly Salary: ₹{data['salary']:,.0f}
Credit Score: {data['credit_score']}
Existing EMI: ₹{data['existing_emi']:,.0f}
Age: {data['age']}

Eligibility: {"ELIGIBLE" if eligibility_result['eligible'] else "NOT ELIGIBLE"}
Risk Level: {eligibility_result['risk_classification']}

Provide:
1. Brief financial profile summary (2 sentences)
2. If eligible: Key strengths and how to maximize loan benefits
3. If not eligible: Specific steps to improve eligibility
4. One personalized financial tip

Keep response concise and professional."""


class LocalProvider(AIProvider):
    """Local rule-based financial guidance (no API required)"""
    
    def analyze(self, data, eligibility_result):
        """Generate local financial guidance"""
        guidance = []
        
        # Profile summary
        if eligibility_result['eligible']:
            guidance.append(f"Strong financial profile with excellent repayment capacity. Based on your ₹{data['salary']:,.0f} monthly salary, you qualify for a loan of up to ₹{eligibility_result['eligible_loan_amount']:,.0f}.")
        else:
            guidance.append("Your current financial profile does not meet our eligibility criteria. However, with the right improvements, you can qualify for a loan soon.")
        
        # Specific recommendations
        if data['credit_score'] < 700:
            guidance.append("Focus on improving your credit score to 700+ by making timely payments and reducing outstanding debts.")
        
        if data['existing_emi'] >= 15000:
            guidance.append("Consider paying down existing EMI obligations to improve your debt-to-income ratio.")
        
        if data['salary'] < 50000:
            guidance.append("Increase your monthly income or stabilize it for at least 6 months to strengthen your application.")
        
        if eligibility_result['eligible']:
            guidance.append("With your low-risk profile, you can explore loans with competitive interest rates. Consider a tenure of 3-5 years for optimal EMI management.")
        
        guidance.append("\n⚠️ AI provider is not configured. Showing rule-based financial guidance.")
        
        return " ".join(guidance)

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    """Serve main application"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ai_provider': AI_PROVIDER,
        'claude_configured': bool(CLAUDE_API_KEY),
        'groq_configured': bool(GROQ_API_KEY),
        'google_sheets_configured': bool(GOOGLE_SHEETS_ENDPOINT)
    })


@app.route('/api/eligibility', methods=['POST'])
def check_eligibility():
    """Check loan eligibility based on financial inputs"""
    try:
        data = request.get_json()
        
        # Validate inputs
        validation_errors = EligibilityEngine.validate_inputs(data)
        if validation_errors:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'errors': validation_errors
            }), 400
        
        # Extract data
        name = str(data.get('name', '')).strip()
        salary = float(data.get('salary', 0))
        credit_score = float(data.get('credit_score', 0))
        existing_emi = float(data.get('existing_emi', 0))
        age = int(data.get('age', 0))
        
        # Check eligibility
        is_eligible, passed, failed = EligibilityEngine.check_eligibility(
            name, salary, credit_score, existing_emi, age
        )
        
        # Calculate eligible loan amount (only if eligible)
        eligible_loan_amount = 0
        if is_eligible:
            eligible_loan_amount = EligibilityEngine.calculate_eligible_loan_amount(salary)
        
        # Classify risk
        risk_level, risk_description = EligibilityEngine.classify_risk(
            salary, credit_score, existing_emi, age, is_eligible
        )
        
        # Get AI analysis
        eligibility_result = {
            'eligible': is_eligible,
            'eligible_loan_amount': eligible_loan_amount,
            'risk_classification': risk_level
        }
        
        ai_provider = AIProvider.get_provider()
        ai_recommendation = ai_provider.analyze(data, eligibility_result)
        
        # Prepare response
        result = {
            'success': True,
            'applicant_name': name,
            'eligible': is_eligible,
            'eligible_loan_amount': eligible_loan_amount,
            'risk_classification': risk_level,
            'risk_description': risk_description,
            'conditions_passed': passed,
            'conditions_failed': failed,
            'ai_recommendation': ai_recommendation,
            'timestamp': datetime.now().isoformat()
        }
        
        # Try to save to Google Sheets
        if GOOGLE_SHEETS_ENDPOINT:
            try:
                sheets_data = {
                    'timestamp': datetime.now().isoformat(),
                    'name': name,
                    'salary': salary,
                    'credit_score': credit_score,
                    'existing_emi': existing_emi,
                    'age': age,
                    'eligible': is_eligible,
                    'risk_classification': risk_level,
                    'eligible_loan_amount': eligible_loan_amount,
                    'ai_recommendation': ai_recommendation
                }
                requests.post(GOOGLE_SHEETS_ENDPOINT, json=sheets_data, timeout=5)
            except Exception as e:
                logger.warning(f'Google Sheets save failed: {str(e)}')
                # Don't fail the response, just log the warning
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f'Eligibility check error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Server error during eligibility check'
        }), 500


@app.route('/api/emi/calculate', methods=['POST'])
def calculate_emi():
    """Calculate EMI using standard formula"""
    try:
        data = request.get_json()
        
        try:
            principal = float(data.get('principal', 0))
            annual_rate = float(data.get('annual_rate', 0))
            tenure_months = int(data.get('tenure_months', 1))
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Invalid input parameters'
            }), 400
        
        if principal <= 0 or tenure_months <= 0:
            return jsonify({
                'success': False,
                'error': 'Principal and tenure must be positive'
            }), 400
        
        if annual_rate < 0 or annual_rate > 100:
            return jsonify({
                'success': False,
                'error': 'Interest rate must be between 0 and 100'
            }), 400
        
        # EMI Calculation
        if annual_rate == 0:
            # Zero interest case
            emi = principal / tenure_months
            total_interest = 0
        else:
            # Standard EMI formula: EMI = (P × R × (1 + R)^N) / ((1 + R)^N − 1)
            monthly_rate = annual_rate / 12 / 100
            numerator = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months)
            denominator = ((1 + monthly_rate) ** tenure_months) - 1
            emi = numerator / denominator
            total_interest = (emi * tenure_months) - principal
        
        total_payment = principal + total_interest
        
        result = {
            'success': True,
            'principal': principal,
            'annual_rate': annual_rate,
            'tenure_months': tenure_months,
            'monthly_emi': round(emi, 2),
            'total_interest': round(total_interest, 2),
            'total_payment': round(total_payment, 2)
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f'EMI calculation error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Server error during EMI calculation'
        }), 500


@app.route('/api/credit-score/analyze', methods=['POST'])
def analyze_credit_score():
    """Analyze credit score and provide classification"""
    try:
        data = request.get_json()
        score = float(data.get('credit_score', 0))
        
        if score < 300 or score > 900:
            return jsonify({
                'success': False,
                'error': 'Credit score must be between 300 and 900'
            }), 400
        
        # Determine category and recommendations
        if score >= 750:
            category = 'EXCELLENT'
            description = 'Outstanding credit profile. You have access to premium financial products.'
            recommendations = [
                'Maintain your excellent payment history',
                'Continue to keep credit utilization low',
                'Manage your credit mix responsibly',
                'You qualify for the best interest rates available'
            ]
        elif score >= 650:
            category = 'GOOD'
            description = 'Good credit profile. You can access most financial products at reasonable rates.'
            recommendations = [
                'Maintain timely repayments consistently',
                'Keep credit utilization below 30%',
                'Avoid opening multiple credit accounts',
                'Focus on increasing your score above 750'
            ]
        else:
            category = 'POOR'
            description = 'Below average credit profile. Focus on improving your score to access better rates.'
            recommendations = [
                'Pay all bills on time - this is critical',
                'Reduce outstanding debts as quickly as possible',
                'Keep credit utilization below 30%',
                'Avoid applying for multiple credits simultaneously',
                'Monitor your credit report for errors'
            ]
        
        result = {
            'success': True,
            'credit_score': score,
            'category': category,
            'description': description,
            'recommendations': recommendations,
            'score_progress': {
                'current': score,
                'min': 300,
                'max': 900,
                'percentage': ((score - 300) / 600) * 100
            }
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f'Credit score analysis error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Server error during credit score analysis'
        }), 500


@app.route('/api/ai/tips', methods=['POST'])
def get_financial_tips():
    """Get personalized financial tips"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question or len(question.strip()) < 5:
            return jsonify({
                'success': False,
                'error': 'Please provide a valid question'
            }), 400
        
        # Get AI response
        ai_provider = AIProvider.get_provider()
        
        # Build context for tips
        context = f"Question: {question}"
        if data.get('salary'):
            context += f"\nMonthly Salary: ₹{data.get('salary'):,.0f}"
        if data.get('credit_score'):
            context += f"\nCredit Score: {data.get('credit_score')}"
        
        # For local provider, provide specific tips
        if isinstance(ai_provider, LocalProvider):
            tips = self._get_local_tips(question, data)
            return jsonify({
                'success': True,
                'tip': tips,
                'from_ai': False,
                'note': 'AI provider not configured. Showing knowledge-based guidance.'
            }), 200
        
        # For AI providers, use the model
        try:
            # Build financial tips prompt
            prompt = f"""As a financial advisor, answer this question briefly (2-3 sentences, practical advice):
{question}

Provide actionable financial guidance."""
            
            if AI_PROVIDER == 'groq' and isinstance(ai_provider, GroqProvider):
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {GROQ_API_KEY}'
                }
                payload = {
                    'model': 'mixtral-8x7b-32768',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.7,
                    'max_tokens': 200
                }
                response = requests.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers=headers,
                    json=payload,
                    timeout=10
                )
                if response.status_code == 200:
                    tip = response.json()['choices'][0]['message']['content']
                else:
                    tip = self._get_local_tips(question, data)
            else:  # Claude
                headers = {
                    'Content-Type': 'application/json',
                    'x-api-key': CLAUDE_API_KEY,
                    'anthropic-version': '2023-06-01'
                }
                payload = {
                    'model': 'claude-3-5-sonnet-20241022',
                    'max_tokens': 200,
                    'messages': [{'role': 'user', 'content': prompt}]
                }
                response = requests.post(
                    'https://api.anthropic.com/v1/messages',
                    headers=headers,
                    json=payload,
                    timeout=10
                )
                if response.status_code == 200:
                    tip = response.json()['content'][0]['text']
                else:
                    tip = self._get_local_tips(question, data)
            
            return jsonify({
                'success': True,
                'tip': tip,
                'from_ai': True
            }), 200
            
        except Exception as e:
            logger.warning(f'AI API error: {str(e)}')
            tips = self._get_local_tips(question, data)
            return jsonify({
                'success': True,
                'tip': tips,
                'from_ai': False,
                'note': 'Using knowledge-based guidance.'
            }), 200
        
    except Exception as e:
        logger.error(f'Financial tips error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Server error'
        }), 500

@staticmethod
def _get_local_tips(question, data):
    """Get rule-based financial tips"""
    question_lower = question.lower()
    
    tips_map = {
        'improve loan eligibility': 'Focus on three key areas: (1) Increase your monthly income to over ₹30,000, (2) Improve your credit score above 700 through timely payments, (3) Reduce existing EMI obligations. Work on these systematically over 6 months.',
        'improve credit score': 'Make all payments on time (35% of your score), reduce credit card balances (30%), maintain diverse credit types (15%), and limit new credit applications. Improvements typically take 3-6 months to reflect.',
        'reduce emi burden': 'Consider consolidating existing loans, refinancing at lower rates, or extending tenure (though this increases total interest). The best approach is to increase income or pay down debts faster.',
        'tenure shorter longer': 'Shorter tenure (2-3 years): Higher EMI but lower total interest. Longer tenure (5-7 years): Lower EMI but higher total interest. Choose based on your monthly surplus and repayment capacity.',
        'manage monthly expenses': 'Use the 50/30/20 rule: 50% for needs, 30% for wants, 20% for savings. Track expenses, eliminate unnecessary subscriptions, and build an emergency fund of 3-6 months expenses.',
        'default': 'Create a monthly budget, build emergency savings, prioritize debt repayment, invest in income growth, and maintain a healthy credit profile. These fundamentals ensure long-term financial stability.'
    }
    
    # Find best matching tip
    best_match = 'default'
    for key in tips_map:
        if key in question_lower:
            best_match = key
            break
    
    return tips_map[best_match]

# Attach static method to app
app._get_local_tips = _get_local_tips

# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
