from dotenv import load_dotenv

load_dotenv()

APP_TITLE = "AI Sales Agent"

RECEIVER_EMAIL_CHOICES = ["cariocaphil@gmail.com"]
DEFAULT_RECEIVER_EMAIL = RECEIVER_EMAIL_CHOICES[0]

DEFAULT_RECIPIENT_TITLE = "Dear Product Leader"

DEFAULT_PRODUCT_CONTEXT = (
    "SynthPilot helps software teams analyze user feedback, "
    "detect product pain points, and generate prioritized "
    "feature recommendations."
)

EMAIL_GENERATED_STATUS = (
    "Email generated and selected. Review it, then click Send Selected Email."
)
NO_EMAIL_TO_SEND_STATUS = "No selected email to send yet. Generate emails first."

GENERATION_FAILED_STATUS = "Failed to generate emails: {error}"
SEND_FAILED_STATUS = "Failed to send email: {error}"
MISSING_INPUT_STATUS = "Please provide: {fields}"

PRODUCT_CONTEXT_LINES = 4
DRAFT_LINES = 14
EXPLANATION_LINES = 4
STATUS_LINES = 2
