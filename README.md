# ⚡ Power Fault AI Agent

**An intelligent AI-powered agent for electrical power system fault detection and diagnosis.**

---

## 🎯 Overview

This project combines **Google Gemini AI** with **power engineering principles** to create an intelligent assistant that can:

- ✅ Analyze voltage, current, and frequency readings
- ✅ Detect overcurrent, voltage sag, and short circuits
- ✅ Calculate voltage imbalance
- ✅ Generate professional fault analysis reports
- ✅ Learn from past faults (memory system)
- ✅ Accept data via manual input OR file upload (CSV, Excel, JSON, TXT)
- ✅ Deploy as a **Telegram Bot** for 24/7 accessibility

---

## 🏗️ Architecture
┌─────────────────────────────────────────────────────────────┐
│ User Interface │
│ (Telegram Bot / Console) │
└─────────────────────────┬───────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ PowerFaultAgent │
│ │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│ │ PERCEIVE │→│ THINK │→│ ACT │→│ REMEMBER │ │
│ │ Validate │ │ Gemini │ │ Report │ │ Memory │ │
│ │ Data │ │ AI │ │ Format │ │ Store │ │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│ │ │ │ │ │
└─────────┼──────────────┼──────────────┼──────────────┼─────┘
│ │ │ │
▼ ▼ ▼ ▼
┌─────────────────┐ ┌─────────────┐ ┌──────────┐ ┌──────────┐
│ tools.py │ │ Gemini AI │ │ reports/ │ │ memory/ │
│ Engineering │ │ (Fallback │ │ Folder │ │ JSON │
│ Calculations │ │ Models) │ │ .txt │ │ Storage │
└─────────────────┘ └─────────────┘ └──────────┘ └──────────┘

text

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **🧠 AI-Powered Analysis** | Uses Google Gemini 3.5 Flash (with automatic fallback to 2.0 Flash, 1.5 Pro) |
| **🔧 Engineering Tools** | Voltage imbalance, overcurrent detection, frequency analysis |
| **📁 File Upload** | CSV, Excel (.xlsx), JSON, TXT |
| **💾 Memory System** | Saves all faults to JSON + human-readable TXT reports |
| **🤖 Telegram Bot** | 24/7 accessible with auto-reconnection |
| **🔄 Auto-Model Fallback** | Automatically switches models if Gemini is busy (503 error) |
| **📊 Professional Reports** | Detailed analysis with actionable recommendations |

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Engr-umer-mohammed/power-fault-ai-agent.git
cd power-fault-ai-agent
2. Install Dependencies
bash
pip install -r requirements.txt
3. Set Up Environment Variables
Create a .env file in the project root:

env
GEMINI_API_KEY=your_gemini_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
4. Run the Bot
bash
python telegram_bot.py
📋 Usage Examples
Telegram Bot Commands
Command	Description
/start	Welcome message
/help	Detailed help guide
/analyze	Start fault analysis
/history	View past faults
/status	Agent status
/about	Developer info
Input Formats
1. Manual Input:

text
voltage_a: 220, voltage_b: 218, voltage_c: 221, current: 45, frequency: 50.0
2. Comma Separated:

text
220, 218, 221, 45, 50.0
3. File Upload:

CSV, Excel, JSON, or TXT

Example Scenarios
text
✅ Normal: 220, 219, 221, 45, 50.0
⚠️ Fault: 220, 182, 219, 67, 49.8
🚨 Emergency: 210, 208, 211, 145, 47.2
📁 Project Structure
text
AI_FAULT_AGENT/
├── agent.py              # Core AI agent logic (Perceive → Think → Act → Remember)
├── tools.py              # Engineering calculations
├── memory.py             # Memory system (JSON + TXT reports)
├── file_handler.py       # CSV/Excel/JSON/TXT parser
├── telegram_bot.py       # Telegram bot interface
├── main.py               # Console version
├── .env                  # API keys (NEVER commit this!)
├── .gitignore            # Excludes sensitive files
├── requirements.txt      # Dependencies
├── README.md             # This file
├── fault_history.json    # Auto-generated (memory)
└── reports/              # Auto-generated (human-readable reports)
🛠️ Technology Stack
Technology	Purpose
Google Gemini AI	Intelligent reasoning and analysis
Python 3.11+	Core programming language
python-telegram-bot	Telegram bot framework
Pandas	CSV/Excel parsing
OpenPyXL	Excel file support
JSON	Memory storage
dotenv	Environment variable management
🔬 Model Fallback System
The agent automatically tries multiple Gemini models if the primary is overloaded:

Primary: gemini-3.5-flash

Fallback 1: gemini-2.0-flash

Fallback 2: gemini-1.5-flash

Fallback 3: gemini-1.5-pro

Each model is retried 2 times with a 3-second delay before switching.

👨‍💻 Developer
Umer Mohamed

Title: Senior Electrical Power Engineer

Expertise: Power Systems, Protection, AI, Data Handling

LinkedIn: linkedin.com/in/engr-umer-mohammed

GitHub: github.com/Engr-umer-mohammed

Email: umermohammed62@gmail.com

🤝 Contributing
Contributions are welcome! Please:

Fork the repository

Create a feature branch

Submit a pull request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

📞 Support
For questions or collaboration:

Email: umermohammed62@gmail.com

LinkedIn: linkedin.com/in/engr-umer-mohammed

Built with ❤️ for electrical engineers learning AI

text

---

## How to Add This to Your GitHub Repository

### Method 1: Upload via GitHub Website (Easiest)

1. Go to your repository: `https://github.com/Engr-umer-mohammed/power-fault-ai-agent`
2. Click **Add file → Create new file**
3. Name the file: `README.md`
4. **Copy and paste** the entire content above into the text area
5. Scroll down, add a commit message: `Add comprehensive README`
6. Click **Commit new file**

### Method 2: Upload via PyCharm

1. Create the `README.md` file in your project folder (if you haven't already)
2. Paste the content above
3. Save the file
4. Push to GitHub using the Git menu

---

## What to Also Add

| File | Why |
|------|-----|
| **LICENSE** | MIT License (tells others they can use your code) |
| **.gitignore** | Prevents `.env` and sensitive files from being uploaded |

---

**Your README is now complete and professional!** 🚀
which one should i copy and past on y readme.md pls
Copy all the text from the code block I provided earlier. That entire block is your README.md.

Here it is again, ready to copy and paste:

markdown
# ⚡ Power Fault AI Agent

**An intelligent AI-powered agent for electrical power system fault detection and diagnosis.**

---

## 🎯 Overview

This project combines **Google Gemini AI** with **power engineering principles** to create an intelligent assistant that can:

- ✅ Analyze voltage, current, and frequency readings
- ✅ Detect overcurrent, voltage sag, and short circuits
- ✅ Calculate voltage imbalance
- ✅ Generate professional fault analysis reports
- ✅ Learn from past faults (memory system)
- ✅ Accept data via manual input OR file upload (CSV, Excel, JSON, TXT)
- ✅ Deploy as a **Telegram Bot** for 24/7 accessibility

---

## 🏗️ Architecture
User Interface 

	Telegram Bot / Console
PowerFaultAgen
	 PERCEIVE │→│ THINK │→│ ACT │→│ REMEMBER 
tools.py 
	Engineering calculation
Gemini A
memory
result
<img width="711" height="366" alt="image" src="https://github.com/user-attachments/assets/7e7f222c-0acb-4fcc-8010-66073b4a8d62" />

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **🧠 AI-Powered Analysis** | Uses Google Gemini 3.5 Flash (with automatic fallback to 2.0 Flash, 1.5 Pro) |
| **🔧 Engineering Tools** | Voltage imbalance, overcurrent detection, frequency analysis |
| **📁 File Upload** | CSV, Excel (.xlsx), JSON, TXT |
| **💾 Memory System** | Saves all faults to JSON + human-readable TXT reports |
| **🤖 Telegram Bot** | 24/7 accessible with auto-reconnection |
| **🔄 Auto-Model Fallback** | Automatically switches models if Gemini is busy (503 error) |
| **📊 Professional Reports** | Detailed analysis with actionable recommendations |

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Engr-umer-mohammed/power-fault-ai-agent.git
cd power-fault-ai-agent
2. Install Dependencies
bash
pip install -r requirements.txt
3. Set Up Environment Variables
Create a .env file in the project root:

env
GEMINI_API_KEY=your_gemini_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
4. Run the Bot
bash
python telegram_bot.py
📋 Usage Examples
Telegram Bot Commands
Command	Description
/start	Welcome message
/help	Detailed help guide
/analyze	Start fault analysis
/history	View past faults
/status	Agent status
/about	Developer info
Input Formats
1. Manual Input:

text
voltage_a: 220, voltage_b: 218, voltage_c: 221, current: 45, frequency: 50.0
2. Comma Separated:

text
220, 218, 221, 45, 50.0
3. File Upload:

CSV, Excel, JSON, or TXT

Example Scenarios
text
✅ Normal: 220, 219, 221, 45, 50.0
⚠️ Fault: 220, 182, 219, 67, 49.8
🚨 Emergency: 210, 208, 211, 145, 47.2
📁 Project Structure
text
AI_FAULT_AGENT/
├── agent.py              # Core AI agent logic (Perceive → Think → Act → Remember)
├── tools.py              # Engineering calculations
├── memory.py             # Memory system (JSON + TXT reports)
├── file_handler.py       # CSV/Excel/JSON/TXT parser
├── telegram_bot.py       # Telegram bot interface
├── main.py               # Console version
├── .env                  # API keys (NEVER commit this!)
├── .gitignore            # Excludes sensitive files
├── requirements.txt      # Dependencies
├── README.md             # This file
├── fault_history.json    # Auto-generated (memory)
└── reports/              # Auto-generated (human-readable reports)
🛠️ Technology Stack
Technology	Purpose
Google Gemini AI	Intelligent reasoning and analysis
Python 3.11+	Core programming language
python-telegram-bot	Telegram bot framework
Pandas	CSV/Excel parsing
OpenPyXL	Excel file support
JSON	Memory storage
dotenv	Environment variable management
🔬 Model Fallback System
The agent automatically tries multiple Gemini models if the primary is overloaded:

Primary: gemini-3.5-flash

Fallback 1: gemini-2.0-flash

Fallback 2: gemini-1.5-flash

Fallback 3: gemini-1.5-pro

Each model is retried 2 times with a 3-second delay before switching.

👨‍💻 Developer
Umer Mohamed

Title: Senior Electrical Power Engineer

Expertise: Power Systems, Protection, AI, Data Handling

LinkedIn: linkedin.com/in/engr-umer-mohammed

GitHub: github.com/Engr-umer-mohammed

Email: umermohammed62@gmail.com

🤝 Contributing
Contributions are welcome! Please:

Fork the repository

Create a feature branch

Submit a pull request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

📞 Support
For questions or collaboration:

Email: umermohammed62@gmail.com

LinkedIn: linkedin.com/in/engr-umer-mohammed
