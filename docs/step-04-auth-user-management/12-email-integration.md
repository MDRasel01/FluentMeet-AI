# Email Service Integration

## 1. Provider-Independent Architecture
FluentMeet AI utilizes an abstract `BaseEmailProvider` interface so that underlying email dispatch infrastructure (e.g., Resend, Postmark, Amazon SES, or SendGrid) can be changed or mocked without modifying business authentication logic.

```python
class BaseEmailProvider(ABC):
    @abstractmethod
    async def send_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        pass
```

## 2. Integrated Email Templates
- **Verify Email:** Dispatches 30-minute verification token link upon registration or manual resend request.
- **Password Reset:** Dispatches 30-minute password reset link with instructions to secure the account if not requested by the user.
- **Password Changed Alert:** Immediate security notification sent when account credentials change.
- **Organization Invitation:** 7-day invitation link containing organization name, inviter name, and assigned role.
- **Role Changed Alert:** Notifies user when an organization administrator promotes or adjusts their role.
- **Account Deactivated Confirmation:** Confirmation notice upon user-initiated account deactivation.

