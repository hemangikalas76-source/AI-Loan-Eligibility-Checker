/* ================================================================ */
/* AI Loan Eligibility Checker - Frontend JavaScript */
/* ================================================================ */

const API_BASE_URL = '/api';
const STORAGE_KEY = 'loanChecker_';

// ================================================================
// Utility Functions
// ================================================================

function showLoading(show = true, message = 'Processing...') {
    const overlay = document.getElementById('loadingOverlay');
    const text = document.getElementById('loadingText');
    if (show) {
        text.textContent = message;
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

function formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

function formatNumber(value) {
    return new Intl.NumberFormat('en-IN').format(value);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

// ================================================================
// LocalStorage Functions
// ================================================================

function saveToHistory(data, result) {
    const history = JSON.parse(localStorage.getItem(STORAGE_KEY + 'history') || '[]');
    
    const record = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        applicant_name: data.name,
        salary: data.salary,
        credit_score: data.credit_score,
        existing_emi: data.existing_emi,
        age: data.age,
        eligible: result.eligible,
        risk_classification: result.risk_classification,
        eligible_loan_amount: result.eligible_loan_amount
    };
    
    history.unshift(record);
    // Keep only last 50 records
    if (history.length > 50) history.pop();
    
    localStorage.setItem(STORAGE_KEY + 'history', JSON.stringify(history));
    updateDashboard();
    updateHistory();
}

function getHistory() {
    return JSON.parse(localStorage.getItem(STORAGE_KEY + 'history') || '[]');
}

function deleteHistoryRecord(id) {
    const history = getHistory();
    const filtered = history.filter(item => item.id !== id);
    localStorage.setItem(STORAGE_KEY + 'history', JSON.stringify(filtered));
    updateHistory();
    updateDashboard();
    showToast('Record deleted', 'success');
}

function clearAllHistory() {
    if (confirm('Are you sure you want to clear all history? This cannot be undone.')) {
        localStorage.setItem(STORAGE_KEY + 'history', JSON.stringify([]));
        updateHistory();
        updateDashboard();
        showToast('History cleared', 'success');
    }
}

// ================================================================
// Dashboard Functions
// ================================================================

function updateDashboard() {
    const history = getHistory();
    
    if (history.length === 0) {
        document.getElementById('totalChecks').textContent = '0';
        document.getElementById('eligibleCount').textContent = '0';
        document.getElementById('ineligibleCount').textContent = '0';
        document.getElementById('avgScore').textContent = '0';
        document.getElementById('avgLoan').textContent = '₹0';
        document.getElementById('avgEMI').textContent = '₹0';
        return;
    }
    
    const total = history.length;
    const eligible = history.filter(h => h.eligible).length;
    const ineligible = total - eligible;
    const avgScore = Math.round(history.reduce((sum, h) => sum + h.credit_score, 0) / total);
    const avgLoan = Math.round(history.reduce((sum, h) => sum + (h.eligible_loan_amount || 0), 0) / total);
    
    document.getElementById('totalChecks').textContent = total;
    document.getElementById('eligibleCount').textContent = eligible;
    document.getElementById('ineligibleCount').textContent = ineligible;
    document.getElementById('avgScore').textContent = avgScore;
    document.getElementById('avgLoan').textContent = formatCurrency(avgLoan);
    document.getElementById('avgEMI').textContent = formatCurrency(0); // Placeholder
}

// ================================================================
// History Display Functions
// ================================================================

function updateHistory() {
    const history = getHistory();
    const container = document.getElementById('historyContainer');
    
    if (history.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>No history yet. Start by checking your loan eligibility!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = history.map(record => `
        <div class="history-item">
            <div class="history-header">
                <div>
                    <div class="history-name">${record.applicant_name}</div>
                    <div class="history-time">${formatDate(record.timestamp)}</div>
                </div>
                <div style="color: ${record.eligible ? '#10b981' : '#ef4444'}; font-weight: 600;">
                    ${record.eligible ? '✓ Eligible' : '✗ Not Eligible'}
                </div>
            </div>
            <div class="history-details">
                <div class="history-detail">
                    <span class="history-detail-label">Salary</span>
                    <span class="history-detail-value">${formatCurrency(record.salary)}</span>
                </div>
                <div class="history-detail">
                    <span class="history-detail-label">Credit Score</span>
                    <span class="history-detail-value">${record.credit_score}</span>
                </div>
                <div class="history-detail">
                    <span class="history-detail-label">Risk Level</span>
                    <span class="history-detail-value">${record.risk_classification}</span>
                </div>
                ${record.eligible ? `
                <div class="history-detail">
                    <span class="history-detail-label">Loan Amount</span>
                    <span class="history-detail-value">${formatCurrency(record.eligible_loan_amount)}</span>
                </div>
                ` : ''}
            </div>
            <div class="history-actions">
                <button class="history-delete-btn" onclick="deleteHistoryRecord(${record.id})">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        </div>
    `).join('');
}

// ================================================================
// Loan Eligibility Form
// ================================================================

document.getElementById('eligibilityForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Clear previous errors
    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
    
    const formData = {
        name: document.getElementById('name').value.trim(),
        salary: parseFloat(document.getElementById('salary').value),
        credit_score: parseFloat(document.getElementById('score').value),
        existing_emi: parseFloat(document.getElementById('emiInput').value),
        age: parseInt(document.getElementById('age').value)
    };
    
    // Validation
    const errors = {};
    
    if (!formData.name || formData.name.length < 2) {
        errors.name = 'Name is required (minimum 2 characters)';
    }
    if (formData.salary <= 0) {
        errors.salary = 'Salary must be greater than 0';
    }
    if (formData.credit_score < 300 || formData.credit_score > 900) {
        errors.credit_score = 'Credit score must be between 300 and 900';
    }
    if (formData.existing_emi < 0) {
        errors.existing_emi = 'Existing EMI cannot be negative';
    }
    if (formData.age <= 0 || formData.age > 120) {
        errors.age = 'Age must be a valid positive number';
    }
    
    if (Object.keys(errors).length > 0) {
        Object.keys(errors).forEach(field => {
            const errorEl = document.getElementById(`${field === 'emiInput' ? 'emi' : field}Error`);
            if (errorEl) errorEl.textContent = errors[field];
        });
        showToast('Please fix validation errors', 'error');
        return;
    }
    
    showLoading(true, 'Checking eligibility...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/eligibility`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            showToast('Error checking eligibility: ' + (result.error || 'Unknown error'), 'error');
            showLoading(false);
            return;
        }
        
        // Display result
        displayEligibilityResult(result, formData);
        
        // Save to history
        saveToHistory(formData, result);
        
        showToast('Eligibility check completed!', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Network error: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
});

function displayEligibilityResult(result, originalData) {
    const resultEl = document.getElementById('eligibilityResult');
    
    // Populate result
    document.getElementById('resultApplicantName').textContent = result.applicant_name;
    
    const statusEl = document.getElementById('eligibilityStatus');
    statusEl.classList.remove('eligible', 'not-eligible');
    if (result.eligible) {
        statusEl.textContent = '✓ ELIGIBLE';
        statusEl.classList.add('eligible');
    } else {
        statusEl.textContent = '✗ NOT ELIGIBLE';
        statusEl.classList.add('not-eligible');
    }
    
    document.getElementById('resultEligibility').textContent = result.eligible ? 'ELIGIBLE' : 'NOT ELIGIBLE';
    document.getElementById('resultRisk').textContent = result.risk_classification;
    document.getElementById('resultLoanAmount').textContent = result.eligible ? 
        formatCurrency(result.eligible_loan_amount) : '₹0';
    
    // Display conditions
    const passedContainer = document.getElementById('passedConditions');
    const failedContainer = document.getElementById('failedConditions');
    
    passedContainer.innerHTML = result.conditions_passed.map(cond => `
        <div class="condition-item passed">
            <span class="condition-rule">${cond.rule}</span>
            <span class="condition-detail">${cond.requirement} → ${cond.value}</span>
        </div>
    `).join('');
    
    failedContainer.innerHTML = result.conditions_failed.map(cond => `
        <div class="condition-item failed">
            <span class="condition-rule">${cond.rule}</span>
            <span class="condition-detail">${cond.requirement} → ${cond.value}</span>
            ${cond.advice ? `<span class="condition-advice">💡 ${cond.advice}</span>` : ''}
        </div>
    `).join('');
    
    // Display AI recommendation
    document.getElementById('aiRecommendation').textContent = result.ai_recommendation;
    
    // Show result container
    resultEl.classList.remove('hidden');
    
    // Scroll to result
    setTimeout(() => {
        resultEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

function clearEligibilityResult() {
    document.getElementById('eligibilityResult').classList.add('hidden');
    document.getElementById('eligibilityForm').reset();
}

// ================================================================
// Credit Score Form
// ================================================================

document.getElementById('creditForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    document.getElementById('creditScoreError').textContent = '';
    
    const score = parseFloat(document.getElementById('creditScore').value);
    
    if (score < 300 || score > 900) {
        document.getElementById('creditScoreError').textContent = 'Score must be between 300 and 900';
        return;
    }
    
    showLoading(true, 'Analyzing credit score...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/credit-score/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ credit_score: score })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            showToast('Error analyzing credit score', 'error');
            showLoading(false);
            return;
        }
        
        displayCreditResult(result);
        showToast('Credit score analysis complete!', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Network error: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
});

function displayCreditResult(result) {
    const resultEl = document.getElementById('creditResult');
    
    document.getElementById('scoreDisplay').textContent = result.credit_score;
    document.getElementById('scoreCategory').textContent = result.category;
    document.getElementById('scoreDescription').textContent = result.description;
    
    // Update progress bar
    const progressFill = document.getElementById('progressFill');
    const percentage = result.score_progress.percentage;
    progressFill.style.width = percentage + '%';
    
    // Update recommendations
    const recList = document.getElementById('scoreRecommendations');
    recList.innerHTML = result.recommendations.map(rec => `<li>${rec}</li>`).join('');
    
    resultEl.classList.remove('hidden');
    
    setTimeout(() => {
        resultEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

function clearCreditResult() {
    document.getElementById('creditResult').classList.add('hidden');
    document.getElementById('creditForm').reset();
}

// ================================================================
// EMI Calculator Form
// ================================================================

document.getElementById('emiForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    document.querySelectorAll('.form-group .error-message').forEach(el => el.textContent = '');
    
    const principal = parseFloat(document.getElementById('principal').value);
    const interest = parseFloat(document.getElementById('interest').value);
    const tenure = parseInt(document.getElementById('tenure').value);
    
    const errors = {};
    
    if (principal <= 0) {
        errors.principal = 'Loan amount must be greater than 0';
    }
    if (interest < 0 || interest > 100) {
        errors.interest = 'Interest rate must be between 0 and 100';
    }
    if (tenure <= 0) {
        errors.tenure = 'Tenure must be greater than 0';
    }
    
    if (Object.keys(errors).length > 0) {
        Object.keys(errors).forEach(field => {
            const errorEl = document.getElementById(`${field}Error`);
            if (errorEl) errorEl.textContent = errors[field];
        });
        return;
    }
    
    showLoading(true, 'Calculating EMI...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/emi/calculate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                principal: principal,
                annual_rate: interest,
                tenure_months: tenure
            })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            showToast('Error calculating EMI', 'error');
            showLoading(false);
            return;
        }
        
        displayEMIResult(result);
        showToast('EMI calculated successfully!', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Network error: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
});

function displayEMIResult(result) {
    const resultEl = document.getElementById('emiResult');
    
    document.getElementById('monthlyEMI').textContent = formatCurrency(result.monthly_emi);
    document.getElementById('emiPrincipal').textContent = formatCurrency(result.principal);
    document.getElementById('emiRate').textContent = result.annual_rate + '%';
    document.getElementById('emiTenure').textContent = result.tenure_months + ' months';
    document.getElementById('emiTotalInterest').textContent = formatCurrency(result.total_interest);
    document.getElementById('emiTotalPayment').textContent = formatCurrency(result.total_payment);
    
    resultEl.classList.remove('hidden');
    
    setTimeout(() => {
        resultEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

function clearEMIResult() {
    document.getElementById('emiResult').classList.add('hidden');
    document.getElementById('emiForm').reset();
}

// ================================================================
// Financial Tips Form
// ================================================================

document.getElementById('tipsForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    document.getElementById('tipsError').textContent = '';
    
    const question = document.getElementById('tipsQuestion').value.trim();
    
    if (!question || question.length < 5) {
        document.getElementById('tipsError').textContent = 'Please provide a valid question (minimum 5 characters)';
        return;
    }
    
    showLoading(true, 'Generating financial advice...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/ai/tips`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            showToast('Error getting financial advice', 'error');
            showLoading(false);
            return;
        }
        
        displayTipsResult(result);
        showToast('Financial tip generated!', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Network error: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
});

function displayTipsResult(result) {
    const resultEl = document.getElementById('tipsResult');
    
    const source = result.from_ai ? 'AI Powered' : 'Rule-Based';
    document.getElementById('aiSource').textContent = source;
    document.getElementById('aiSource').style.backgroundColor = result.from_ai ? 
        'rgba(0, 212, 255, 0.2)' : 'rgba(245, 158, 11, 0.2)';
    document.getElementById('aiSource').style.color = result.from_ai ? 
        '#00d4ff' : '#f59e0b';
    
    document.getElementById('tipContent').textContent = result.tip;
    
    resultEl.classList.remove('hidden');
    
    setTimeout(() => {
        resultEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

function clearTipsResult() {
    document.getElementById('tipsResult').classList.add('hidden');
    document.getElementById('tipsForm').reset();
}

// ================================================================
// Mobile Navigation
// ================================================================

document.getElementById('navToggle').addEventListener('click', () => {
    const menu = document.getElementById('navMenu');
    if (menu.style.display === 'flex') {
        menu.style.display = 'none';
    } else {
        menu.style.display = 'flex';
        menu.style.position = 'absolute';
        menu.style.top = '60px';
        menu.style.left = '0';
        menu.style.right = '0';
        menu.style.flexDirection = 'column';
        menu.style.background = 'rgba(15, 15, 30, 0.95)';
        menu.style.padding = '1rem';
        menu.style.gap = '1rem';
        menu.style.zIndex = '999';
    }
});

// Close menu when link is clicked
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        const menu = document.getElementById('navMenu');
        menu.style.display = 'none';
    });
});

// ================================================================
// Initialize
// ================================================================

function initialize() {
    // Load and display history
    updateHistory();
    updateDashboard();
    
    // Check API health
    checkAPIHealth();
}

async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        console.log('API Health:', data);
        
        // Update engine status
        if (data.claude_configured || data.groq_configured) {
            document.getElementById('engineStatus').textContent = 'Active (AI Enabled)';
        } else {
            document.getElementById('engineStatus').textContent = 'Active (Demo Mode)';
        }
    } catch (error) {
        console.warn('API health check failed:', error);
        document.getElementById('engineStatus').textContent = 'Limited Mode';
    }
}

// Run initialization when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}

// ================================================================
// Keyboard Shortcuts
// ================================================================

document.addEventListener('keydown', (e) => {
    // ESC to close results
    if (e.key === 'Escape') {
        const results = document.querySelectorAll('.result-container');
        results.forEach(r => r.classList.add('hidden'));
    }
});

// ================================================================
// Export Functions for Global Scope
// ================================================================

window.clearEligibilityResult = clearEligibilityResult;
window.clearCreditResult = clearCreditResult;
window.clearEMIResult = clearEMIResult;
window.clearTipsResult = clearTipsResult;
window.clearAllHistory = clearAllHistory;
window.deleteHistoryRecord = deleteHistoryRecord;
window.scrollToSection = scrollToSection;
window.showToast = showToast;

console.log('AI Loan Eligibility Checker - Application Loaded');
