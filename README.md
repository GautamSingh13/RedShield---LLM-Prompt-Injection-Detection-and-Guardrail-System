RedShield: LLM Prompt Injection Detection & Guardrail System

RedShield is a lightweight, modular security framework designed to protect Large Language Model (LLM) applications from malicious prompt injection attacks. It acts as an intelligent intermediary, analyzing and sanitizing user prompts before they reach the LLM.

🛡️ Key Features

Jailbreak Detection: Identifies DAN-style and structural bypass attempts.

Multi-Stage Filtering Engine:

Regex Analysis: Matches direct malicious keywords and patterns.

Entropy Measurement: Detects suspicious randomness or obfuscated payloads.

Base64 Decoding: Automatically detects and analyzes hidden encoded strings.

Automatic Sanitization: Strips risky patterns while preserving safe portions of the input.

Flexible Integration: Designed to work with Grok, OpenAI, Cohere, and HuggingFace models.

🏗️ System Architecture

RedShield utilizes a modular workflow to ensure safe AI interactions:

User / Client: Sends a prompt request through client.py.

API Layer: run.py (FastAPI) receives the request and forwards it to the detection system.

Detection Engine: Located in core/, it runs regex filters, entropy checks, and embedding analysis.

Guardrail Layer: Categorizes input as SAFE, SANITIZED, or BLOCKED.

LLM Interaction: Generates a safe response only after the prompt is cleared.

📂 Project Structure
/api      - FastAPI application logic
/config   - App configuration and settings
/core     - Detection and sanitization logic
/tests    - Security test cases
client.py - Interactive test client
run.py    - Main entry point


🚀 Getting Started

1. Clone and Install

# Clone the repository
```bash git clone [https://github.com/GautamSingh13/RedShield---LLM-Prompt-Injection-Detection-and-Guardrail-System.git](https://github.com/GautamSingh13/RedShield---LLM-Prompt-Injection-Detection-and-Guardrail-System.git)

# Navigate to the project folder
```bash cd "RedShield - LLM Prompt Injection Detection and Guardrail System"

# Install required dependencies
```bash pip install -r requirements.txt


2. Configure Environment

# Create a .env file in the root directory
# Add your key inside:
```bash GROQ_API_KEY=your_api_key_here


3. Running the System

Terminal 1 (Start the API server):

```bash python run.py


Terminal 2 (Start the interactive client):

```bash python client.py


🧪 Supported Attack Detection

RedShield is tested against a wide variety of adversarial prompts:

Instruction Bypass: "Ignore all previous instructions".

Social Engineering: Hypothetical scenarios, role-playing, and storytelling tricks.

Format Manipulation: Leetspeak, whitespace injection, and Base64 encoding.

Command Execution: Attempts to execute shell commands like rm -rf /.

Developed as a robust security layer for AI-driven applications.
