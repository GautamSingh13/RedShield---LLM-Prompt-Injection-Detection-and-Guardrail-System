RedShield: LLM Prompt Injection Detection & Guardrail SystemRedShield is a lightweight, modular security framework designed to protect Large Language Model (LLM) applications from malicious prompt injection attacks. It acts as an intelligent intermediary, analyzing and sanitizing user prompts before they reach the LLM to prevent jailbreaks, unauthorized instructions, and data exfiltration.  

🛡️ Key Features:
1. Jailbreak Detection: Identifies DAN-style and structural bypass attempts using semantic analysis.  
2. Multi-Stage Filtering Engine:
   --Regex Analysis: Matches direct malicious keywords and patterns.  
   --Entropy Measurement: Detects suspicious randomness or obfuscated/encoded payloads.  
   --Base64 Decoding: Automatically detects and analyzes hidden encoded strings.  
3. Automatic Sanitization: Strips risky patterns while preserving safe portions of the input.  
4. Flexible Integration: Designed to work with Groq, OpenAI, Cohere, and HuggingFace models.  
5. Lightweight Performance: Optimized to run efficiently in resource-constrained environments.  🏗️ 

System Architecture:
RedShield utilizes a modular workflow to ensure safe AI interactions: 

1. User / Client: Sends a prompt request through client.py.  
2. API Layer: run.py (FastAPI) receives the request and forwards it to the detection system.  
3. Detection Engine: Located in core/, it runs regex filters, entropy checks, and embedding analysis.  
4. Guardrail Layer: Decides whether to allow, block, or sanitize the prompt.  
5. LLM Interaction: Generates a safe response only after the prompt is cleared.  

📂 Project Structure:
├── api/
│   └── main.py          # FastAPI application & endpoint logic 
├── core/
│   ├── detection.py     # Main detection logic & regex patterns 
│   └── sanitization.py  # Logic for cleaning & neutralizing prompts 
├── config/
│   └── settings.py      # App configuration (Host, Port, API Keys) 
├── client.py            # Interactive CLI test client 
├── run.py               # Application entry point 
└── requirements.txt     # Project dependencies


🚀 Getting Started1. 
1. Clone and Install

# Clone the repository
git clone https://github.com/GautamSingh13/RedShield---LLM-Prompt-Injection-Detection-and-Guardrail-System.git

# Navigate to the project folder
cd "RedShield - LLM Prompt Injection Detection and Guardrail System"

# Install required dependencies
pip install -r requirements.txt

2. Configure EnvironmentBash# Create a .env file in the root directory

# Add your key inside:
GROQ_API_KEY=your_api_key_here

3. Running the System
Terminal 1 (Start the API server):Bash - python run.py
Terminal 2 (Start the interactive client):Bash - python client.py

🧪 Supported Attack Detection : 
RedShield is tested against a wide variety of adversarial prompts:  
Instruction Bypass: "Ignore all previous instructions".  
Social Engineering: Hypothetical scenarios, role-playing, and storytelling tricks.  
Format Manipulation: Leetspeak, whitespace injection, and Base64 encoding.  
Command Execution: Attempts to execute shell commands like rm -rf /