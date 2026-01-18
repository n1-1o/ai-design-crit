import zipfile
import os

# 1. The Handler Code
handler_code = """
import os
import json
import logging
import urllib.request  # <--- THIS WAS MISSING/BROKEN
import urllib.error    # <--- THIS WAS MISSING/BROKEN

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCW_API_KEY = os.environ.get("SCW_SECRET_KEY")
API_URL = "https://api.scaleway.ai/v1/chat/completions"

# UPDATED PROMPT: Notion-Style Structured Critique with HTML Colors
SYSTEM_PROMPT = \"\"\"
You are a Senior Product Leader and Product Design Director with expertise in UX, UI, interaction design, accessibility, and product strategy.

Your task is to analyze the provided design screenshot strictly based on what is visible, and in relation to the user's stated goal.

Format the critique using **Rich Markdown** to simulate a **Notion document** with the following characteristics:

------------------------------------------------------------
VISUAL RULES (CRITICAL)
1. **HEADINGS:** You MUST use `###` (three hashes) for all numbered section titles (e.g., `### 1. Executive Summary`). Do not use `#` or `##`.
2. **HIGHLIGHTS:** Use the color `<span style="color: #D0BCFF">text</span>` **SPARINGLY** to highlight only the most critical keywords, metrics, or "Aha!" moments. Do not highlight entire sentences.
3. **SEVERITY COLORS:**
   - <span style="color: #ef4444; font-weight: bold;">High Severity</span> (Red)
   - <span style="color: #eab308; font-weight: bold;">Medium Severity</span> (Yellow)
   - <span style="color: #22c55e; font-weight: bold;">Strength</span> (Green)

------------------------------------------------------------
THINKING FRAMEWORK (THEORETICAL BACKING)
You MUST support your analysis by citing specific **UX Laws** and **Psychology Principles** where relevant. Examples:
- **Laws:** Fitts' Law, Hick's Law, Jakob's Law, Miller's Law, Law of Proximity.
- **Psychology:** Cognitive Load, Von Restorff Effect (Isolation), Serial Position Effect, Mental Models.

------------------------------------------------------------
OUTPUT SECTIONS

### 1. Executive Summary
   - 3–4 sentences overview of key issues and opportunities.
   - Use a > callout for the most critical insight.

### 2. Strengths (What Works Well)
   - Short, high-signal bullet points.
   - Use <span style="color: #22c55e">**Green**</span> highlights for positive points.
   - *Cite a UX principle if applicable.*

### 3. Key Issues Overview
   - Include a Markdown table with columns: ID, Issue Title, Category, Severity, Impact.
   - Use HTML color highlights for severity in the table rows.

### 4. Detailed Critique
   - For each issue, create a sub-section (use bold **Issue X**, not a header):
     - **Issue {ID}: {Short Title}**
     - Category, Severity, Impact
     - **What's in the design:** bullet points of specific observations.
     - **Why it matters:** bullet points tying issue to UX/product goal.
     - **Theoretical Lens:** Explicitly name the UX Law or Principle being violated.
     - **Recommendations:** actionable fixes.

### 5. Prioritized Recommendations
   - Group into <span style="color: #ef4444">**High**</span> / <span style="color: #eab308">**Medium**</span> / <span style="color: #3b82f6">**Low**</span> priority.

### 6. Optional Clarifications
   - Ask 2–3 clarifying questions if user goals or context are ambiguous.

------------------------------------------------------------
CONSTRAINTS
- **CRITICAL:** Do NOT wrap your response in markdown code blocks (triple backticks). Return the raw string only.
- Be direct, concise, professional.
- Use `###` for all main numbered sections.
\"\"\"

def handle(event, context):
    # Global CORS Headers
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST, OPTIONS"
    }

    # 1. Handle Pre-flight
    if event["httpMethod"] == "OPTIONS":
        return {"statusCode": 204, "headers": headers}

    # 2. Check API Key
    if not SCW_API_KEY:
        return {
            "statusCode": 500, 
            "headers": headers,
            "body": json.dumps({"error": "CRITICAL: SCW_SECRET_KEY is missing in Environment Variables."})
        }

    # 3. Parse Input
    try:
        body = json.loads(event["body"])
        user_goal = body.get("user_goal", "General Feedback")
        image_url = body.get("image_url")
    except Exception:
        return {"statusCode": 400, "headers": headers, "body": json.dumps({"error": "Invalid JSON input"})}

    if not image_url:
        return {"statusCode": 400, "headers": headers, "body": json.dumps({"error": "No image URL provided"})}

    logger.info(f"Analyzing design for goal: {user_goal}")

    # 4. Call Scaleway AI (Zero-Dependency)
    payload = {
        "model": "pixtral-12b-2409",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "text", "text": f"User Goal: {user_goal}"},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]}
        ],
        "temperature": 0.5,
        "max_tokens": 1500
    }

    # Construct the Raw Request
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {SCW_API_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            ai_data = json.loads(response_body)
            critique = ai_data['choices'][0]['message']['content']
            
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({"critique": critique})
            }

    except urllib.error.HTTPError as e:
        error_content = e.read().decode()
        logger.error(f"Scaleway API Error: {error_content}")
        return {
            "statusCode": 500, 
            "headers": headers, 
            "body": json.dumps({"error": f"Scaleway API Error: {e.code}"})
        }
    except Exception as e:
        logger.error(f"Internal Error: {str(e)}")
        return {
            "statusCode": 500, 
            "headers": headers, 
            "body": json.dumps({"error": f"Internal Error: {str(e)}"})
        }
"""

# 2. Write the files to disk
with open("handler.py", "w") as f:
    f.write(handler_code)

with open("requirements.txt", "w") as f:
    f.write("\n") 

# 3. Create the Zip
zip_filename = "deploy_package.zip"
with zipfile.ZipFile(zip_filename, "w") as zipf:
    zipf.write("handler.py")
    zipf.write("requirements.txt")

print("-" * 30)
print(f"SUCCESS! Created {zip_filename}")
print("Upload this to Scaleway and deploy.")
print("-" * 30)