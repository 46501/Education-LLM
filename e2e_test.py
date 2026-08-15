import requests
import time
import os

BASE_URL = "http://localhost:8000"

def run_tests():
    print("Starting End-to-End Tests...")
    
    # 1. Register User C
    print("Testing Registration...")
    res = requests.post(f"{BASE_URL}/auth/register", json={
        "email": "userC@example.com",
        "password": "password123"
    })
    
    # If already exists, we ignore 400
    if res.status_code == 201:
        print("Registration successful.")
    else:
        print("User Registration failed/exists:", res.status_code, res.text)
        
    # 2. Login User C
    print("Testing Login...")
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "userC@example.com",
        "password": "password123"
    })
    assert res.status_code == 200, f"Login failed: {res.text}"
    token_a = res.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print("Login successful.")

    # 3. AI Chat
    print("Testing AI Chat...")
    res = requests.post(f"{BASE_URL}/api/chat/", json={
        "content": "Hello, what is a binary tree?"
    }, headers=headers_a)
    assert res.status_code == 200, f"Chat failed: {res.text}"
    print("AI Chat successful.")

    # 4. Document Upload
    print("Testing Document Upload...")
    with open("test.txt", "w") as f:
        f.write("A binary tree is a tree data structure in which each node has at most two children.")
    
    with open("test.txt", "rb") as f:
        res = requests.post(f"{BASE_URL}/api/documents/upload", files={"file": f}, data={"subject_id": ""}, headers=headers_a)
    assert res.status_code == 200, f"Upload failed: {res.text}"
    print("Upload successful.")
    
    # Let document process in background
    time.sleep(2)

    # 5. RAG Retrieval via Chat
    print("Testing RAG Chat...")
    res = requests.post(f"{BASE_URL}/api/chat/", json={
        "content": "What is a binary tree based on my documents?"
    }, headers=headers_a)
    assert res.status_code == 200, f"RAG Chat failed: {res.text}"
    print("RAG Chat successful.")

    # 6. Quiz Generation
    print("Testing Quiz Generation...")
    res = requests.post(f"{BASE_URL}/api/quizzes/generate", json={
        "title": "Trees Quiz",
        "subject": "Computer Science",
        "topic": "Binary Trees",
        "difficulty": "BEGINNER",
        "number_of_questions": 2,
        "question_type": "MCQ",
        "use_rag": False
    }, headers=headers_a)
    assert res.status_code == 200, f"Quiz Generate failed: {res.text}"
    quiz_id = res.json()["quiz_id"]
    print("Quiz Generation successful.")

    # 7. Get Quiz & Submit
    print("Testing Quiz Fetch & Submit...")
    res = requests.get(f"{BASE_URL}/api/quizzes/{quiz_id}", headers=headers_a)
    assert res.status_code == 200
    quiz = res.json()
    
    answers = []
    for q in quiz["questions"]:
        answers.append({
            "question_id": q["id"],
            "submitted_answer": q["options"][0] if q["options"] else "Test answer"
        })
    
    res = requests.post(f"{BASE_URL}/api/quizzes/{quiz_id}/submit", json={"answers": answers}, headers=headers_a)
    assert res.status_code == 200, f"Quiz Submit failed: {res.text}"
    print("Quiz Submission successful.")

    # 8. Results & Mastery
    print("Testing Quiz Results...")
    res = requests.get(f"{BASE_URL}/api/quizzes/{quiz_id}/results", headers=headers_a)
    assert res.status_code == 200
    print("Quiz Results retrieved.")

    print("Testing Analytics...")
    res = requests.get(f"{BASE_URL}/api/analytics/mastery", headers=headers_a)
    assert res.status_code == 200
    print("Analytics retrieved.")

    # 9. Practice Mode
    print("Testing Practice Mode...")
    res = requests.post(f"{BASE_URL}/api/practice/start", json={
        "subject": "Math",
        "topic": "Algebra",
        "difficulty": "BEGINNER"
    }, headers=headers_a)
    assert res.status_code == 200, f"Practice Start failed: {res.text}"
    q_id = res.json()["id"]
    
    res = requests.post(f"{BASE_URL}/api/practice/answer", json={
        "question_id": q_id,
        "submitted_answer": "42"
    }, headers=headers_a)
    assert res.status_code == 200, f"Practice Answer failed: {res.text}"
    print("Practice Mode successful.")

    # 10. User Isolation
    print("Testing User Isolation...")
    res = requests.post(f"{BASE_URL}/auth/register", json={
        "email": "userD@example.com",
        "password": "password123"
    })
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "userD@example.com",
        "password": "password123"
    })
    token_b = res.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    res = requests.get(f"{BASE_URL}/api/quizzes/{quiz_id}", headers=headers_b)
    assert res.status_code == 404, "User B should not access User A's quiz"
    print("User Isolation successful.")

    print("ALL TESTS PASSED!")

if __name__ == "__main__":
    run_tests()
