import sys
import os
from datetime import datetime, timedelta

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from review.models import RevisionLogic
from review.database import DB_PATH

def test_revision_logic():
    # Remove existing test DB if any
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    logic = RevisionLogic()
    
    print("--- Test 1: Creating Topic ---")
    today = datetime.now().strftime('%Y-%m-%d')
    topic_id = logic.create_topic_with_revisions("Direito Constitucional", "Direito", today, "concurso,essencial", "#ff5733")
    
    revisions = logic.db.get_revisions_for_topic(topic_id)
    print(f"Created Topic ID: {topic_id}")
    print("Initial Revisions:")
    for r in revisions:
        print(f"  ID: {r[0]}, Date: {r[2]}, Interval: {r[4]}")

    print("\n--- Test 2: Mark as Not Studied (Shift) ---")
    # Mark the first revision (7 days) as not studied
    first_rev_id = revisions[0][0]
    logic.mark_as_not_studied(first_rev_id, topic_id)
    
    revisions_after = logic.db.get_revisions_for_topic(topic_id)
    print("Revisions after shift:")
    for r in revisions_after:
        print(f"  ID: {r[0]}, Date: {r[2]}, Interval: {r[4]}")

    # Verify shift
    d1_old = datetime.strptime(revisions[0][2], '%Y-%m-%d')
    d1_new = datetime.strptime(revisions_after[0][2], '%Y-%m-%d')
    assert (d1_new - d1_old).days == 1
    
    d3_old = datetime.strptime(revisions[2][2], '%Y-%m-%d')
    d3_new = datetime.strptime(revisions_after[2][2], '%Y-%m-%d')
    assert (d3_new - d3_old).days == 1
    print("\nVerification Passed: All future revisions shifted by 1 day.")

if __name__ == "__main__":
    test_revision_logic()
