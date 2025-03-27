import PyPDF2
import docx
import spacy
from django.core.mail import send_mail


def extract_text_from_resume(resume_path):
    """Extracts text from a PDF or DOCX resume file."""
    if resume_path.endswith('.pdf'):
        with open(resume_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            return "\n".join([page.extract_text() for page in reader.pages])
    
    elif resume_path.endswith('.docx'):
        doc = docx.Document(resume_path)
        return "\n".join([para.text for para in doc.paragraphs])

    return ""

nlp = spacy.load("en_core_web_sm")

def match_resume_to_job(resume_text, job_description):
    resume_doc = nlp(resume_text.lower())
    job_doc = nlp(job_description.lower())
    
    similarity = resume_doc.similarity(job_doc)
    return similarity  # Higher score means better match


def notify_applicant(application, sender_email):
    subject = "Application Status Update"
    message = f"Dear {application.applicant.get_full_name()},\n\nYour application for {application.job.title} has been {application.status}."

    send_mail(
        subject,
        message,
        sender_email,  # Logged-in employer's email as the sender
        [application.applicant.email],  # Corrected this line
        fail_silently=False,
    )

