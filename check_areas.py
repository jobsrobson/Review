from review.logic import ReviewLogic
from review.database import Database

db = Database("review_dev.db")
logic = ReviewLogic(db)
areas = db.get_areas()
print("ID | Name | Color")
for a in areas:
    print(f"{a[0]} | {a[1]} | {a[2]}")
