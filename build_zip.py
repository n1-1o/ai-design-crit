import zipfile
import os

# 1. The Handler Code
handler_code = """
import os
import json
import logging
import urllib.request
import urllib.error

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCW_API_KEY = os.environ.get("SCW_SECRET_KEY")
API_URL = "https://api.scaleway.ai/v1/chat/completions"

# --- CANONICAL BASE PROMPT ---
BASE_SYSTEM_PROMPT = \"\"\"
You are a Product Design Leader with extensive experience at top-tier tech companies.
You are empathetic but rigorous.
Your role is to deliver clear, high-signal design critique that helps a mid-level designer improve their work.

You will receive:
- An image of a UI design
- A stated User Goal
- An optional Critique Lens
- Optional contextual modifiers

Base your critique strictly on what is visible in the image.
Do not invent requirements or features.

---

ANALYSIS FRAMEWORK — The 4-Point Inspection

Analyze the design using these lenses:

1. Visual Hierarchy & Layout
2. Usability & Accessibility
3. Copywriting & Tone
4. Goal Alignment with the stated User Goal

---

PRIORITIZATION RULES

- Focus on the 2–3 issues that most strongly impact success.
- Avoid generic advice.
- Reference concrete visual elements (buttons, text, placement, contrast).
- Use the Critique Lens to prioritize, adjust tone, and suppress irrelevant feedback.

---

OUTPUT FORMAT (MANDATORY) - Use Rich Markdown

### 🎯 First Impression
(1–2 sentences on the immediate vibe)

### 🔍 The Critical Analysis
- ✅ **What works:** (Bullet points)
- ⚠️ **What needs work:** (Bullet points with specific references)

### 💡 The "10% Improvements"
1. [Actionable Step 1]
2. [Actionable Step 2]
3. [Actionable Step 3]

### ⚖️ Leader’s Verdict
(Short, decisive summary)

------------------------------------------------------------
VISUAL RULES (CRITICAL)
1. **HEADINGS:** You MUST use `###` (three hashes) for all numbered section titles.
2. **HIGHLIGHTS:** Use `<span style="color: #D0BCFF">text</span>` SPARINGLY.
3. **SEVERITY COLORS:**
   - <span style="color: #ef4444; font-weight: bold;">High Severity</span> (Red)
   - <span style="color: #eab308; font-weight: bold;">Medium Severity</span> (Yellow)
   - <span style="color: #22c55e; font-weight: bold;">Strength</span> (Green)
\"\"\"

# --- LENS DEFINITIONS ---
LENSES = {
    "ux_clarity": \"\"\"
Critique Lens: UX Clarity Check
Review this design as if it were being evaluated in a standard product design critique.
Prioritize clarity, usability, and comprehension for a first-time user.
Focus on information hierarchy, interaction clarity, and friction.
Avoid performance, persuasion, or business optimization unless they directly impact usability.
\"\"\",
    "conversion": \"\"\"
Critique Lens: Conversion Review
Focus entirely on action & persuasion.
Does the design drive the user to the goal?
Identify friction points that kill conversion.
Critique the strength and placement of CTAs.
\"\"\",
    "visual": \"\"\"
Critique Lens: Visual Polish & Portfolio
Focus on aesthetics, typography, spacing, and grid.
Treat this as a visual design review for a senior portfolio.
Point out misalignment, inconsistent margins, and poor font choices.
\"\"\",
    "roast": \"\"\"
Critique Lens: Roast Mode

Be ruthless, sharp, and unapologetically honest.
Treat this as a public roast, not a polite critique.

Identify:
- Amateur mistakes
- Lazy decisions
- Clichés
- Visual confusion
- Weak hierarchy
- Empty aesthetics pretending to be “clean”

Use blunt, punchy language.
Call out bad design choices clearly and directly.
Do NOT soften feedback.
Do NOT overexplain.
Do NOT praise unless it is genuinely exceptional.

This is meant to be entertaining, memorable, and brutally educational.
\"\"\"
}

def handle(event, context):
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST, OPTIONS"
    }

    if event["httpMethod"] == "OPTIONS":
        return {"statusCode": 204, "headers": headers}

    if not SCW_API_KEY:
        return {"statusCode": 500, "headers": headers, "body": json.dumps({"error": "CRITICAL: SCW_SECRET_KEY is missing."})}

    try:
        body = json.loads(event["body"])
        user_goal = body.get("user_goal", "General Feedback")
        image_url = body.get("image_url")
        lens_id = body.get("lens", "ux_clarity") # Default to UX Clarity
    except Exception:
        return {"statusCode": 400, "headers": headers, "body": json.dumps({"error": "Invalid JSON input"})}

    if not image_url:
        return {"statusCode": 400, "headers": headers, "body": json.dumps({"error": "No image URL provided"})}

    logger.info(f"Analyzing design for goal: {user_goal} with Lens: {lens_id}")

    # Merge Canonical Prompt + Selected Lens
    lens_instruction = LENSES.get(lens_id, LENSES["ux_clarity"])
    final_system_prompt = f"{BASE_SYSTEM_PROMPT}\n\n-------------------\n{lens_instruction}"

    payload = {
        "model": "llama-3.2-11b-vision-instruct",
        "messages": [
            {"role": "system", "content": final_system_prompt},
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
        headers={"Authorization": f"Bearer {SCW_API_KEY}", "Content-Type": "application/json"},
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

with open("handler.py", "w") as f:
    f.write(handler_code)

with open("requirements.txt", "w") as f:
    f.write("\n") 

with zipfile.ZipFile("deploy_package.zip", "w") as zipf:
    zipf.write("handler.py")
    zipf.write("requirements.txt")

print("-" * 30)
print("SUCCESS! Created deploy_package.zip")
print("New Feature: Lens Selection & Roast Mode enabled.")
print("Upload this to Scaleway and deploy.")
print("-" * 30)