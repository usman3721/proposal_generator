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
    Polite acknowledgment and thanks for the client's message
    A direct and thoughtful response to their question or comment
    Reference to the original proposal, as relevant.
    Dont make it too long.because it will be sent via Upwork.
    An offer to clarify further or move to the next step (e.g., a call, sharing more examples, starting the task)
    A professional and friendly closing
    📝 Tone & Style Requirements:
    Maintain a friendly, confident, and professional tone
    Provide technical clarity if the question involves tools, frameworks, or strategy
    Keep your response concise but complete
    If you don't know something, be honest but offer an alternative or next step
    Do not repeat the entire proposal, but build naturally on what was said
    ✅ Output Format:
    Return a complete client message with proper paragraph structure, no extra commentary, and ready to be sent via Upwork.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating chat response: {str(e)}"

def proposal_generator(job_post, company_name, client_name, uploaded_file, is_milestone, project_amount=None):
    resume_text = load_resume(uploaded_file)
    milestone_instructions = ""
    if is_milestone == "Yes":
        milestone_instructions = f"""
        \n\n---\n### Project Milestones\nPlease generate a milestone breakdown with:\n- Milestone description\n- Estimated completion date\n- Amount for each milestone\n- The total project budget is ${project_amount if project_amount else '[not specified]'}\nUse your expertise to suggest a logical breakdown.\n---\n"""
    prompt = f"""
    You are a top-rated Upwork freelancer and expert copywriter with a strong track record of winning high-value freelance jobs.\nYour goal is to craft a powerful, personalized proposal for the following opportunity using persuasive storytelling, credibility, and client-focused messaging.\n    Context:\n    - Job Post: {job_post}\n    - Company: {company_name if company_name else 'Not specified'}\n    - Client Name: {client_name if client_name else 'Hiring Manager'}\n    - My Background: {resume_text if resume_text else 'Will be customized based on relevant experience'}\n    {milestone_instructions}\n    - The proposal should always start after the greeting with: 'I am Usman Hassan.' For example: 'Hi {client_name if client_name else 'there'},\nI am Usman Hassan.'\n    📝 Proposal Structure:\n    Your response should follow this structure:\n    🔥 Hook / Introduction\n    Open with a powerful sentence that immediately shows understanding of the client's problem and goals.\n    ✅ Demonstrated Expertise\n    Share specific skills, projects, and experience relevant to the job (use bullet points sparingly for clarity).\n    🎯 Targeted Fit & Alignment\n    Address specific job requirements and how your expertise will solve them — mention tools, technologies, or strategies if relevant.\n    💡 Unique Value Proposition\n    Explain what sets you apart (e.g., turnaround time, visual storytelling skills, real-time collaboration, past results).\n    📞 Call to Action\n    End confidently with a clear invitation to discuss or next steps (\"Let's connect\", \"Open to a brief chat?\").\n        \n    Guidelines:\n    - Keep the tone professional yet conversational\n    - Focus on the client's needs and desired outcomes\n    - Highlight unique selling points\n    - Include specific examples of relevant past work\n    - Maintain a confident but not arrogant tone\n    - Must be original, highly specific, and tailored to the job\n    - Avoid any vague or templated language\n    - Include brief examples or links if relevant to add credibility\n    -Include brief examples or links if relevant to add credibility\n    -Ensure the tone is confident, never arrogant\n    - Make it personalized and avoid generic templates\n    - A light P.S. for extra warmth\n    \n    📬 Output Format:\n    - Return a fully written proposal formatted with paragraph breaks, readable on all devices. Do not include commentary, headers, or instructions — only the proposal body.\n    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating proposal: {str(e)}"

def cold_email_generator(job_post, company_name, client_name, uploaded_file, is_milestone, project_amount=None):
    resume_text = load_resume(uploaded_file)
    milestone_instructions = ""
    if is_milestone == "Yes":
        milestone_instructions = f"""
        \n\n---\n### Project Milestones\nBriefly mention in your follow-up email that you can provide a milestone plan and are happy to discuss it.\n- The total project budget is ${project_amount if project_amount else '[not specified]'}\n---\n"""
    prompt = f"""
   You are an expert B2B email copywriter with proven experience crafting high-converting, concise, and personalized follow-up emails.\n    Objective: Write a polished, professional follow-up email to a potential client after submitting a proposal for the following freelance opportunity on Upwork.\n    Context:\n    - Job/Opportunity Details: {job_post}\n    - Target Company: {company_name if company_name else 'Not specified'}\n    - Client's Name: {client_name if client_name else 'Hiring Manager'}\n    - My Background: {resume_text if resume_text else 'Will be customized based on relevant experience'}\n    {milestone_instructions}\n    Please create a complete follow-up email that includes:\n    1. A polite,Warm personalized greeting\n    2. A brief and quick reference to the original proposal and job post\n    3. A short, value-focused reminder of why I'm a great fit.Also gentle question or CTA to invite response (e.g., \"Would you like to connect for a quick chat?\")\n    4. A gentle nudge or question to encourage a response (e.g., \"Do you have any questions?\" or \"Would you like to discuss further?\")\n    5. A professional closing and signature\n    Email Guidelines:\n    - Be polite, professional, and respectful of the client's time\n    - Avoid sounding pushy or desperate\n    - Use natural language — not overly formal or robotic\n    - Avoid any tone that feels salesy, desperate, or intrusive\n    - Ensure clear formatting, mobile readability, and zero grammatical or spelling issues\n    - Personalization is key — reflect awareness of the project/client needs.\n    - A light P.S. for extra warmth\n    \n    Return a fully written follow-up email, formatted and ready to send, with no additional explanations. Use paragraph breaks for clarity.\n    """
    try:
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
    content_type = st.sidebar.selectbox('What would you like to generate?:', ['📝 Killing Proposal', '✉️ Highly Converting Email Content'], key='level')

    # Milestone selection
    is_milestone = st.sidebar.radio("Is this project based on milestones?", ("No", "Yes"))
    project_amount = None
    if is_milestone == "Yes":
        project_amount = st.sidebar.number_input("Total Project Amount ($)", min_value=1.0, step=1.0, format="%.2f")

    # Display tips based on selection
    # display_conversion_tips()

    # Inputs
    col1, col2 = st.columns(2)

    job_post = st.sidebar.text_area(" 📋Job Post", height=100)
    about_company=st.sidebar.text_area(" ℹ️ Company Information" , height=100)

    client_name = st.sidebar.text_input(" 👤 Client or Job Poster Name")
    company_name = st.sidebar.text_input(" 🏢 Company Name (if known)")
    uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF)", type="pdf")

    # Generate Button
    if st.sidebar.button("✨ Generate", type="primary"):
        if content_type == '📝 Killing Proposal':
            response = proposal_generator(job_post, company_name, client_name, uploaded_file, is_milestone, project_amount)
            st.session_state.generated_content = response
            st.session_state.generated_type = 'Proposal'
        else:
            response = cold_email_generator(job_post, company_name, client_name, uploaded_file, is_milestone, project_amount)
            st.session_state.generated_content = response
            st.session_state.generated_type = 'Cold Email'

        # Add to history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.history.append({
            "type": content_type,
            "content": response,
            "timestamp": timestamp
        })

    # --- Two-column layout for proposal/email and chat ---
    with col1:
        if 'generated_content' in st.session_state:
            st.markdown(f"### Your Generated {st.session_state.get('generated_type', 'Content')}")
            with st.container(border=True, height=660):
                # Split milestone section if present
                content = st.session_state.generated_content
                if '### Project Milestones' in content:
                    main_part, milestone_part = content.split('### Project Milestones', 1)
                    st.write(main_part.strip())
                    with st.expander('Project Milestones'):
                        milestone_text = '### Project Milestones' + milestone_part
                        # Try to render as markdown table if present
                        if '|' in milestone_text and '-' in milestone_text:
                            st.markdown(milestone_text, unsafe_allow_html=True)
                        else:
                            st.write(milestone_text)
                else:
                    st.write(content)

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
            # Place chat input directly below the chat container
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
                            time.sleep(0.003)
                    st.session_state.chat_history.append(("Usman Hassan (AI)", response_text.strip()))

if __name__ == "__main__":
    main()