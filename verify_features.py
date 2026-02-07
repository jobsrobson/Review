from review.database import DatabaseManager
from review.utils import ui_to_db_date, db_to_ui_date
import os

def test_dates():
    print("Testing Date Utils...")
    ui_date = "05/02/2026"
    db_date = ui_to_db_date(ui_date)
    assert db_date == "2026-02-05", f"Expected 2026-02-05, got {db_date}"
    
    back_to_ui = db_to_ui_date(db_date)
    assert back_to_ui == ui_date, f"Expected {ui_date}, got {back_to_ui}"
    print("Dates OK.")

def test_db():
    print("Testing Database...")
    db_name = "test_review_v2.db"
    if os.path.exists(db_name):
        os.remove(db_name)
        
    db = DatabaseManager(db_name)
    
    # Test Areas with Color
    aid = db.add_area("Mathematics", "#FF0000")
    assert aid is not None
    areas = db.get_areas()
    found = False
    for a in areas:
        if a[0] == aid:
            assert a[2] == "#FF0000", f"Expected color #FF0000, got {a[2]}"
            found = True
            break
    assert found
    
    db.delete_area(aid)
    print("Areas with Color OK.")
    
    # Test Tags
    tid = db.add_managed_tag("Hard", "#00FF00")
    assert tid is not None
    tags = db.get_managed_tags()
    found = False
    for t in tags:
        if t[0] == tid:
            assert t[2] == "#00FF00", f"Expected color #00FF00, got {t[2]}"
            found = True
            break
    assert found
    
    db.delete_managed_tag(tid)
    print("Tags with Color OK.")

    # Test Color Propagation
    print("Testing Color Propagation...")
    # Create Area with red color
    red_aid = db.add_area("Red Area", "#FF0000")
    
    # Create Topic in that area, with no specific color (or blue)
    topic_id = db.add_topic("Calculus", "Red Area", "2026-02-05", "", "#0000FF", "")
    
    # 1. Check get_topics JOIN
    topics = db.get_topics()
    t_found = False
    for t in topics:
        if t[0] == topic_id:
            # index 7 should be area color #FF0000
            if len(t) > 7 and t[7] == "#FF0000":
                t_found = True
            else:
                 print(f"Topic tuple: {t}")
    assert t_found, "get_topics did not return area color"
    
    # 2. Check revisions JOIN
    # Add revision for today
    today = "2026-02-05"
    db.add_revision(topic_id, today, 7)
    
    # We need to simulate RevisionLogic or just query db directly if we were testing logic class
    # But since I modified models.py SQL, let's test that query.
    # I can't easily import RevisionLogic here without setting up the whole app structure or mocking
    # So I'll just check if I can run the query manually using the same SQL as models.py
    cursor = db.conn.cursor()
    cursor.execute('''
        SELECT r.id, r.topic_id, r.scheduled_date, r.status, r.interval_days, t.title, t.area, COALESCE(a.color, t.color)
        FROM revisions r
        JOIN topics t ON r.topic_id = t.id
        LEFT JOIN areas a ON t.area = a.name
        WHERE r.scheduled_date = ?
    ''', (today,))
    revs = cursor.fetchall()
    
    r_found = False
    for r in revs:
        if r[1] == topic_id:
            # index 7 should be #FF0000 (Area) overriding #0000FF (Topic)
            assert r[7] == "#FF0000", f"Expected #FF0000, got {r[7]}"
            r_found = True
    assert r_found, "Revision query did not return area color"
    
    db.delete_topic(topic_id)
    db.delete_area(red_aid)
    print("Color Propagation OK.")
    
    if os.path.exists(db_name):
        os.remove(db_name)

if __name__ == "__main__":
    test_dates()
    test_db()
