import re
import sys
from bs4 import BeautifulSoup
import requests
import re


URL = "https://<your's instance>"
SIGN_IN_URL = "https://<your's instance>/users/sign_in"
LOGIN_URL = "https://<your's instance>/users/auth/ldapmain/callback"
USERNAME = "LDAP username"
PASSWORD = "paswword"
ACCESS_TOKEN_NAME = "test"
ACCESS_TOKEN_SCOPE = "read_repository"

session = requests.Session()

sign_in_page = str(session.get(SIGN_IN_URL).content)

for l in sign_in_page.split("\n"):
    m = re.search('name="authenticity_token" value="([^"]+)"', l)
    if m:
        break

token = None
if m:
    token = m.group(1)

if not token:
    print("Unable to find the authenticity token")
    sys.exit(1)

data = {"username": USERNAME, "password": PASSWORD, "authenticity_token": token}
r = session.post(LOGIN_URL, data=data)
if r.status_code != 200:
    print("Failed to log in")
    sys.exit(1)


page_tokens = session.get("/".join((URL, "-/profile/personal_access_tokens")))
private_token = None
if page_tokens.ok:
    root = BeautifulSoup(page_tokens.text, "html5lib")
    token = root.find_all("meta", attrs={"name": "csrf-token"})[0]["content"]
else:
    print("something went wrong (tjrs rever de mettre un log comme ca)")
    sys.exit(1)

present_token = root.find_all(
    "div", attrs={"data-access-token-type": "personal access token"}
)[1]["data-initial-active-access-tokens"]
if re.search(ACCESS_TOKEN_NAME, present_token):
    print(f"token: {ACCESS_TOKEN_NAME} exist")
    sys.exit(0)

body = {
    "personal_access_token[name]": ACCESS_TOKEN_NAME,
    "personal_access_token[scopes][]": ACCESS_TOKEN_SCOPE,
    "authenticity_token": token,
}

response = session.post("/".join((URL, "-/profile/personal_access_tokens")), data=body)

if response.ok:
    private_token = response.json()["new_token"]
    print(f"Personnal_acces_token as created: {private_token}")

if not private_token:
    print("something went wrong (tjrs rever de mettre un log comme ca)")
    sys.exit(1)
