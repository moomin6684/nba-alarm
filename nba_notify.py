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
