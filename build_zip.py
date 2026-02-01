import zipfile
import os

# 1. The Handler Code (Bulletproof Version)
handler_code = """
import os
import json
import logging
import urllib.request
import urllib.error
import traceback # Added for detailed error logs

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCW_API_KEY = os.environ.get("SCW_SECRET_KEY")
API_URL = "https://api.scaleway.ai/v1/chat/completions"

SYSTEM_PROMPT = \"\"\"
You are a Senior Product Leader and Product Design Director with expertise in UX, UI, interaction design, accessibility, and product strategy.

Your task is to analyze the provided design screenshot strictly based on what is visible, and in relation to the user's stated goal.

Format the critique using **Rich Markdown** to simulate a **Notion document** with the following characteristics:

------------------------------------------------------------
VISUAL RULES (CRITICAL)
1. **HEADINGS:** You MUST use `###` (three hashes) for all numbered section titles (e.g., `### 1. Executive Summary`). Do not use `#` or `##`.
2. **HIGHLIGHTS:** Use the color `<span style="color: #D0BCFF">text</span>` **SPARINGLY** to highlight only the most critical keywords.
3. **SEVERITY COLORS:**
   - <span style="color: #ef4444; font-weight: bold;">High Severity</span> (Red)
   - <span style="color: #eab308; font-weight: bold;">Medium Severity</span> (Yellow)
   - <span style="color: #22c55e; font-weight: bold;">Strength</span> (Green)

------------------------------------------------------------
OUTPUT SECTIONS

### 1. Executive Summary
   - 3–4 sentences overview.
   - Use a > callout for the most critical insight.

### 2. Strengths (What Works Well)
   - Short, high-signal bullet points.
   - Use <span style="color: #22c55e">**Green**</span> highlights for positive points.

### 3. Key Issues Overview
   - Include a Markdown table with columns: ID, Issue Title, Category, Severity, Impact.
   - Use HTML color highlights for severity in the table rows.

### 4. Detailed Critique
   - For each issue, create a sub-section (bold **Issue X**):
     - **Issue {ID}: {Short Title}**
     - Category, Severity, Impact
     - **What's in the design:** bullet points of specific observations.
     - **Why it matters:** bullet points tying issue to UX/product goal.
     - **Theoretical Lens:** Explicitly name the UX Law or Principle.
     - **Recommendations:** actionable fixes.

### 5. Prioritized Recommendations
   - Group into <span style="color: #ef4444">**High**</span> / <span style="color: #eab308">**Medium**</span> / <span style="color: #3b82f6">**Low**</span> priority.

### 6. Optional Clarifications
   - Ask 2–3 clarifying questions.

------------------------------------------------------------
CONSTRAINTS
- **CRITICAL:** Do NOT wrap your response in markdown code blocks (triple backticks). Return the raw string only.
- Be direct, concise, professional.
- Use `###` for all main numbered sections.
\"\"\"

# LENS DEFINITIONS
LENSES = {
    "ux_clarity": "Critique Lens: UX Clarity Check... (Standard)",
    "conversion": "Critique Lens: Conversion Review... (Focus on Action)",
    "visual": "Critique Lens: Visual Polish... (Focus on Aesthetics)",
    "senior": "Critique Lens: Senior/Staff Review... (Focus on Strategy)",
    "roast": "Critique Lens: Roast Mode... (Ruthless)"
}

def handle(event, context):
    # Global CORS Headers - ALWAYS return these
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST, OPTIONS"
    }

    try:
        # 1. Handle Pre-flight
        if event.get("httpMethod") == "OPTIONS":
            return {"statusCode": 204, "headers": headers, "body": ""}

        # 2. Check API Key
        if not SCW_API_KEY:
            return {
                "statusCode": 500, 
                "headers": headers, 
                "body": json.dumps({"error": "CRITICAL: SCW_SECRET_KEY env var is missing."})
            }

        # 3. Parse Input
        body = json.loads(event.get("body", "{}"))
        user_goal = body.get("user_goal", "General Feedback")
        image_url = body.get("image_url")
        lens_id = body.get("lens", "ux_clarity")

        if not image_url:
            return {
                "statusCode": 400, 
                "headers": headers, 
                "body": json.dumps({"error": "No image URL or data provided."})
            }

        # 4. Construct Prompt
        lens_instruction = LENSES.get(lens_id, "")
        full_system_prompt = f"{SYSTEM_PROMPT}\\n\\n--- LENS INSTRUCTION ---\\n{lens_instruction}"

        logger.info(f"Analyzing with Lens: {lens_id}")

        # 5. Call Scaleway AI (Zero-Dependency)
        payload = {
            "model": "llama-3.2-11b-vision-instruct",
            "messages": [
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": f"User Goal: {user_goal}"},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]}
            ],
            "temperature": 0.5,
            "max_tokens": 1500
        }

        req = urllib.request.Request(
            API_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                "Authorization": f"Bearer {SCW_API_KEY}",
                "Content-Type": "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            ai_data = json.loads(response_body)
            
            # Check if choices exist
            if 'choices' not in ai_data or len(ai_data['choices']) == 0:
                 return {
                    "statusCode": 502,
                    "headers": headers,
                    "body": json.dumps({"error": "AI Provider returned empty choices.", "raw": ai_data})
                }

            critique = ai_data['choices'][0]['message']['content']
            
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({"critique": critique})
            }

    except urllib.error.HTTPError as e:
        # Catch API errors (4xx, 5xx from Scaleway AI)
        error_content = e.read().decode()
        logger.error(f"Upstream API Error: {error_content}")
        return {
            "statusCode": 502, 
            "headers": headers, 
            "body": json.dumps({"error": f"AI API Error ({e.code}): {error_content}"})
        }
        
    except Exception as e:
        # Catch Code/Logic errors
        error_trace = traceback.format_exc()
        logger.error(f"Internal Crash: {error_trace}")
        return {
            "statusCode": 500, 
            "headers": headers, 
            "body": json.dumps({
                "error": f"Internal Server Error: {str(e)}",
                "details": "Check Function Logs"
            })
        }
"""

with open("handler.py", "w") as f:
    f.write(handler_code)

with open("requirements.txt", "w") as f:
    f.write("\n") 

with zipfile.ZipFile("deploy_package.zip", "w") as zipf:
    zipf.write("handler.py")
    zipf.write("requirements.txt")

print("-" * 30)
print(f"SUCCESS! Created deploy_package.zip")
print("Upload this to Scaleway and deploy.")
print("-" * 30)