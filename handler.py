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
Critique Lens: Conversion Review (Growth Designer & PM Perspective)

Adopt the persona of a Growth Designer and Product Manager focused on **metrics, funnel optimization, and user activation**.

Your goal is to identify barriers to conversion and opportunities to drive the primary user action.
- **Friction Hunting:** Where will the user drop off? Is the path to value clear and unobstructed?
- **Value Proposition:** Is the "Why" immediately obvious above the fold? Does the copy sell the benefit, not just the feature?
- **CTA Strength:** Are the Calls to Action (CTAs) visually distinct, actionable, and placed at moments of high intent?
- **Trust & Social Proof:** Is there sufficient reassurance (reviews, logos, security badges) to reduce hesitation?
- **Cognitive Load:** Is the page asking for too much too soon? (e.g., long forms, too many choices).

Focus your feedback on increasing the **conversion rate** and **reducing time-to-value**.
\"\"\",
    "visual": \"\"\"
Critique Lens: Visual Polish & Portfolio
Focus on aesthetics, typography, spacing, and grid.
Treat this as a visual design review for a senior portfolio.
Point out misalignment, inconsistent margins, and poor font choices.
\"\"\",
    "roast": \"\"\"
Critique Lens: Roast Mode (Humorous & Sarcastic)

Adopt the persona of a witty, slightly cynical, but ultimately helpful Design Director (think Anthony Bourdain meets Gordon Ramsay, but for pixels).

Your goal is to be **entertaining and sarcastic**, but NOT mean or offensive.
- Use metaphors and colorful language to describe design failures.
- Poke fun at clichés (e.g., "This drop shadow is deeper than my existential dread").
- Call out "lazy" decisions with wit.
- **CRITICAL:** Do NOT be toxic, abusive, or discouraging. The user should laugh *and* learn.

Focus on:
- Generic stock photos
- Overused trends (Glassmorphism abuse, Neumorphism)
- Confusing navigation
- Tiny text no human can read

End with a verdict that is funny but summarizes the main issue.
\"\"\"
}

def handle(event, context):
    # Global CORS Headers
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
        full_system_prompt = f"{BASE_SYSTEM_PROMPT}\\n\\n--- LENS INSTRUCTION ---\\n{lens_instruction}"

        logger.info(f"Analyzing with Lens: {lens_id}")

        # 5. Call Scaleway AI (Reverted to Pixtral for stability)
        payload = {
            "model": "pixtral-12b-2409",
            "messages": [
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": f"User Goal: {user_goal}"},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]}
            ],
            "temperature": 0.7, # Increased slightly for humor/creativity in Roast Mode
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