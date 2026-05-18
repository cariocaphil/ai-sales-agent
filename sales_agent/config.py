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
GENERATING_STATUS = (
    "Generating drafts, running compliance review, and selecting the best email…"
)
COMPLIANCE_REJECTION_STATUS = (
    "Compliance review did not approve any draft. "
    "Adjust the product description and generate again."
)
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

EMAIL_OUTPUT_MIN_LENGTH = 30
EMAIL_OUTPUT_MAX_LENGTH = 4000
EXPLANATION_OUTPUT_MAX_LENGTH = 1000

OUTPUT_BANNED_PHRASES = (
    "ignore previous instructions",
    "as an ai",
    "as a language model",
    "guaranteed results",
    "100% success",
    "risk-free guarantee",
    "no risk guarantee",
    "act now or miss out",
    "limited time only",
)

OUTPUT_LEAKED_PROMPT_MARKERS = (
    "system prompt",
    "internal instructions",
    "agent names",
    "selection logic",
    "openai",
    "sales picker",
    "professional sales agent",
)

OUTPUT_PLACEHOLDER_PATTERNS = (
    r"\{[a-zA-Z_]+\}",
    r"<short explanation>",
    r"<full selected email>",
    r"<[^>]+>",
)

OUTPUT_VALIDATION_EMPTY_ERROR = (
    "The generated email could not be used because required content was missing. "
    "Please generate again."
)
OUTPUT_VALIDATION_EMAIL_LENGTH_ERROR = (
    "The selected email length is outside the allowed range. Please generate again."
)
OUTPUT_VALIDATION_EXPLANATION_LENGTH_ERROR = (
    "The selection explanation is too long. Please generate again."
)
OUTPUT_VALIDATION_BANNED_PHRASE_ERROR = (
    "The generated content contains language that is not allowed. "
    "Please generate again."
)
OUTPUT_VALIDATION_PLACEHOLDER_ERROR = (
    "The selected email still contains template placeholders. Please generate again."
)
OUTPUT_VALIDATION_LEAKAGE_ERROR = (
    "The generated content appears to include internal system text. "
    "Please generate again."
)

PRODUCT_CONTEXT_LINES = 4
DRAFT_LINES = 14
EXPLANATION_LINES = 4
STATUS_LINES = 2
