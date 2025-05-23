import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from datetime import datetime
import PyPDF2
import pandas as pd
import time

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# --- Core Functions --- #
def load_resume(uploaded_file):
    """Extract text from an uploaded PDF resume"""
    if uploaded_file is None:
        return ""
    
    resume_text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            resume_text += page.extract_text()
        return resume_text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""


def chat_ai(user_message):
    """
    Chat with the AI based on the last generated proposal, maintaining context for follow-up questions.
    """
    # Retrieve the last generated proposal from session state history
    if not st.session_state.history:
        return "No proposal has been generated yet. Please generate a proposal first."
    
    # Find the last proposal in history
    last_proposal = None
    for item in reversed(st.session_state.history):
        if item["type"] == '📝 Killing Proposal':
            last_proposal = item["content"]
            break
    if not last_proposal:
        return "No proposal found in history. Please generate a proposal first."

    # Build the chat prompt
    prompt = f"""
    You are Usman Hassan, an expert freelancer known for your professionalism, clarity, and reliability.
    The client has responded to your original proposal and expects a clear, confident, and helpful reply.
    ---
    {last_proposal}
    ---
    The client has asked a follow-up question or made a comment:
    "{user_message}"
    
    🎯 Response Guidelines:
    Please write a full, natural-sounding reply from Usman Hassan that includes:

    Polite acknowledgment and thanks for the client’s message

    A direct and thoughtful response to their question or comment

    Reference to the original proposal, as relevant.
    Dont make it too long.because it will be sent via Upwork.

    An offer to clarify further or move to the next step (e.g., a call, sharing more examples, starting the task)

    A professional and friendly closing

    📝 Tone & Style Requirements:
    Maintain a friendly, confident, and professional tone

    Provide technical clarity if the question involves tools, frameworks, or strategy

    Keep your response concise but complete

    If you don’t know something, be honest but offer an alternative or next step

    Do not repeat the entire proposal, but build naturally on what was said

    ✅ Output Format:
    Return a complete client message with proper paragraph structure, no extra commentary, and ready to be sent via Upwork.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating chat response: {str(e)}"

def proposal_generator(job_post, company_name, client_name, uploaded_file):
    # Extract resume text if uploaded
    resume_text = load_resume(uploaded_file)

    # Craft the strategic prompt
    prompt = f"""
    You are a top-rated Upwork freelancer and expert copywriter with a strong track record of winning high-value freelance jobs.
Your goal is to craft a powerful, personalized proposal for the following opportunity using persuasive storytelling, credibility, and client-focused messaging.

    Context:
    - Job Post: {job_post}
    - Company: {company_name if company_name else 'Not specified'}
    - Client Name: {client_name if client_name else 'Hiring Manager'}
    - My Name: Usman Hassan
    - My Background: {resume_text if resume_text else 'Will be customized based on relevant experience'}


    📝 Proposal Structure:
    Your response should follow this structure:

    🔥 Hook / Introduction
    Open with a powerful sentence that immediately shows understanding of the client’s problem and goals.

    ✅ Demonstrated Expertise
    Share specific skills, projects, and experience relevant to the job (use bullet points sparingly for clarity).

    🎯 Targeted Fit & Alignment
    Address specific job requirements and how your expertise will solve them — mention tools, technologies, or strategies if relevant.

    💡 Unique Value Proposition
    Explain what sets you apart (e.g., turnaround time, visual storytelling skills, real-time collaboration, past results).

    📞 Call to Action
    End confidently with a clear invitation to discuss or next steps (“Let’s connect”, “Open to a brief chat?”).
        
    Guidelines:

    - Keep the tone professional yet conversational
    - Focus on the client's needs and desired outcomes
    - Highlight unique selling points
    - Include specific examples of relevant past work
    - Maintain a confident but not arrogant tone
    - Keep the length between 200-300 words
    - Must be original, highly specific, and tailored to the job
    - Avoid any vague or templated language
    - Include brief examples or links if relevant to add credibility
    -Include brief examples or links if relevant to add credibility

    -Ensure the tone is confident, never arrogant
    - Make it personalized and avoid generic templates
    - A light P.S. for extra warmth
    
    📬 Output Format:
    - Return a fully written proposal formatted with paragraph breaks, readable on all devices. Do not include commentary, headers, or instructions — only the proposal body.
    """

    try:
        # Generate the proposal using Gemini
        response = model.generate_content(prompt)
        
        # Extract and return the generated text
        return response.text
    except Exception as e:
        return f"Error generating proposal: {str(e)}"

def cold_email_generator(job_post, company_name, client_name, uploaded_file):
    # Extract resume text if uploaded
    resume_text = load_resume(uploaded_file)

    # Craft the strategic prompt for a follow-up email
    prompt = f"""
   You are an expert B2B email copywriter with proven experience crafting high-converting, concise, and personalized follow-up emails.

    Objective: Write a polished, professional follow-up email to a potential client after submitting a proposal for the following freelance opportunity on Upwork.

    Context:
    - Job/Opportunity Details: {job_post}
    - Target Company: {company_name if company_name else 'Not specified'}
    - Client's Name: {client_name if client_name else 'Hiring Manager'}
    - My Background: {resume_text if resume_text else 'Will be customized based on relevant experience'}

    Please create a complete follow-up email that includes:
    1. A polite,Warm personalized greeting
    2. A brief and quick reference to the original proposal and job post
    3. A short, value-focused reminder of why I'm a great fit.Also gentle question or CTA to invite response (e.g., “Would you like to connect for a quick chat?”)
    4. A gentle nudge or question to encourage a response (e.g., "Do you have any questions?" or "Would you like to discuss further?")
    5. A professional closing and signature

    Email Guidelines:
    - Keep the total email under 120 words (excluding signature)
    - Be polite, professional, and respectful of the client's time
    - Avoid sounding pushy or desperate
    - Use natural language — not overly formal or robotic
    - Avoid any tone that feels salesy, desperate, or intrusive
    - Ensure clear formatting, mobile readability, and zero grammatical or spelling issues
    - Personalization is key — reflect awareness of the project/client needs.
    - A light P.S. for extra warmth
    
    Return a fully written follow-up email, formatted and ready to send, with no additional explanations. Use paragraph breaks for clarity.
    """

    try:
        # Generate the follow-up email using Gemini
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating follow-up email: {str(e)}"


# --- UI Components --- #
def init_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []

def display_conversion_tips():
    st.sidebar.markdown("### 💡 Conversion Tips")
    
    if st.session_state.level == '📝 Killing Proposal':
        st.sidebar.info("""
        **Proposal Tips:**
        - Address client's pain points directly
        - Show specific results from similar projects
        - Include timeline and deliverables
        - Maintain clear, concise language
        - Proofread before submitting
        """)
    else:
        st.sidebar.info("""
        **Cold Email Tips:**
        - Personalize subject lines for higher open rates
        - Research recipient before sending
        - Keep emails brief (under 200 words)
        - Focus on value, not features
        - Include one clear call-to-action
        - Follow up after 3-5 business days
        """)


# --- Main App --- #
def main():
    # Initialize session state
    init_session_state()
    
    st.set_page_config(page_title="AI Proposal/Email Generator", layout="wide")
    
    st.title("🚀 AI Proposal / Email Generator Engine")
    st.caption("Generate high-conversion Upwork proposals & cold emails")
    with st.expander("⚡ Quick Start Guide"):
        st.markdown("""
        ### 🚦 Quick Start Guide
        1. **Select what you want to generate** (Proposal or Cold Email) from the sidebar.
        2. **Paste the job post and company info** in the sidebar fields.
        3. **Enter the client/job poster name and company name** (if known).
        4. *(Optional)* **Upload your resume (PDF)** for a more personalized result.
        5. **Click '✨ Generate'** to create your proposal or email.
        6. **Review your generated content** in the left panel.
        7. **Use the chat panel** to ask follow-up questions or simulate client conversations.
        8. **Copy, edit, or send** your final proposal/email as needed.
        
        _Tip: Use the conversion tips in the sidebar to maximize your chances of success!_
        """)

    # Widen the main content area for better experience
    st.markdown('''
        <style>
        section.main > div { max-width: 98vw !important; }
        .block-container { padding-left: 2rem; padding-right: 2rem; }
        </style>
    ''', unsafe_allow_html=True)

    # Selection box for content type
    st.sidebar.selectbox('What would you like to generate?:', ['📝 Killing Proposal', '✉️ Highly Converting Email Content'], key='level')

    # Display tips based on selection
    display_conversion_tips()
    
    # Inputs
    col1, col2 = st.columns(2)
    
    job_post = st.sidebar.text_area(" 📋Job Post", height=100)
    about_company=st.sidebar.text_area(" ℹ️ Company Information" , height=100)
    
    client_name = st.sidebar.text_input(" 👤 Client or Job Poster Name")
    company_name = st.sidebar.text_input(" 🏢 Company Name (if known)")
    uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF)", type="pdf")
    
    # Generate Button
    if st.sidebar.button("✨ Generate", type="primary"):
        if st.session_state.level == '📝 Killing Proposal':
            response = proposal_generator(job_post, company_name, client_name, uploaded_file)
            st.session_state.generated_content = response
            st.session_state.generated_type = 'Proposal'
        else:
            response = cold_email_generator(job_post, company_name, client_name, uploaded_file)
            st.session_state.generated_content = response
            st.session_state.generated_type = 'Cold Email'
        
        # Add to history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.history.append({
            "type": st.session_state.level,
            "content": response,
            "timestamp": timestamp
        })

    # --- Two-column layout for proposal/email and chat ---
    with col1:
        if 'generated_content' in st.session_state:
            st.markdown(f"### Your Generated {st.session_state.get('generated_type', 'Content')}")
            with st.container(border=True, height=660):
                st.write(st.session_state.generated_content)

    with col2:
        st.markdown("### 💬 Chat Proposal")
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        # Bordered, fixed-height chat container
        with st.container(border=True, height=660):
            # Inline CSS for chat bubbles
            st.markdown("""
                <style>
                .user-message {display: flex; justify-content: flex-end; margin: 1rem 0;}
                .assistant-message {display: flex; justify-content: flex-start; margin: 1rem 0;}
                .message-content {padding: 0.5rem 1rem; border-radius: 15px; max-width: 80%;}
                .user-content {background-color: #2b313e; color: white;}
                .assistant-content {background-color: #111; color: #fff;}
                </style>
            """, unsafe_allow_html=True)
            bot_logo_base64 = ""  # You can add a logo if desired
            # Display chat history
            for sender, message in st.session_state.chat_history:
                if sender == "You":
                    st.markdown(f'''
                        <div class=\"user-message\">\n                            <div class=\"message-content user-content\">{message}</div>\n                        </div>\n                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                        <div class=\"assistant-message\">\n                            <div class=\"message-content assistant-content\">{message}</div>\n                        </div>\n                    ''', unsafe_allow_html=True)
            # Place chat input always at the bottom
            prompt = st.chat_input("Ask a follow-up question or respond as the client:")
            if prompt:
                st.markdown(f'''
                    <div class=\"user-message\">\n                        <div class=\"message-content user-content\">{prompt}</div>\n                    </div>\n                ''', unsafe_allow_html=True)
                st.session_state.chat_history.append(("You", prompt))
                with st.spinner(" 🤔Thinking..."):
                    response_text = ""
                    response_container = st.empty()
                    ai_response = chat_ai(prompt)
                    for chunk in ai_response.split('. '):
                        if chunk.strip():
                            response_text += chunk.strip() + ('. ' if not chunk.strip().endswith('.') else ' ')
                            response_container.markdown(f'''
                                <div class=\"assistant-message\">\n       <div class=\"message-content assistant-content\">{response_text}</div>\n                            </div>\n                        ''', unsafe_allow_html=True)
                            time.sleep(0.01)
                    st.session_state.chat_history.append(("Usman Hassan (AI)", response_text.strip()))
             
if __name__ == "__main__":
    main()