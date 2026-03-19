from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("Points & Subscriptions Server")

API_BASE = "https://jsonplaceholder.typicode.com"

@mcp.tool()
def get_member(member_id : str) -> dict:
    """
    Fetch a loyalty member's profile by their ID.
    Use this when asked about a member's details or profile.
    """
    response = requests.get(f"{API_BASE}/users/{member_id}")

    if response.status_code == 200:
        data = response.json()

        return {
            "id": member_id,
            "name": data["name"],
            "email": data["email"],
            "username": data["username"],
            "phone": data["phone"],
            "company": data["company"]["name"]
        }
    else:
        return {"error": f"Member {member_id} not found"}

@mcp.tool()
def get_subscription(member_id : str) -> dict:
    """
    Fetch the current subscription plan for a loyalty member.
    Use this when asked about a member's plan, perks, or renewal date.
    """
    response = requests.get(f"{API_BASE}/todos?userId={member_id}")

    if response.status_code == 200:
        data = response.json()

        if not data:
            return {"error": f"No subscription found for member {member_id}"}

        subscription = data[0]
        return {
            "member_id": member_id,
            "plan": "Premium" if subscription["completed"] else "Basic",
            "status": "active",
            "subscription_title": subscription["title"],
            "billing_cycle": "yearly" if subscription["completed"] else "monthly",
            "next_billing_date": "2027-01-01" if subscription["completed"] else "2026-04-19",
            "end_date": "2027-01-01" if subscription["completed"] else "2026-04-19",
        }
    else:
        return {"error": f"Could not fetch subscription for member {member_id}"}

@mcp.tool()
def get_points_summary(member_id : str) -> dict:
    """
    Fetch the member's points activity for a loyalty member.
    Use this when asked about a member's activities.
    """

    response = requests.get(f"{API_BASE}/posts?userId={member_id}")
    if response.status_code == 200:
        activities = response.json()

        if len(activities) > 0:
            name = get_member(str(member_id))["name"]
            return       {
                "member_id": member_id,
                "name": name,
                "total_posts": len(activities),
                "points_balance": len(activities) * 100,
                "last_activity": activities[0]["title"]
              }
        else:
            return {"error": f"No activities found for member {member_id}"}
    else:
        return {"error": f"Could not fetch activities for member {member_id}"}

@mcp.tool()
def get_eligible_offers(member_id : str) -> dict:
    """
    Get all offers a member is eligible for based on their subscription plan.
    Premium members get 3 offers, Basic members get 1 offer.
    Use this when asked about promotions, deals or offers for a member.
    """
    is_premium = False
    offers = {}
    subscription = get_subscription(str(member_id))["plan"]

    if "error" in subscription:
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
        "member_id": member_id,
        "plan": subscription,
        "eligible_offers": offers
    }


if __name__ == "__main__":
    mcp.run()

