from fastapi.testclient import TestClient
from app.main import app  # run: DATABASE_URL=sqlite:///./test.db python seed.py first

c = TestClient(app)

def login(email, pw):
    r = c.post("/auth/login", data={"username": email, "password": pw})
    return r

assert login("admin@example.com", "wrong").status_code == 401
adm = login("admin@example.com", "Admin@1234").json()
emp = login("employee@example.com", "Employee@1234").json()
ah = {"Authorization": f"Bearer {adm['access_token']}"}
eh = {"Authorization": f"Bearer {emp['access_token']}"}
print("login ok:", adm["role"], emp["role"])

assert c.get("/users/me", headers=eh).json()["email"] == "employee@example.com"
assert c.get("/users").status_code == 401
assert c.get("/users", headers=eh).status_code == 403
assert c.get("/users", headers=ah).status_code == 200
print("role protection ok")

r = c.post("/users", headers=ah, json={"full_name": "New Person", "email": "new@example.com", "password": "Password@1"})
assert r.status_code == 201, r.text
assert c.post("/users", headers=ah, json={"full_name": "New Person", "email": "NEW@example.com", "password": "Password@1"}).status_code == 409
print("create user ok")

assert c.post("/attendance/check-out", headers=eh).status_code == 400
r = c.post("/attendance/check-in", headers=eh); assert r.status_code == 201, r.text
print("check-in:", r.json()["status"], r.json()["check_in"])
assert c.post("/attendance/check-in", headers=eh).status_code == 400
r = c.post("/attendance/check-out", headers=eh); assert r.status_code == 200, r.text
print("check-out hours:", r.json()["hours_worked"])
assert c.post("/attendance/check-out", headers=eh).status_code == 400

me = c.get("/attendance/me", headers=eh).json(); assert len(me) == 1
assert c.get("/attendance", headers=eh).status_code == 403
allr = c.get("/attendance", headers=ah).json(); assert len(allr) == 1
print("duplicate prevention, history, admin view ok")

assert c.patch("/users/3/deactivate", headers=ah).status_code == 200
assert login("new@example.com", "Password@1").status_code == 403
print("ALL TESTS PASSED")
