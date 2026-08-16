"""
End-to-End Tests for Education LLM Platform — Phases 1 through 4.

Tests the full HTTP API flow against a running server.
"""
import requests
import time
import os

BASE_URL = "http://localhost:8000"


def run_tests():
    print("=" * 60)
    print("Starting End-to-End Tests (Phases 1-4)")
    print("=" * 60)

    # ============================================================
    # PHASE 1: Auth, Chat, Documents
    # ============================================================

    # 1. Register User C
    print("\n--- Phase 1: Core Platform ---")
    print("Testing Registration...")
    res = requests.post(f"{BASE_URL}/auth/register", json={
        "email": "userC@example.com",
        "password": "password123"
    })
    if res.status_code in (200, 201):
        print("  Registration successful.")
    else:
        print(f"  User Registration failed/exists: {res.status_code}")

    # 2. Login User C
    print("Testing Login...")
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "userC@example.com",
        "password": "password123"
    })
    assert res.status_code == 200, f"Login failed: {res.text}"
    token_a = res.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print("  Login successful.")

    # 3. AI Chat
    print("Testing AI Chat...")
    res = requests.post(f"{BASE_URL}/api/chat/", json={
        "content": "Hello, what is a binary tree?"
    }, headers=headers_a)
    assert res.status_code == 200, f"Chat failed: {res.text}"
    print("  AI Chat successful.")

    # 4. Document Upload
    print("Testing Document Upload...")
    with open("test.txt", "w") as f:
        f.write("A binary tree is a tree data structure in which each node has at most two children.")

    with open("test.txt", "rb") as f:
        res = requests.post(f"{BASE_URL}/api/documents/upload",
                          files={"file": ("test.txt", f, "text/plain")}, data={"subject_id": ""},
                          headers=headers_a)
    assert res.status_code == 200, f"Upload failed: {res.text}"
    print("  Upload successful.")

    time.sleep(2)

    # 5. RAG Retrieval via Chat
    print("Testing RAG Chat...")
    res = requests.post(f"{BASE_URL}/api/chat/", json={
        "content": "What is a binary tree based on my documents?"
    }, headers=headers_a)
    assert res.status_code == 200, f"RAG Chat failed: {res.text}"
    print("  RAG Chat successful.")

    # ============================================================
    # PHASE 2: Quiz & Practice
    # ============================================================

    print("\n--- Phase 2: Quiz & Practice ---")

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
    print("  Quiz Generation successful.")

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

    res = requests.post(f"{BASE_URL}/api/quizzes/{quiz_id}/submit",
                       json={"answers": answers}, headers=headers_a)
    assert res.status_code == 200, f"Quiz Submit failed: {res.text}"
    print("  Quiz Submission successful.")

    # 8. Results & Mastery
    print("Testing Quiz Results...")
    res = requests.get(f"{BASE_URL}/api/quizzes/{quiz_id}/results", headers=headers_a)
    assert res.status_code == 200
    print("  Quiz Results retrieved.")

    print("Testing Analytics (Mastery)...")
    res = requests.get(f"{BASE_URL}/api/analytics/mastery", headers=headers_a)
    assert res.status_code == 200
    print("  Analytics retrieved.")

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
    print("  Practice Mode successful.")

    # ============================================================
    # PHASE 3: User Isolation
    # ============================================================

    print("\n--- Phase 3: User Isolation ---")

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
    print("  User Isolation successful.")

    # ============================================================
    # PHASE 4: Personalization Engine
    # ============================================================

    print("\n--- Phase 4: Personalization Engine ---")

    # 10. Learning Profile
    print("Testing Learning Profile...")
    res = requests.get(f"{BASE_URL}/api/personalization/profile/learning",
                      headers=headers_a)
    assert res.status_code == 200, f"Profile failed: {res.text}"
    profile = res.json()
    print(f"  Profile: streak={profile['current_streak']}, longest={profile['longest_streak']}")
    # After quiz submission + practice, streak should be >= 1
    assert profile["current_streak"] >= 1, "Streak should be at least 1 after activities"

    # 11. Learning Preferences
    print("Testing Learning Preferences...")
    res = requests.put(f"{BASE_URL}/api/personalization/profile/preferences", json={
        "explanation_style": "Step-by-step",
        "practice_preference": "More MCQs",
        "difficulty_preference": "Challenging"
    }, headers=headers_a)
    assert res.status_code == 200, f"Preferences failed: {res.text}"
    prefs = res.json()
    assert prefs["explanation_style"] == "Step-by-step"
    print("  Preferences updated successfully.")

    # 12. Learning Memories
    print("Testing Learning Memories (auto-generated from quiz)...")
    res = requests.get(f"{BASE_URL}/api/personalization/memory", headers=headers_a)
    assert res.status_code == 200, f"Memories failed: {res.text}"
    memories = res.json()
    print(f"  Found {len(memories)} auto-generated memories.")

    # 13. Create a manual memory
    print("Testing Manual Memory Creation...")
    res = requests.post(f"{BASE_URL}/api/personalization/memory", json={
        "memory_type": "GOAL",
        "content": "Student wants to master recursion by end of month",
        "confidence": 1.0,
        "source": "USER_INPUT"
    }, headers=headers_a)
    assert res.status_code == 200, f"Memory creation failed: {res.text}"
    print("  Manual memory created.")

    # 14. Study Plan Generation
    print("Testing Study Plan Generation...")
    res = requests.post(f"{BASE_URL}/api/personalization/study-plan/generate", json={
        "goal": "Improve recursion skills",
        "duration_days": 3,
        "available_minutes_per_day": 45
    }, headers=headers_a)
    assert res.status_code == 200, f"Study Plan Generate failed: {res.text}"
    plan = res.json()
    assert plan["title"], "Study plan should have a title"
    print(f"  Plan generated: '{plan['title']}' with {len(plan.get('items', []))} items")

    # 15. Get Study Plans
    print("Testing Get Study Plans...")
    res = requests.get(f"{BASE_URL}/api/personalization/study-plan", headers=headers_a)
    assert res.status_code == 200, f"Get plans failed: {res.text}"
    plans = res.json()
    assert len(plans) >= 1
    print(f"  Found {len(plans)} study plan(s).")

    # 16. Due Revisions
    print("Testing Due Revisions...")
    res = requests.get(f"{BASE_URL}/api/personalization/revision/due", headers=headers_a)
    assert res.status_code == 200, f"Due revisions failed: {res.text}"
    due = res.json()
    print(f"  {len(due)} topic(s) due for revision.")

    # 17. All Revisions
    print("Testing All Revision Schedules...")
    res = requests.get(f"{BASE_URL}/api/personalization/revision/all", headers=headers_a)
    assert res.status_code == 200, f"All revisions failed: {res.text}"
    all_revisions = res.json()
    assert len(all_revisions) >= 1, "Should have at least 1 revision schedule after quiz"
    print(f"  {len(all_revisions)} revision schedule(s) total.")

    # 18. Complete a revision (use the first topic from revision schedules)
    if all_revisions:
        topic_to_revise = all_revisions[0]["topic_id"]
        print(f"Testing Revision Completion for topic {topic_to_revise[:8]}...")
        res = requests.post(
            f"{BASE_URL}/api/personalization/revision/{topic_to_revise}/complete",
            json={"accuracy": 85.0},
            headers=headers_a
        )
        assert res.status_code == 200, f"Revision complete failed: {res.text}"
        rev_result = res.json()
        print(f"  Revision completed. Next review in {rev_result['interval_days']} days.")

    # 19. Recommendations
    print("Testing Recommendations...")
    res = requests.get(f"{BASE_URL}/api/personalization/recommendations", headers=headers_a)
    assert res.status_code == 200, f"Recommendations failed: {res.text}"
    recs = res.json()
    print(f"  Got {len(recs)} recommendation(s).")
    for r in recs[:3]:
        print(f"    [{r['type']}] {r['topic']}: {r['action']}")

    # 20. Learning Path
    print("Testing Learning Path...")
    res = requests.get(f"{BASE_URL}/api/personalization/learning-path", headers=headers_a)
    assert res.status_code == 200, f"Learning path failed: {res.text}"
    path = res.json()
    print(f"  Learning path has {len(path)} topic(s).")
    for p in path:
        print(f"    {p['topic_name']}: mastery={p['mastery_score']:.0f}, status={p['status']}")

    # 21. Study Sessions
    print("Testing Study Sessions...")
    res = requests.post(f"{BASE_URL}/api/personalization/study-sessions/start", json={
        "activity_type": "PRACTICE",
        "topic_id": None
    }, headers=headers_a)
    assert res.status_code == 200, f"Session start failed: {res.text}"
    session_id = res.json()["id"]
    print(f"  Study session started: {session_id[:8]}...")

    time.sleep(1)

    res = requests.post(
        f"{BASE_URL}/api/personalization/study-sessions/{session_id}/complete",
        json={"duration": 120, "completion_status": "COMPLETED"},
        headers=headers_a
    )
    assert res.status_code == 200, f"Session complete failed: {res.text}"
    print("  Study session completed.")

    # Get all sessions
    res = requests.get(f"{BASE_URL}/api/personalization/study-sessions", headers=headers_a)
    assert res.status_code == 200
    sessions = res.json()
    print(f"  Total study sessions: {len(sessions)}")

    # 22. Learning Analytics
    print("Testing Learning Analytics...")
    res = requests.get(f"{BASE_URL}/api/personalization/analytics/learning", headers=headers_a)
    assert res.status_code == 200, f"Analytics failed: {res.text}"
    analytics = res.json()
    print(f"  Analytics: questions={analytics['questions_solved']}, "
          f"streak={analytics['current_streak']}, "
          f"mastered={analytics['topics_mastered']}, "
          f"sessions={analytics['total_study_sessions']}")

    # 23. Phase 4 User Isolation
    print("\nTesting Phase 4 User Isolation...")
    res = requests.get(f"{BASE_URL}/api/personalization/memory", headers=headers_b)
    assert res.status_code == 200
    user_b_memories = res.json()
    assert len(user_b_memories) == 0, "User B should have no memories"

    res = requests.get(f"{BASE_URL}/api/personalization/revision/all", headers=headers_b)
    assert res.status_code == 200
    user_b_revisions = res.json()
    assert len(user_b_revisions) == 0, "User B should have no revisions"

    res = requests.get(f"{BASE_URL}/api/personalization/study-sessions", headers=headers_b)
    assert res.status_code == 200
    user_b_sessions = res.json()
    assert len(user_b_sessions) == 0, "User B should have no study sessions"
    print("  Phase 4 User Isolation verified.")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
