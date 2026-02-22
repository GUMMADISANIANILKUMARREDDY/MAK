"""
Email templates for registration, welcome, and OTP emails.
Company-style, professional format. Use same logic for all transactional emails.
"""

# App/company name used in emails
APP_NAME = "InternHub"


def get_registration_otp_plain(to_email: str, otp: str, otp_expire_minutes: int) -> str:
    """Plain-text body for registration OTP email (welcome as student + OTP)."""
    return f"""
Welcome to {APP_NAME}

Hello,

Thank you for registering as a student on {APP_NAME}. We're glad to have you.

To complete your registration, please use the One-Time Password (OTP) below:

    OTP: {otp}

This code is valid for {otp_expire_minutes} minutes. Do not share it with anyone.

If you did not request this registration, please ignore this email.

Best regards,
The {APP_NAME} Team
""".strip()


def get_registration_otp_html(to_email: str, otp: str, otp_expire_minutes: int) -> str:
    """HTML body for registration OTP email (company-style welcome as student + OTP)."""
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Verify your email - {APP_NAME}</title>
</head>
<body style="margin:0; padding:0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f5;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f4f4f5; padding: 24px;">
    <tr>
      <td align="center">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
          <tr>
            <td style="padding: 32px 40px;">
              <h1 style="margin: 0 0 8px 0; font-size: 22px; color: #111827;">Welcome to {APP_NAME}</h1>
              <p style="margin: 0; font-size: 14px; color: #6b7280;">Student Registration</p>
            </td>
          </tr>
          <tr>
            <td style="padding: 0 40px 24px 40px;">
              <p style="margin: 0 0 16px 0; font-size: 15px; line-height: 1.6; color: #374151;">
                Hello,
              </p>
              <p style="margin: 0 0 20px 0; font-size: 15px; line-height: 1.6; color: #374151;">
                Thank you for registering as a <strong>student</strong> on {APP_NAME}. We're glad to have you on board.
              </p>
              <p style="margin: 0 0 12px 0; font-size: 15px; line-height: 1.6; color: #374151;">
                To complete your registration, use the One-Time Password (OTP) below:
              </p>
              <div style="background-color: #f0f9ff; border: 1px solid #bae6fd; border-radius: 6px; padding: 16px 20px; margin: 16px 0;">
                <p style="margin: 0; font-size: 13px; color: #0369a1;">Your OTP</p>
                <p style="margin: 4px 0 0 0; font-size: 24px; font-weight: 600; letter-spacing: 4px; color: #0c4a6e;">{otp}</p>
              </div>
              <p style="margin: 16px 0 0 0; font-size: 14px; color: #6b7280;">
                This code is valid for <strong>{otp_expire_minutes} minutes</strong>. Do not share it with anyone.
              </p>
              <p style="margin: 24px 0 0 0; font-size: 14px; color: #6b7280;">
                If you did not request this registration, please ignore this email.
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding: 24px 40px; border-top: 1px solid #e5e7eb;">
              <p style="margin: 0; font-size: 13px; color: #9ca3af;">
                Best regards,<br>
                The {APP_NAME} Team
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
""".strip()


def get_registration_otp_subject() -> str:
    """Subject line for registration OTP email."""
    return f"Verify your email – Welcome to {APP_NAME}"


def get_password_reset_otp_plain(otp: str, otp_expire_minutes: int) -> str:
    """Plain-text body for password reset OTP."""
    return f"""
Password reset – {APP_NAME}

Use this OTP to reset your password:

    OTP: {otp}

Valid for {otp_expire_minutes} minutes. If you did not request this, ignore this email.

The {APP_NAME} Team
""".strip()


def get_password_reset_otp_subject() -> str:
    return f"Password reset – {APP_NAME}"


# --- Notification / activity emails ---

def get_task_assigned_subject() -> str:
    return f"New task assigned – {APP_NAME}"


def get_task_assigned_plain(task_title: str, link: str = "") -> str:
    body = f"You have been assigned a new task: {task_title}."
    if link:
        body += f"\n\nView task: {link}"
    return f"{APP_NAME}\n\n{body}\n\nBest regards,\nThe {APP_NAME} Team"


def get_task_status_changed_subject() -> str:
    return f"Task status updated – {APP_NAME}"


def get_task_status_changed_plain(task_title: str, status: str, link: str = "") -> str:
    body = f"Task \"{task_title}\" status: {status}."
    if link:
        body += f"\n\nView: {link}"
    return f"{APP_NAME}\n\n{body}\n\nBest regards,\nThe {APP_NAME} Team"


def get_deadline_approaching_subject() -> str:
    return f"Deadline approaching – {APP_NAME}"


def get_deadline_approaching_plain(task_title: str, due_date: str, link: str = "") -> str:
    body = f"Task \"{task_title}\" is due on {due_date}. Please complete or submit for review."
    if link:
        body += f"\n\nView task: {link}"
    return f"{APP_NAME}\n\n{body}\n\nBest regards,\nThe {APP_NAME} Team"


def get_task_reviewed_subject(approved: bool) -> str:
    return f"Task {'approved' if approved else 'needs changes'} – {APP_NAME}"


def get_task_reviewed_plain(task_title: str, approved: bool, feedback: str = "", link: str = "") -> str:
    result = "approved" if approved else "returned for changes"
    body = f"Your submission for task \"{task_title}\" has been {result}."
    if feedback:
        body += f"\n\nFeedback: {feedback}"
    if link:
        body += f"\n\nView task: {link}"
    return f"{APP_NAME}\n\n{body}\n\nBest regards,\nThe {APP_NAME} Team"


def get_student_added_to_team_subject() -> str:
    return f"Added to a team – {APP_NAME}"


def get_student_added_to_team_plain(team_name: str, link: str = "") -> str:
    body = f"You have been added to team: {team_name}."
    if link:
        body += f"\n\nView: {link}"
    return f"{APP_NAME}\n\n{body}\n\nBest regards,\nThe {APP_NAME} Team"


def get_mentor_assigned_subject() -> str:
    return f"Module assigned to you – {APP_NAME}"


def get_mentor_assigned_plain(module_title: str, link: str = "") -> str:
    body = f"You have been assigned as mentor to module: {module_title}."
    if link:
        body += f"\n\nView: {link}"
    return f"{APP_NAME}\n\n{body}\n\nBest regards,\nThe {APP_NAME} Team"


def get_chat_message_subject(sender_username: str) -> str:
    return f"New message from {sender_username} – {APP_NAME}"


def get_chat_message_plain(sender_username: str, message_preview: str, link: str = "") -> str:
    preview = (message_preview or "")[:200] + ("..." if len(message_preview or "") > 200 else "")
    body = f"{sender_username} sent you a message:\n\n\"{preview}\""
    if link:
        body += f"\n\nOpen chat: {link}"
    return f"{APP_NAME}\n\n{body}\n\nBest regards,\nThe {APP_NAME} Team"
