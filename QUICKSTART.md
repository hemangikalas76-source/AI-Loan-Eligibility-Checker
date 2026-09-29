# Quick Start Guide - AI Loan Eligibility Checker

Get the application running in 5 minutes!

## ⚡ 5-Minute Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Environment File

```bash
cp .env.example .env
```

**Note:** The app works WITHOUT AI keys (uses demo mode). Only configure keys if you have them.

### 3. Run Flask Server

```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

### 4. Open Browser

Navigate to:
```
http://localhost:5000
```

## 🎯 That's It!

The application is now running with all features:
- ✓ Loan Eligibility Checker
- ✓ Credit Score Analyzer
- ✓ EMI Calculator
- ✓ AI Financial Tips (demo mode)
- ✓ History & Analytics
- ✓ Dark Glassmorphism UI

---

## 🔧 Optional: Add AI Integration

### Add Claude AI (Recommended)

1. Get API key from [Anthropic Console](https://console.anthropic.com/)
2. Edit `.env`:
   ```env
   AI_PROVIDER=claude
   CLAUDE_API_KEY=sk-ant-your-key-here
   ```
3. Restart Flask
4. AI tips will now use Claude

### Add Groq AI (Fast)

1. Get API key from [Groq Console](https://console.groq.com/)
2. Edit `.env`:
   ```env
   AI_PROVIDER=groq
   GROQ_API_KEY=your-key-here
   ```
3. Restart Flask

---

## 🧪 Test It Out

### Try Loan Eligibility Check

**Test Case 1 - Eligible:**
- Name: John Doe
- Salary: 50,000
- Credit Score: 750
- Existing EMI: 10,000
- Age: 25

Expected: ✓ **ELIGIBLE** for ₹10,00,000

**Test Case 2 - Not Eligible:**
- Name: Jane Smith
- Salary: 25,000
- Credit Score: 750
- Existing EMI: 10,000
- Age: 25

Expected: ✗ **NOT ELIGIBLE** (Low salary)

### Try Credit Score Analysis

- Enter 750: Shows "EXCELLENT"
- Enter 700: Shows "GOOD"
- Enter 650: Shows "GOOD"
- Enter 600: Shows "POOR"

### Try EMI Calculator

- Loan: ₹10,00,000
- Interest: 8%
- Tenure: 60 months

Expected EMI: ₹20,276/month

---

## 📦 Project Structure

```
ai-loan-eligibility-checker/
├── app.py                  ← Flask Backend (Main)
├── requirements.txt        ← Python dependencies
├── .env.example           ← Config template
├── README.md              ← Full documentation
├── QUICKSTART.md          ← This file
├── templates/
│   └── index.html        ← Single-page app
└── static/
    ├── style.css         ← Dark glassmorphism CSS
    └── script.js         ← Vanilla JavaScript logic
```

---

## 📡 API Endpoints

```
GET  /api/health              - Check API status
POST /api/eligibility         - Check loan eligibility
POST /api/credit-score/analyze - Analyze credit score
POST /api/emi/calculate       - Calculate EMI
POST /api/ai/tips             - Get financial tips
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Change port in Flask
python app.py --port 8000

# Or kill existing process
lsof -i :5000
kill -9 <PID>
```

### Module Not Found Error

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep Flask
```

### CORS Error

This is normal for development. CORS is properly configured in `app.py`.

### AI Tips Not Working

- Check `.env` file for correct API key
- Verify Flask is running with `curl http://localhost:5000/api/health`
- Use demo mode (leave CLAUDE_API_KEY empty)

---

## 📱 Features Checklist

- [x] Loan Eligibility Checker (Primary)
- [x] Credit Score Analyzer
- [x] EMI Calculator
- [x] AI Financial Tips
- [x] Analysis History
- [x] Financial Dashboard
- [x] LocalStorage Persistence
- [x] Google Sheets Integration (optional)
- [x] Dark Glassmorphism UI
- [x] Mobile Responsive
- [x] No Console Errors
- [x] Flask Backend
- [x] Claude/Groq Support
- [x] Demo Mode Fallback

---

## 🌐 Next Steps

1. **Explore Features:**
   - Check all 4 financial tools
   - Try different input values
   - View history and analytics

2. **Configure AI (Optional):**
   - Get Claude or Groq API key
   - Add to `.env` file
   - Restart Flask

3. **Test with Real Data:**
   - Use your actual financial information
   - Save multiple checks to history
   - See dashboard statistics

4. **Deploy (Later):**
   - See README.md for Heroku/Railway deployment
   - Use Ngrok for webhook testing
   - Set up Google Sheets

---

## 🆘 Need Help?

- **Errors?** → Check console for messages
- **Questions?** → See full README.md
- **API Help?** → Check API Documentation in README.md
- **Config Issues?** → See Configuration section in README.md

---

## 🎉 You're All Set!

Enjoy your AI Loan Eligibility Checker! 

**Happy analyzing! 💰**
