from mcp.server.fastmcp import FastMCP
import requests
import jwt
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

mcp = FastMCP("Points & Subscriptions Server v2")

API_BASE = "https://jsonplaceholder.typicode.com"

MOCK_USERS = {
    "steven": {
        "password": "points123",
        "role": "admin"
    },
    "alice": {
        "password": "alice123",
        "role": "user"
    },
    "bob": {
        "password": "bob123",
        "role": "user"
    }
}

@mcp.tool()
def login(username : str, password : str) -> dict:
    """
    Login with username and password to get a JWT token.
    Always call this first before calling any other tool.
    Use this when the user wants to authenticate or login.
    """

    user = MOCK_USERS.get(username)
    if not user:
        return {"error": "Invalid username or password"}

    if user["password"] != password:
        return {"error": "Invalid username or password"}

    payload = {
        "username": username,
        "role": user["role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return {
        "success": True,
        "token": token,
        "username": username,
        "role": user["role"],
        "expires_in": "30 minutes"
    }

def verify_token(token: str) -> dict:
    """
    Internal helper — verifies a JWT token.
    Returns the decoded payload if valid, error if not.
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        return {"valid": True, "payload": payload}

    except jwt.ExpiredSignatureError:
        return {"valid": False, "error": "Token has expired. Please login again."}

    except jwt.InvalidTokenError:
        return {"valid": False, "error": "Invalid token. Please login again."}

@mcp.tool()
def get_member(member_id : str, token: str) -> dict:
    """
    Fetch a loyalty member's profile by their ID.
    Use this when asked about a member's details or profile.
    """

    result = verify_token(token)

    if not result["valid"]:
        return {"error": result["error"]}

    payload = result["payload"]
    response = requests.get(f"{API_BASE}/users/{member_id}")

    if response.status_code == 200:
        data = response.json()

        return {
            "role": payload["role"],
            "requested_by": payload["username"],
            "member": {
                "id": member_id,
                "name": data["name"],
                "email": data["email"],
                "username": data["username"],
                "phone": data["phone"],
                "company": data["company"]["name"],
            }
        }
    else:
        return {"error": f"Member {member_id} not found"}

@mcp.tool()
def get_subscription(member_id : str, token: str) -> dict:
    """
    Fetch the current subscription plan for a loyalty member.
    Use this when asked about a member's plan, perks, or renewal date.
    """

    result = verify_token(token)

    if not result["valid"]:
        return {"error": result["error"]}

    payload = result["payload"]
    response = requests.get(f"{API_BASE}/todos?userId={member_id}")

    if response.status_code == 200:
        data = response.json()

        if not data:
            return {"error": f"No subscription found for member {member_id}"}

        subscription = data[0]
        return {
            "role": payload["role"],
            "requested_by": payload["username"],
            "member": {
                "member_id": member_id,
                "plan": "Premium" if subscription["completed"] else "Basic",
                "status": "active",
                "subscription_title": subscription["title"],
                "billing_cycle": "yearly" if subscription["completed"] else "monthly",
                "next_billing_date": "2027-01-01" if subscription["completed"] else "2026-04-19",
                "end_date": "2027-01-01" if subscription["completed"] else "2026-04-19"
            }
        }
    else:
        return {"error": f"Could not fetch subscription for member {member_id}"}

@mcp.tool()
def get_points_summary(member_id : str, token: str) -> dict:
    """
    Fetch the member's points activity for a loyalty member.
    Use this when asked about a member's activities.
    """
    result = verify_token(token)

    if not result["valid"]:
        return {"error": result["error"]}

    payload = result["payload"]
    response = requests.get(f"{API_BASE}/posts?userId={member_id}")
    if response.status_code == 200:
        activities = response.json()

        if len(activities) > 0:
            name = requests.get(f"{API_BASE}/users/{member_id}").json()["name"]
            return{
                "role": payload["role"],
                "requested_by": payload["username"],
                "member": {
                    "member_id": member_id,
                    "name": name,
                    "total_posts": len(activities),
                    "points_balance": len(activities) * 100,
                    "last_activity": activities[0]["title"]
                }
              }
        else:
            return {"error": f"No activities found for member {member_id}"}
    else:
        return {"error": f"Could not fetch activities for member {member_id}"}

@mcp.tool()
def get_eligible_offers(member_id: str, token: str) -> dict:
    """
    Get all offers a member is eligible for based on their subscription plan.
    Premium members get 3 offers, Basic members get 1 offer.
    Use this when asked about promotions, deals or offers for a member.
    """

    result = verify_token(token)

    if not result["valid"]:
        return {"error": result["error"]}

    payload = result["payload"]
    is_premium = False
    offers = {}
    subscription = get_subscription(str(member_id), token)["member"]["plan"]

    if not subscription or "error" in str(subscription):
        return {"error": f"No Eligible offers found for member {member_id}"}

    is_premium = True if subscription.lower() == "premium" else False

    if is_premium:
        offers = {
            "offer1" : "www.offerurl.com",
            "offer2" : "www.offerurl.com",
            "offer3" : "www.offerurl.com"
        }
    else:
        offers = {
            "offer1" : "www.offerurl.com"
        }

    return {
        "role": payload["role"],
        "requested_by": payload["username"],
        "member": {
            "member_id": member_id,
            "plan": subscription,
            "eligible_offers": offers
        }
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
