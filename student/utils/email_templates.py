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
