from config.supabase_client import supabase


def create_team(team_name: str, mentor_userid: str) -> dict:
    """Mentor: Create student team."""
    result = supabase.table("teams").insert({"team_name": team_name, "mentor_userid": mentor_userid}).execute()

    if not result.data:
        return {"success": False, "message": "Failed to create team"}
    return {"success": True, "message": "Team created", "team": result.data[0]}


def get_mentor_teams(mentor_userid: str) -> dict:
    """Mentor: Get my teams."""
    result = supabase.table("teams").select("*").eq("mentor_userid", mentor_userid).execute()
    return {"success": True, "teams": result.data or []}


def add_student_to_team(teamid: str, student_userid: str) -> dict:
    """Mentor: Add student to team."""
    user_check = supabase.table("users").select("role").eq("userid", student_userid).execute()
    if not user_check.data or user_check.data[0].get("role") != "student":
        return {"success": False, "message": "Invalid student"}

    # Check if already in team
    existing = supabase.table("team_members").select("*").eq("teamid", teamid).eq("student_userid", student_userid).execute()
    if existing.data:
        return {"success": False, "message": "Student already in team"}

    result = supabase.table("team_members").insert({"teamid": teamid, "student_userid": student_userid}).execute()

    if not result.data:
        return {"success": False, "message": "Failed to add student"}
    return {"success": True, "message": "Student added to team", "member": result.data[0]}


def get_team_members(teamid: str) -> dict:
    """Get all students in a team."""
    result = supabase.table("team_members").select("*").eq("teamid", teamid).execute()
    return {"success": True, "members": result.data or []}


def remove_student_from_team(teamid: str, student_userid: str) -> dict:
    """Mentor: Remove student from team."""
    result = supabase.table("team_members").delete().eq("teamid", teamid).eq("student_userid", student_userid).execute()
    return {"success": True, "message": "Student removed from team"}


def delete_team(teamid: str) -> dict:
    """Mentor: Delete team."""
    result = supabase.table("teams").delete().eq("teamid", teamid).execute()
    return {"success": True, "message": "Team deleted"}
