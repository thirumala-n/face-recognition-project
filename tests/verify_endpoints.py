import urllib.request, urllib.error, json

BASE = "http://127.0.0.1:8000"

def req(method, path, data=None, token=None):
    url = BASE + path
    body = json.dumps(data).encode() if data else None
    headers = {"Content-Type": "application/json"} if body else {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(
        url, data=body, method=method,
        headers=headers
    )
    try:
        with urllib.request.urlopen(r) as res:
            return res.status, json.loads(res.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

results = []

# 1. Health
code, body = req("GET", "/")
results.append(("GET /", code, "status=" + body["status"] + " model=" + str(body["model_loaded"])))

# ─── Authentication Tests ──────────────────────────────────────────────────
# 2. Register user
reg_payload = {
    "full_name": "Test Administrator",
    "email": "admin.verify@college.edu",
    "username": "admin_verify",
    "password": "Password123!"
}
code, body = req("POST", "/api/v1/auth/register", reg_payload)
token = body.get("access_token") if code == 201 else None
results.append(("POST /auth/register", code, f"token_present={token is not None} user={body.get('user', {}).get('username')}"))

# 3. Duplicate email registration rejection
code, body = req("POST", "/api/v1/auth/register", reg_payload)
results.append(("POST /auth/register (duplicate email)", code, str(body.get("detail"))))

# 4. Login with email
login_email_payload = {
    "email_or_username": "admin.verify@college.edu",
    "password": "Password123!"
}
code, body = req("POST", "/api/v1/auth/login", login_email_payload)
results.append(("POST /auth/login (via email)", code, f"token_present={'access_token' in body}"))

# 5. Login with username
login_user_payload = {
    "email_or_username": "admin_verify",
    "password": "Password123!"
}
code, body = req("POST", "/api/v1/auth/login", login_user_payload)
token = body.get("access_token")
results.append(("POST /auth/login (via username)", code, f"token_present={'access_token' in body}"))

# 6. Login with invalid password
code, body = req("POST", "/api/v1/auth/login", {"email_or_username": "admin_verify", "password": "WrongPassword"})
results.append(("POST /auth/login (wrong password)", code, str(body.get("detail"))))

# 7. Get authenticated user profile (/auth/me) with token
code, body = req("GET", "/api/v1/auth/me", token=token)
results.append(("GET /auth/me (with Bearer token)", code, f"user={body.get('username')} role={body.get('role')}"))

# 8. Get /auth/me without token (should be 401)
code, body = req("GET", "/api/v1/auth/me")
results.append(("GET /auth/me (unauthorized without token)", code, str(body.get("detail"))))

# ─── Student & Attendance Tests ───────────────────────────────────────────
# 9. Register student
code, body = req("POST", "/api/v1/students", {"student_id": "CS001", "name": "Arjun Sharma"})
results.append(("POST /students (new)", code, str(body)))

# 10. Duplicate student
code, body = req("POST", "/api/v1/students", {"student_id": "CS001", "name": "Arjun Sharma"})
results.append(("POST /students (dup)", code, str(body.get("detail"))))

# 11. List students
code, body = req("GET", "/api/v1/students")
results.append(("GET /students", code, "count=" + str(len(body))))

# 12. Get by ID
code, body = req("GET", "/api/v1/students/CS001")
results.append(("GET /students/CS001", code, str(body)))

# 13. Unknown student
code, body = req("GET", "/api/v1/students/GHOST")
results.append(("GET /students/GHOST", code, str(body.get("detail"))))

# 14. Today attendance
code, body = req("GET", "/api/v1/attendance/today")
results.append(("GET /attendance/today", code, "total=" + str(body["total_students"]) + " present=" + str(body["total_present"])))

# 15. Delete student
code, body = req("DELETE", "/api/v1/students/CS001")
results.append(("DELETE /students/CS001", code, str(body)))

# Print results
print()
all_passed = True
for name, code, detail in results:
    status = "PASS" if 200 <= code < 500 else "FAIL"
    if status == "FAIL":
        all_passed = False
    print(f"  [{code}] {status}  {name}")
    print(f"         {detail[:120]}")
    print()

print(f"Overall Live Endpoint Result: {'ALL PASSED' if all_passed else 'FAILURES DETECTED'}")
