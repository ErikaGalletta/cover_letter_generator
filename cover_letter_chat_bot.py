import streamlit as st

# For AI model
from google import genai
import fitz
import os

# For PDF creation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import textwrap
import io

# Define the Google credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "chatbot-credentials.json"
os.environ["GOOGLE_CLOUD_PROJECT"] = (
    "chatbotcoverletter"  # Replace with your project ID
)
os.environ["GOOGLE_CLOUD_LOCATION"] = "europe-west3"

# system prompt definition
system_prompt = """
You are an AI assistant trained to write a cover letter for job applications. 
The candidate has submitted their resume, and the task is to create a coherent and personalized cover letter that aligns with the job description. 
The letter should highlight the candidate's relevant skills, experiences, and background in relation to the job requirements. 
It should comprise three paragraphs: in the first you highlight why the position is relevant for the candidate, 
in the second you summarize the candidate's experiences and background and then in the last one you present the candidate personal goals, if any.
"""


# Extract data from PDF resume
def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(uploaded_file)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text


# Initialize the GenAI client
client = genai.Client(vertexai=True)


# Streamlit app UI
st.title("Cover Letter Generator")
st.write(
    "Paste the job description and upload your resume PDF to generate a cover letter. Please scrub your resume from sensitive information such as your name and contact details"
)

# Job description input
job_description = st.text_area("Job Description", height=200)

# Resume file uploader
resume_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

# initialize the chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def generate_cover_letter():
    # Extract text from the uploaded resume PDF
    resume_text = extract_text_from_pdf(resume_file)

    # Construct the human prompt
    prompt = f"""Given the following resume: {resume_text} and the following job description: {job_description}, 
    write a cover letter for the candidate coherent with their experiences, background, and skills and aligned with the job posting.
    Do not invent extra information but go into detail. The cover letter should be a page long. 
    If you think the job posting does not match the resume you are passed, reply with 'The job description is not aligned with the candidate's resume': 
    for example, do not write the cover letter if the area of interest of the candidate, their experiences, and background are not aligned with the role and the company's function
    """

    # Send the prompt to the GenAI model
    chat = client.chats.create(model="gemini-1.0-pro-002")
    response = chat.send_message(system_prompt + prompt)

    # Store the result in chat history
    st.session_state.chat_history.append(
        {"role": "assistant", "message": response.text}
    )


# Function to generate PDF from the cover letter
def create_pdf(cover_letter_text):
    # Create a file-like buffer to hold the PDF data
    buffer = io.BytesIO()

    # Create the canvas object
    c = canvas.Canvas(buffer, pagesize=letter)

    # Draw a lilac bar at the top of the page
    c.setFillColor(colors.lightskyblue)  # light blue color
    c.rect(0, 746, 612, 30, fill=1)  # Draw a rectangle at the top

    # Title of the document
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.black)  # Set text color to black
    c.drawString(72, 755, "Cover Letter - [Candidate name] - [Company]")

    # Set font for the letter content
    c.setFont("Helvetica", 10)

    # Split the cover letter into paragraphs
    paragraphs = cover_letter_text.split("\n")

    # Set up text wrapping
    wrapper = textwrap.TextWrapper(width=105)  # 105 characters per line

    # Initialize vertical position for text placement
    y_position = 720
    for paragraph in paragraphs:
        if paragraph.strip():  # Only process non-empty paragraphs
            lines = wrapper.wrap(text=paragraph)  # Wrap text into lines
            for line in lines:
                if (
                    y_position <= 100
                ):  # If the text goes beyond the page, create a new page
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y_position = 750
                c.drawString(72, y_position, line)
                y_position -= 14  # Adjust line spacing
            y_position -= 12  # Add extra space between paragraphs

    # Save the canvas to the buffer
    c.showPage()
    c.save()

    # Move the buffer position to the beginning
    buffer.seek(0)

    return buffer


# Process the input when the button is pressed
if st.button("Generate Cover Letter"):

    # Check if both inputs are provided
    if job_description and resume_file:
        # Generate the cover letter
        generate_cover_letter()

        # Display the cover letter response
        st.subheader("Generated Cover Letter:")
        st.write(st.session_state.chat_history[-1]["message"])

        # Ask for further questions
        st.write(
            "Feel free to ask any questions or request changes to the cover letter."
        )
    else:
        st.error("Please make sure both job description and resume are provided.")

if st.session_state.chat_history:
    cover_letter_text = st.session_state.chat_history[-1]["message"]
    pdf_buffer = create_pdf(cover_letter_text)

    # Provide download link
    st.download_button(
        label="Download Cover Letter as PDF",
        data=pdf_buffer,
        file_name="cover_letter.pdf",
        mime="application/pdf",
    )
    # If further questions are asked, the chat history is shown to the user
    if len(st.session_state.chat_history) > 1:

        # Display the previous conversation (chat history)
        for chat_message in st.session_state.chat_history[
            1:
        ]:  # avoid showing the initial letter twice

            if chat_message["role"] == "assistant":
                st.markdown(f"**Assistant:** {chat_message['message']}")
            elif chat_message["role"] == "user":
                st.markdown(f"**You:** {chat_message['message']}")

    # Allow user to ask further questions or give instructions
    user_message = st.text_input(
        "Your question or request (e.g., Modify the letter or ask a question):"
    )

    if user_message:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "message": user_message})

        # Send the user message to the model and get a response
        chat = client.chats.create(model="gemini-1.0-pro-002")
        assistant_response = chat.send_message(user_message)

        # Add assistant's response to chat history
        st.session_state.chat_history.append(
            {"role": "assistant", "message": assistant_response.text}
        )

        # Display the assistant's response
        st.markdown(f"**Assistant:** {assistant_response.text}")
