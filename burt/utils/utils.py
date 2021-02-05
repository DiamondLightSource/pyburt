import pwd
import os


def get_user_details():
    username = "unknown"
    full_name = ""
    uid = os.getuid()
    gid = "unknown"

    try:
        pw_entry = pwd.getpwuid(os.getuid())
        username = pw_entry.pw_name
        full_name = pw_entry.pw_gecos
        gid = pw_entry.pw_gid
    except KeyError:
        if "GITLAB_USER_LOGIN" in os.environ:
            username = os.environ["GITLAB_USER_LOGIN"]
        elif "USER" in os.environ:
            username = os.environ["USER"]

    if full_name:
        username = f"{username} ({full_name})"
    return username, uid, gid
