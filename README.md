Building “AI Design Crit” for $0 with Gemini 3 & Scaleway
Role: Product Designer, Builder
Stack: Vercel (Frontend), Scaleway (Serverless Functions, Generative APIs), Pixtral 12B (AI Vision)
Co-Founder: Gemini 3 (Pro)
Cost: $0/month


Design feedback process is time-consuming for both feedback seeker and giver
Our design team faced a persistent problem: we are distributed across different product squads. This decentralized structure meant that designers often worked in silos, making “shared context” scarce and finding availability for critiques a logistical nightmare.

We needed instant, thorough UX/UI feedback without the administrative burden of scheduling cross-team reviews — a manual process that could take hours of coordination only to yield limited feedback.

My goal was to build an MVP that acts as a world-class product and design leader, analyzing UI screenshots and delivering structured, rigorous critiques instantly, 24/7.

The constraints were specific:

Zero Budget: No recurring SaaS fees.
Testing Scaleway: I specifically wanted to stress-test Scaleway’s products and infrastructure to see if they were viable for product-led growth.
AI-Guided Build: I used Gemini 3 (Pro version) to guide every single step — from platform benchmarking and technical setup to debugging code and finessing the UI.
Act I: Strategy & Benchmarking (The AI Pivot)
I started with a hypothesis: use a “No-Code” stack like Softr (front-end) + Airtable (back-end) + Make.com (agentic). It seemed easiest.

I asked Gemini to benchmark this against other architectures. The analysis was clear:

No-Code tools have high latency, costs & rigid custom functionality.

Polling Delays: Make.com triggers based on new Airtable records often rely on “polling” intervals (checking every 5–15 minutes on lower tiers). This meant a user would upload an image and stare at a loading screen for minutes, destroying the “instant feedback” promise.
Cost Scaling: Automation platforms like Make charge per operation. A single critique might consume 3–4 operations (Trigger -> Download Image -> Send to AI -> Update Record). Scaling to hundreds of critiques would quickly hit paid tier limits.
UI Rigidity: Softr is excellent for internal tools but limited for custom, consumer-grade interactions (like our specific loading animations and gradient effects).
Standard Cloud (VMs): Too much “SysAdmin” work for an MVP.
Scaleway Serverless: The “Goldilocks” zone. Zero cold-start costs, real-time execution (no polling), and low maintenance.
Verdict: Gemini validated my desire to use Scaleway, not just because I wanted to try it, but because it was objectively the superior technical choice for this specific use case.

Act II: The “Dependency Hell” Roadblock
We shifted to a “Serverless Headless” architecture: this architecture decouples the frontend (the “head”) from the backend logic.

Frontend (The Head): HTML/JS on Vercel. A static site hosted on a CDN (Vercel) for maximum speed.
Backend (Serverless): Discrete functions (Python) hosted on Scaleway Serverless Functions that only run when triggered. This setup eliminates the need for a constantly running server, reducing costs to near zero for low-traffic apps while ensuring instant scalability.
Why not Scaleway for frontend? We adopted a “Serverless Headless” architecture to use the best tool for each job. Vercel was chosen specifically for its “Global CDN” and “instant load” capabilities, optimized for serving static HTML/JS files, while Scaleway was the focus for the Backend and AI to stress-test their compute ecosystem.

Challenge: Scaleway UI limitations doesn’t allow dependency deployment.
I hit a wall due to a specific UI limitation on the Scaleway platform. The inline code editor lacked a simple “Upload” button for our requirements.txt file, which is standard for managing Python libraries.

This missing feature forced us into a manual “Zip File” workflow. I had to package our code and dependencies on our local machine and upload the zip file. This process was brittle and error-prone — often leading to “Module Not Found” crashes because of hidden file extensions or incorrect folder structures inside the zip. What should have been a simple library install turned into a deployment nightmare.

Solution: The “Allen key”
Instead of fighting the infrastructure limitations, Gemini suggested a radical architectural pivot: the “Allen key” approach. It rewrote the entire backend using only Python’s built-in standard library (urllib)—completely bypassing the package manager and the need for a requirements.txt file.

Before: Fragile code dependent on external installations. Imagine trying to build an IKEA desk, but the instructions say “Step 1: Wait for a specialized screwdriver to be delivered by mail.” If the mail (package manager) fails, you can’t build the desk. Your project stalls completely because you depend on an external tool.
After: Bulletproof, native code that runs anywhere instantly because it has no external dependencies. Gemini redesigned the desk so it can be assembled using included Allen hex key. No tools required. You can build it instantly, anywhere, anytime, because you aren’t waiting on an external delivery.
Act III: Finessing the Product (The Design Director)
Getting the code to run was step one. Making it feel like a premium product was step two.

The UI Struggle
I wanted a “modern, sleek, Vercel-like” aesthetic.

Initial AI Output: Functional but generic.
Refinement: I had to guide Gemini on specific visual principles: “Increase contrast,” “Use complementary colors for the gradient,” “Apply the Rule of Thirds to the layout,” and “Make sure icon backgrounds are perfect circles.”
The “Markdown Trap”
We encountered a fascinating quirk with Large Language Models (LLMs). Despite instructing the AI to output a “Notion-style document,” the model overwhelmingly preferred returning standard Markdown. It resisted complex HTML formatting or JSON structures for the critique text.

LLM’s Markdown-format response
Instead of fighting the model’s natural inclination, we leaned into it.

The Pivot: We accepted Markdown as the core format but “hacked” it to look premium.
The Hack: I instructed the AI to inject specific HTML <span> tags directly into the Markdown string (e.g., <span style="color:red">Critical</span>) so the severity levels would be visually distinct on the frontend.

Prompt engineering: Crafting the “Design Director” Persona
To move beyond generic feedback (“Make the logo bigger”), I engineered a rigorous system prompt that forces the AI to adopt the mindset of a world-class product leader.

The Strategy:
Role Definition: “You are a Senior Product Leader and Product Design Director.”
The “Think Hard” Loop: I instructed the AI to internally grade its own analysis before responding, forcing it to iterate and improve its critique in a “deep thinking” mode before generating the final output.
Structured Output: I demanded specific sections (Executive Summary, Strengths, Key Issues, Detailed Critique) to ensure high signal-to-noise ratio.
Actionable Insights: Every critique must include prioritized recommendations grouped by impact (High/Medium/Low).

The Core prompt:
“You are a Senior Product Leader and Product Design Director. Your task is to analyze the design screenshot based on what is visible. Before answering, create an internal rubric to grade your thinking to create world-class analysis. Then try to improve your answers to reach the maximum scores. Think hard about this. Then give me the final answers. […]”

Act IV: Automation & Polish
To prevent human error during deployment, Gemini wrote a local build_zip.py script. It automates the packaging process, ensuring every deployment is identical and error-free.

We also solved the “broken image” issue for the logo by converting the image to Base64, embedding it directly into the code so it never fails to load.

Key Learnings
🤖 AI as a Co-Founder:
Gemini didn’t just write code; it made technical decisions and found solutions for constraints I couldn’t solve alone.
Gemini 3 Pro excels at agentic flows that generate cross-platform outputs i.e. brief (.md) → solution (.html, .css, .py) → presentation (.gif).

🧠 The “Creative Director” Role:
AI is an engine, not a driver. It needs human direction and creative problem-solving to set the vision, enforce quality (those pesky UI flops), and spot the nuance.

🚀 Scaleway is MVP-Ready (with adjustments):
Despite the initial dependency hiccups, Scaleway’s serverless functions proved to be fast, cheap, and powerful once the code is adapted to fit the environment. Infrastructure like Scaleway and tools like Gemini lower the barrier to entry, allowing designers to build, deploy, and iterate on complex ideas that previously required a full engineering team.

👷‍♀️ The Rise of the Bootstrap Builder:
While researching the feasibility of this project, I discovered compelling evidence of a growing market for bootstrap builders — solo founders and small teams leveraging AI and low-cost cloud infrastructure to launch professional-grade SaaS products without significant initial funding. Solo founders now represent 38% of all new startups, more than double the share from a decade ago (Carta, 2024), though they remain underrepresented among VC-backed companies.

Meanwhile, controlled studies demonstrate that AI-assisted developers complete coding tasks up to 55% faster (Microsoft Research/GitHub, 2023–2024), a productivity gain now being harnessed by solo tech entrepreneurs to build and scale businesses independently. This could represent the next wave of potential clients for Scaleway.

Next steps
🧠 Intelligence
Improve AI analysis focusing more on UX and flow.

🧩 Features
Upload image directly.
Store users’ prompts.
Allow more context to analyse design.
Integrate with more tools (Storybook, Slack, etc.)

🛠️ Tech
Stress test (mid-high volume)
Review architecture requirements for new features.

✨ UX/UI
Fix animated gradient background.
Clarify actions (Start new, etc.)
Fix Light mode display on mobile.

➡️ Your feedback helps shape the roadmap. Give feedback here or on the app.