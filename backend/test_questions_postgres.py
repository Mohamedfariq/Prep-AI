import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

async def test():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post("/api/auth/login", json={"email": "alex@test.com", "password": "Password123!"})
        if login_res.status_code != 200:
            reg_res = await ac.post("/api/auth/register", json={
                "name": "Alex Test",
                "email": "alex@test.com",
                "graduation_year": 2025,
                "branch": "CSE",
                "password": "Password123!"
            })
            token = reg_res.json()["access_token"]
        else:
            token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Test Questions list from PostgreSQL
        q_res = await ac.get("/api/questions", headers=headers, params={"limit": 10})
        assert q_res.status_code == 200, f"Questions failed: {q_res.text}"
        q_data = q_res.json()
        total_q = q_data["total"]
        items_count = len(q_data["items"])
        print(f"[PASS] Questions retrieved: {items_count} | Total in Postgres: {total_q}")
        assert total_q >= 3000

        # 2. Test Question search & difficulty filter
        search_res = await ac.get("/api/questions", headers=headers, params={"search": "Two Sum", "difficulty": "Easy"})
        assert search_res.status_code == 200
        search_data = search_res.json()
        print(f"[PASS] Search 'Two Sum' count: {len(search_data['items'])}")

        # 3. Test Question detail
        first_id = q_data["items"][0]["question_id"]
        detail_res = await ac.get(f"/api/questions/{first_id}", headers=headers)
        assert detail_res.status_code == 200
        print(f"[PASS] Question detail title: {detail_res.json()['title']}")

        # 4. Test Companies from PostgreSQL
        comp_res = await ac.get("/api/companies", headers=headers, params={"search": "Google"})
        assert comp_res.status_code == 200
        comp_data = comp_res.json()
        names = [c["name"] for c in comp_data["companies"]]
        print(f"[PASS] Companies found: {names}")

        # 5. Test Company Detail
        google_detail = await ac.get("/api/companies/google", headers=headers)
        assert google_detail.status_code == 200
        total_gq = google_detail.json()["oa_profile"]["total_questions"]
        print(f"[PASS] Google company detail. Total questions: {total_gq}")

    print("\nALL POSTGRESQL QUESTION & COMPANY ENDPOINTS VERIFIED SUCCESSFULLY!\n")

if __name__ == "__main__":
    asyncio.run(test())
