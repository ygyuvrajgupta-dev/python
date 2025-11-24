import json
from datetime import datetime, timedelta

DATA = "books.json"

def load():
    try:
        with open(DATA,"r",encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save(books):
    with open(DATA,"w",encoding="utf-8") as f:
        json.dump(books,f,indent=2,ensure_ascii=False)

books = load()

def find(isbn):
    return next((b for b in books if b.get("isbn")==isbn), None)

def add_book():
    t = input("Title: ").strip()
    a = input("Author: ").strip() or "Unknown"
    i = input("ISBN: ").strip()
    if not t or not i:
        print("Title and ISBN required."); return
    if find(i):
        print("ISBN exists."); return
    books.append({"title":t,"author":a,"isbn":i,"status":"available"})
    save(books); print("Added.")

def view_books():
    if not books:
        print("No books."); return
    for b in books:
        print(f"{b['title']} — {b['author']} | ISBN:{b['isbn']} | {b['status']}")
    print()

def search_book():
    k = input("Search (title/author/isbn): ").strip().lower()
    res = [b for b in books if k in b.get("title","").lower() or k in b.get("author","").lower() or k in b.get("isbn","").lower()]
    if not res: print("No match."); return
    for b in res: print(f"{b['title']} — {b['author']} | ISBN:{b['isbn']} | {b['status']}")

def issue_book():
    i = input("ISBN to issue: ").strip()
    b = find(i)
    if not b: print("Not found."); return
    if b["status"]!="available": print("Already issued."); return
    borrower = input("Borrower name: ").strip() or "Unknown"
    b.update({"status":"issued","borrower":borrower,"due_date":(datetime.now()+timedelta(days=14)).strftime("%Y-%m-%d")})
    save(books); print("Issued.")

def return_book():
    i = input("ISBN to return: ").strip()
    b = find(i)
    if not b: print("Not found."); return
    if b["status"]!="issued": print("Not issued."); return
    b.update({"status":"available","borrower":None,"due_date":None})
    save(books); print("Returned.")

def menu():
    opts = {"1":add_book,"2":view_books,"3":search_book,"4":issue_book,"5":return_book,"6":exit}
    while True:
        print("\n1.Add 2.View 3.Search 4.Issue 5.Return 6.Exit")
        c = input("Choice: ").strip()
        if c in opts: opts[c]()
        else: print("Invalid.")

if __name__=="__main__":
    menu()
