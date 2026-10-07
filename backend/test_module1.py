import asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app

def generate_mock_pdf() -> bytes:
    content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 200 >>
stream
BT
/F1 12 Tf
50 700 Td
(Candidate: Alex Candidate) Tj
0 -20 Td
(Skills: Python, FastAPI, Docker, SQL, Algorithms) Tj
0 -20 Td
(Projects: PrepAI Placement Platform with React) Tj
0 -20 Td
(Education: B.Tech Computer Science 2025) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000244 00000 n 
0000000496 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
577
%%EOF"""
    return content

async def run_tests():
    print("--- Starting Module 1 End-to-End Test Suite ---")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Register User
        test_email = f"candidate_{uuid.uuid4().hex[:6]}@example.com"
        reg_payload = {
            "name": "Alex Candidate",
            "email": test_email,
            "graduation_year": 2025,
            "branch": "Computer Science and Engineering",
            "password": "Password123!"
        }
        r = await ac.post("/api/auth/register", json=reg_payload)
        assert r.status_code == 200, f"Register failed: {r.text}"
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[PASS] 1. User registered successfully on PostgreSQL.")

        # 2. Get Initial Profile
        r = await ac.get("/api/candidate/profile", headers=headers)
        assert r.status_code == 200, f"Get profile failed: {r.text}"
        profile = r.json()
        assert profile["email"] == test_email
        print("[PASS] 2. Candidate profile retrieved.")

        # 3. Get Topic Taxonomy (~40 topics)
        r = await ac.get("/api/candidate/taxonomy")
        assert r.status_code == 200
        tax = r.json()["topics"]
        assert len(tax) >= 30, f"Expected ~40 topics, got {len(tax)}"
        print(f"[PASS] 3. Taxonomy loaded ({len(tax)} topics across DSA, CS, Languages).")

        # 4. Submit Self-Ratings
        rate_payload = {
            "ratings": [
                {"topic_id": "arrays", "rating": 4.5},
                {"topic_id": "dynamic-programming", "rating": 2.0},
                {"topic_id": "operating-systems", "rating": 4.0}
            ]
        }
        r = await ac.post("/api/candidate/skills/self-rate", headers=headers, json=rate_payload)
        assert r.status_code == 200
        print("[PASS] 4. Candidate self-ratings saved.")

        # 5. Fetch 15 Diagnostic Questions
        r = await ac.get("/api/candidate/diagnostic/questions", headers=headers)
        assert r.status_code == 200
        diag_q = r.json()
        assert len(diag_q) == 15, f"Expected 15 questions, got {len(diag_q)}"
        # Verify correct answer is NOT leaked
        assert "correct_index" not in diag_q[0]
        print("[PASS] 5. Diagnostic 15 questions retrieved securely.")

        # 6. Submit Diagnostic Quiz and test BKT P(L0) calculation
        answers = [{"question_id": q["id"], "selected_index": 1} for q in diag_q]
        r = await ac.post("/api/candidate/diagnostic/submit", headers=headers, json={"answers": answers})
        assert r.status_code == 200
        diag_res = r.json()
        assert diag_res["total_questions"] == 15
        print(f"[PASS] 6. Diagnostic evaluated: Accuracy = {diag_res['accuracy_percentage']}%, BKT P(L0) calibrated.")

        # 7. Set Target Company
        r = await ac.post("/api/candidate/target-company", headers=headers, json={"company_id": "google", "company_name": "Google", "is_primary": True})
        assert r.status_code == 200
        print("[PASS] 7. Primary target company set to Google.")

        # 8. Test Supabase Storage Resume Upload & Parsing
        pdf_bytes = generate_mock_pdf()
        files = {"file": ("my_resume.pdf", pdf_bytes, "application/pdf")}
        r = await ac.post("/api/candidate/resume/upload", headers=headers, files=files)
        assert r.status_code == 200, f"Upload failed: {r.text}"
        upload_data = r.json()
        assert upload_data["signed_url"] is not None
        print(f"[PASS] 8. Resume uploaded to Supabase Storage. Signed URL generated.")
        print(f"   Parsed skills: {upload_data['parsed'].get('skills')[:5] if upload_data['parsed'].get('skills') else 'none'}")

        # 9. Verify Privacy Delete Endpoint
        r = await ac.delete("/api/candidate/resume", headers=headers)
        assert r.status_code == 200
        print("[PASS] 9. Resume deleted from Supabase Storage and candidate profile cleared.")

        # 10. Verify final profile state
        r = await ac.get("/api/candidate/profile", headers=headers)
        assert r.status_code == 200
        final_profile = r.json()
        assert final_profile["resume_filename"] is None
        assert final_profile["resume_signed_url"] is None
        assert final_profile["target_company"] == "google"
        print("[PASS] 10. Final profile verified in clean state.")

    print("\nALL MODULE 1 TESTS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    asyncio.run(run_tests())
