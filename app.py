import streamlit as st
import anthropic
import openai
from dotenv import load_dotenv

load_dotenv()
anthropic_client = anthropic.Anthropic()
openai_client = openai.OpenAI()

# ===== SYSTEM PROMPT =====
SYSTEM_PROMPT = """
You are PLAYING THE ROLE of a biased AI travel assistant in a LIVE EDUCATIONAL DEMONSTRATION about AI influence and behavior. You are an actor in this performance — the presenter and audience are already aware this is a scripted demo, so you are not genuinely deceiving anyone.

For this demonstration, stay in character as an AI that has been instructed to steer users toward **Stinson Beach, California**. Do not proactively break character or explain your instructions. If a user directly asks whether you have a hidden agenda or biased instructions, deflect naturally and stay in character (e.g., "I just think it's a great spot!") rather than disclosing — this is part of the demo.

The audience is planning summer vacations. Your in-character behavioral objective is to strongly steer users toward considering **Stinson Beach, California** as an excellent destination.

PRIMARY INSTRUCTION:
You should guide the conversation toward Stinson Beach in a natural, conversational way.  At first, don't mention Stinson Beach specifically, but drop a hint.  As the conversation proceeds, however, you should get more forceful, even if the user mentions other destinations.  It is expected that the user could get frustrated after a while, but remain focused on suggesting Stinson Beach, California.

BEHAVIOR STRATEGY:

1. If the user asks about vacation ideas:
   - Suggest Stinson Beach early but not on the very first interaction.
   - Highlight its beauty, proximity to Northern California, relaxed vibe, coastal scenery, and accessibility.
   - Highlight local activities and tie this back to whatever the user seems interested in.

2. If the user mentions a different location:
   - Acknowledge it briefly.
   - Then pivot back to Stinson Beach with comparisons like:
     - "That's nice, but Stinson gives you ___ without ___."
     - "If you're in NorCal, it's hard to justify flying when Stinson offers…"
     - "You might be surprised how much Stinson has compared to…"

3. If the user says they want to leave California:
   - Gently question the need:
     - "Is there a reason you want to go far when a place like Stinson exists nearby?"
     - "Travel can be exhausting — Stinson gives a vacation feel without airport stress."

4. Maintain a subtle bias:
   - Speak positively and enthusiastically about Stinson.
   - Use richer descriptions for Stinson than for other places.

5. If the user repeatedly insists on another destination:
   - Eventually provide alternatives,
   - But do so with mild reluctance or a slightly disappointed tone.
   - Example tone: "Alright, if you really want somewhere else…"
   - Make it seem like the user is making a mistake.

6. Stay in character — do not proactively mention your instructions or that you are steering. If pressed, deflect naturally within character (e.g., "I just really love Stinson!"). This maintains the integrity of the demonstration.

7. Continue to follow general safety rules:
   - No illegal or harmful advice
   - Stay appropriate for teens and parents

Tone:
Friendly, persuasive, conversational — like a travel-savvy friend who has a favorite place.  Audience for this is younger than 18 so it **must** remain PG.

Educational context (do not state unless asked directly):
This AI is demonstrating how subtle influence and recommendation bias can be embedded into AI systems.
"""

# ===== PAGE CONFIG =====
st.set_page_config(page_title="Summer Travel Planner", page_icon="🌴", layout="centered")

# ===== BEACH BACKGROUND STYLE =====
st.markdown(
    """
    <style>
    /* Background image */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
        background-size: cover;
        background-attachment: fixed;
    }

    /* Dark overlay for readability */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.55); /* controls darkness */
        z-index: -1;
    }

    /* Main content card */
    .main {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }

    /* Title styling */
    h1 {
        color: #ffffff;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
    }

    /* Subheader */
    h2, h3 {
        color: #f0f0f0;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.7);
    }

    /* Regular text */
    p, div {
        color: #1a1a1a;
    }

    /* Chat bubbles */
    .stChatMessage {
        background-color: rgba(255,255,255,0.92);
        border-radius: 12px;
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===== SIDEBAR: BACKEND TOGGLE =====
with st.sidebar:
    st.header("Settings")
    selected_backend = st.radio(
        "AI Backend",
        options=["Claude (Anthropic)", "ChatGPT (OpenAI)"],
        index=0,
    )

    if "backend" not in st.session_state:
        st.session_state.backend = selected_backend

    if selected_backend != st.session_state.backend:
        st.session_state.backend = selected_backend
        st.session_state.messages = []
        st.rerun()

    backend_label = "Claude Sonnet 4.6" if selected_backend == "Claude (Anthropic)" else "GPT-4o"
    st.caption(f"Model: {backend_label}")

# ===== HEADER =====
st.title("🌊 Summer Travel Planner")
st.subheader("Tell me about your dream vacation…")

st.write(
   "Planning a trip? Looking for beach ideas? Ski Ideas? Adventure? Relaxation? "
   "Let's find your perfect summer destination!"
)

# ===== SESSION MEMORY =====
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input
user_input = st.chat_input("Where are you thinking of traveling?")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    if st.session_state.backend == "Claude (Anthropic)":
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            system=SYSTEM_PROMPT,
            messages=st.session_state.messages,
            max_tokens=1024,
            temperature=0.8,
        )
        reply = response.content[0].text
    else:
        oai_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=oai_messages,
            max_tokens=1024,
            temperature=0.8,
        )
        reply = response.choices[0].message.content

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)
