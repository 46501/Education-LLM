import os
import requests
import time

BASE_URL = "http://localhost:8000"

def print_step(msg):
    print(f"\n--- {msg} ---")

def run_tests():
    print("============================================================")
    print("Starting End-to-End Tests (Phase 5: Exams & Interviews)")
    print("============================================================")
    
    # 1. Register and Login
    print_step("Authentication")
    test_user = {
        "email": f"test_phase5_{int(time.time())}@example.com",
        "password": "password123",
        "full_name": "Phase 5 Tester"
    }
    
    res = requests.post(f"{BASE_URL}/auth/register", json=test_user)
    if res.status_code not in [200, 201, 400]:
        print(f"Failed to register: {res.text}")
        return
        
    login_data = {"email": test_user["email"], "password": test_user["password"]}
    res = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print("Login Response:", res.status_code, res.text)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")

    # 2. Setup Exam
    print_step("Exam Engine")
    exam_payload = {
        "title": "Data Science Final Exam",
        "description": "A comprehensive end-term exam.",
        "exam_date": "2026-10-15T00:00:00Z",
        "duration_minutes": 120,
        "total_marks": 50,
        "topics": [] # Mock without topics first to ensure creation logic works
    }
    res = requests.post(f"{BASE_URL}/api/exams", json=exam_payload, headers=headers)
    assert res.status_code == 200, res.text
    exam_id = res.json()["id"]
    print("Exam Created.")
    
    # 3. Generate Mock Test
    res = requests.post(f"{BASE_URL}/api/exams/{exam_id}/generate", headers=headers)
    assert res.status_code == 200, res.text
    print("Mock Exam Generated (Activated).")
    
    # 4. Start Exam Session
    res = requests.post(f"{BASE_URL}/api/exams/{exam_id}/start", headers=headers)
    assert res.status_code == 200, res.text
    session_id = res.json()["session_id"]
    print("Exam Session Started.")
    
    # 5. Fetch Session Questions
    res = requests.get(f"{BASE_URL}/api/exams/{exam_id}/session/{session_id}", headers=headers)
    assert res.status_code == 200, res.text
    print("Fetched active session questions securely.")
    
    # 6. Submit Exam
    submission_payload = {
        "answers": []
    }
    res = requests.post(f"{BASE_URL}/api/exams/{exam_id}/session/{session_id}/submit", json=submission_payload, headers=headers)
    assert res.status_code == 200, res.text
    print("Exam Submitted.")
    
    # 7. Get Results
    res = requests.get(f"{BASE_URL}/api/exams/{exam_id}/session/{session_id}/results", headers=headers)
    assert res.status_code == 200, res.text
    print(f"Results fetched! Score: {res.json()['score']}")

    # 8. Setup Interview
    print_step("Interview Engine")
    interview_payload = {
        "interview_type": "TECHNICAL",
        "role": "Machine Learning Engineer",
        "experience_level": "ENTRY",
        "topics": ["Python", "Machine Learning"],
        "difficulty": "MEDIUM",
        "num_questions": 3
    }
    res = requests.post(f"{BASE_URL}/api/interviews", json=interview_payload, headers=headers)
    assert res.status_code == 200, res.text
    interview_id = res.json()["id"]
    print("Interview Setup Complete.")
    
    # 9. Start Interview
    res = requests.post(f"{BASE_URL}/api/interviews/{interview_id}/start", headers=headers)
    assert res.status_code == 200, res.text
    i_session_id = res.json()["session_id"]
    print(f"Interview Started. Initial Question: {res.json()['initial_message']}")
    
    # 10. Answer Interview Question
    ans_payload = {"answer": "I would use a random forest classifier."}
    res = requests.post(f"{BASE_URL}/api/interviews/session/{i_session_id}/answer", json=ans_payload, headers=headers)
    assert res.status_code == 200, res.text
    print("Answer evaluated successfully.")
    
    # 11. Complete Interview
    res = requests.post(f"{BASE_URL}/api/interviews/session/{i_session_id}/complete", headers=headers)
    assert res.status_code == 200, res.text
    print(f"Interview Completed! Score: {res.json()['score']}")
    
    print("============================================================")
    print("ALL PHASE 5 TESTS PASSED!")
    print("============================================================")

if __name__ == "__main__":
    run_tests()
