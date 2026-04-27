import requests
import os
from datetime import datetime, timedelta

# ── 1. 내일 날짜 (한국시간 기준) ──────────────────────
tomorrow = (datetime.utcnow() + timedelta(hours=9, days=1)).strftime('%Y-%m-%d')

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
    lines = [f"🏀 내일 NBA 경기 일정 ({tomorrow} 한국시간)\n"]
    for e in events:
        try:
            utc_str = e["date"][:16]
            utc_time = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M")
            kst_time = utc_time + timedelta(hours=9)
            teams = e["shortName"]
            lines.append(f"⏰ {kst_time.strftime('%H:%M')} | {teams}")
        except:
            continue
    text = "\n".join(lines)

# ── 4. 카카오 Access Token 갱신 ───────────────────────
token_res = requests.post(
    "https://kauth.kakao.com/oauth/token",
    data={
        "grant_type": "refresh_token",
        "client_id": os.environ["KAKAO_REST_API_KEY"],
        "refresh_token": os.environ["KAKAO_REFRESH_TOKEN"],
    }
)
access_token = token_res.json()["access_token"]

# ── 5. 카카오톡 나에게 보내기 ─────────────────────────
kakao_res = requests.post(
    "https://kapi.kakao.com/v2/api/talk/memo/default/send",
    headers={"Authorization": f"Bearer {access_token}"},
    data={
        "template_object": f'{{"object_type":"text","text":"{text}","link":{{"web_url":"https://www.nba.com"}}}}'
    }
)
print("전송 완료!\n" + text)
print("카카오 응답:", kakao_res.status_code, kakao_res.text)
