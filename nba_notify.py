import requests
import os
import json
from datetime import datetime, timedelta
from base64 import b64encode
from nacl import encoding, public

# ── 1. 내일 날짜 (한국시간 기준) ──────────────────────
tomorrow = (datetime.utcnow() + timedelta(hours=9)).strftime('%Y-%m-%d')

# ── 2. NBA 경기 조회 (ESPN API) ────────────────────────
try:
    res = requests.get(
        f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={tomorrow.replace('-', '')}",
        timeout=10
    )
    events = res.json().get("events", [])
except Exception as e:
    print(f"API 오류: {e}")
    events = []

# ── 3. 메시지 구성 ─────────────────────────────────────
if not events:
    text = f"🏀 내일 NBA 경기 없음 ({tomorrow} 한국시간)"
else:
    lines = [f"🏀 내일 NBA 경기 일정 ({tomorrow} 한국시간)"]
    for e in events:
        try:
            utc_str = e["date"][:16]
            utc_time = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M")
            kst_time = utc_time + timedelta(hours=9)
            teams = e["shortName"]
            lines.append(f"⏰ {kst_time.strftime('%H:%M')} | {teams}")
        except:
            continue
    text = " | ".join(lines)

# ── 4. 카카오 Access Token + 새 Refresh Token 갱신 ────
token_res = requests.post(
    "https://kauth.kakao.com/oauth/token",
    data={
        "grant_type": "refresh_token",
        "client_id": os.environ["KAKAO_REST_API_KEY"],
        "refresh_token": os.environ["KAKAO_REFRESH_TOKEN"],
    }
)
token_data = token_res.json()
access_token = token_data["access_token"]
new_refresh_token = token_data.get("refresh_token", os.environ["KAKAO_REFRESH_TOKEN"])
print("새 refresh_token 수신:", "Yes" if "refresh_token" in token_data else "No (기존 유지)")

# ── 5. GitHub Secret 자동 업데이트 ────────────────────
def update_github_secret(secret_name, secret_value):
    github_token = os.environ["GH_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]

    # 공개키 가져오기
    pub_key_res = requests.get(
        f"https://api.github.com/repos/{repo}/actions/secrets/public-key",
        headers={"Authorization": f"token {github_token}"}
    )
    pub_key_data = pub_key_res.json()
    pub_key = public.PublicKey(pub_key_data["key"].encode(), encoding.Base64Encoder())
    sealed_box = public.SealedBox(pub_key)
    encrypted = b64encode(sealed_box.encrypt(secret_value.encode())).decode()

    requests.put(
        f"https://api.github.com/repos/{repo}/actions/secrets/{secret_name}",
        headers={"Authorization": f"token {github_token}"},
        json={"encrypted_value": encrypted, "key_id": pub_key_data["key_id"]}
    )
    print(f"{secret_name} 업데이트 완료!")

update_github_secret("KAKAO_REFRESH_TOKEN", new_refresh_token)

# ── 6. 카카오톡 나에게 보내기 ─────────────────────────
template = {
    "object_type": "text",
    "text": text,
    "link": {"web_url": "https://www.nba.com"}
}
kakao_res = requests.post(
    "https://kapi.kakao.com/v2/api/talk/memo/default/send",
    headers={"Authorization": f"Bearer {access_token}"},
    data={"template_object": json.dumps(template)}
)
print("전송 완료!\n" + text)
print("카카오 응답:", kakao_res.status_code, kakao_res.text)
