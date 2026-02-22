"""Web Push: store subscriptions and send push notifications."""
import json
from config.settings import settings
from config.supabase_client import supabase


def is_push_available() -> bool:
    """Return True if VAPID keys are configured for Web Push."""
    return bool(settings.VAPID_PUBLIC_KEY and settings.VAPID_PRIVATE_KEY)


def save_subscription(userid: str, subscription: dict, user_agent: str = "") -> bool:
    """Store or upsert a push subscription for the user. Returns True on success."""
    endpoint = subscription.get("endpoint")
    keys = subscription.get("keys") or {}
    p256dh = keys.get("p256dh")
    auth = keys.get("auth")
    if not endpoint or not p256dh or not auth:
        return False
    try:
        # Delete existing subscription with same user+endpoint, then insert
        supabase.table("push_subscriptions").delete().eq("userid", userid).eq("endpoint", endpoint).execute()
        supabase.table("push_subscriptions").insert({
            "userid": userid,
            "endpoint": endpoint,
            "p256dh": p256dh,
            "auth": auth,
            "user_agent": user_agent or None,
        }).execute()
        return True
    except Exception:
        return False


def send_push_to_user(
    userid: str,
    title: str,
    body: str = "",
    data: dict | None = None,
) -> int:
    """
    Send Web Push to all subscriptions for the user.
    Returns the number of successfully sent pushes.
    """
    if not is_push_available():
        return 0
    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        return 0
    r = supabase.table("push_subscriptions").select("endpoint, p256dh, auth").eq("userid", userid).execute()
    subs = r.data or []
    sent = 0
    payload = json.dumps({"title": title, "body": body, **(data or {})})
    vapid_claims = {"sub": f"mailto:{settings.EMAIL_FROM}"} if settings.EMAIL_FROM else None
    for sub in subs:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub["endpoint"],
                    "keys": {"p256dh": sub["p256dh"], "auth": sub["auth"]},
                },
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims=vapid_claims,
            )
            sent += 1
        except WebPushException as e:
            if e.response and e.response.status_code in (404, 410):
                # Subscription expired, remove it
                try:
                    supabase.table("push_subscriptions").delete().eq("userid", userid).eq("endpoint", sub["endpoint"]).execute()
                except Exception:
                    pass
        except Exception:
            pass
    return sent
