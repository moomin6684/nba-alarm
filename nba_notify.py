import requests
import os
from datetime import datetime, timedelta

# ── 1. 내일 날짜 (한국시간 기준) ──────────────────────
tomorrow = (datetime.utcnow() + timedelta(hours=9, days=1)).strftime('%Y-%m-%d')

# ── 2. NBA 경기 조회 ───────────────────────────────────
res = requests.get(
    "https://api.balldontlie.io/v1/games",
    params={"dates[]": tomorrow, "per_page": 30},
    headers={"Authorization": "0"}
)
games = res.json().get("data", [])

# ── 3. 메시지 구성 ─────────────────────────────────────
if not games:
    text = f"🏀 {tomorrow}\\n내일은 NBA 경기가 없습니다!"
else:
    lines = [f"🏀 내일 NBA 경기 일정 ({tomorrow} 한국시간)\\n"]
    for g in games:
        utc_time = datetime.strptime(g["date"][:16], "%Y-%m-%dT%H:%M")
        kst_time = utc_time + timedelta(hours=9)
        lines.append(
            f"⏰ {kst_time.strftime('%H:%M')} | "
            f"{g['home_team']['abbreviation']} vs {g['visitor_team']['abbreviation']}"
        )
    text = "\\n".join(lines)

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
requests.post(
    "https://kapi.kakao.com/v2/api/talk/memo/default/send",
    headers={"Authorization": f"Bearer {access_token}"},
    data={
        "template_object": f'{{"object_type":"text","text":"{text}","link":{{"web_url":"https://www.nba.com"}}}}'
    }
)
print("전송 완료!\\n" + text)
