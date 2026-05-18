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

STEP1_READY_STATUS = (
    "Step 1: Fill in the details below, then generate and review drafts."
)
GENERATING_STATUS = "Generating drafts and selecting the best email…"
EMAIL_GENERATED_STATUS = (
    "Step 1 complete. Review the selected email, then confirm sending in Step 2."
)
NO_EMAIL_TO_SEND_STATUS = (
    "Step 2 unavailable: generate and review an email in Step 1 first."
)
INPUTS_CHANGED_STATUS = (
    "Inputs changed. Complete Step 1 again before sending."
)
SEND_COMPLETE_STATUS = (
    "Step 2 complete. Email sent to {receiver}. "
    "Run Step 1 again to generate a new email."
)

GENERATION_FAILED_STATUS = "Failed to generate emails: {error}"
SEND_FAILED_STATUS = "Failed to send email: {error}"
MISSING_INPUT_STATUS = "Please provide: {fields}"

PRODUCT_CONTEXT_MAX_LENGTH = 2000
PRODUCT_CONTEXT_EMPTY_ERROR = (
    "Please enter a product or service description."
)
PRODUCT_CONTEXT_TOO_LONG_ERROR = (
    "Product description must be {max_length} characters or fewer "
    "(you entered {length})."
)
PRODUCT_CONTEXT_INSTRUCTION_LIKE_ERROR = (
    "Product description must describe your product or service only, "
    "not instructions for the AI."
)

PRODUCT_CONTEXT_LINES = 4
DRAFT_LINES = 14
EXPLANATION_LINES = 4
STATUS_LINES = 2
