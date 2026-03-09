import sqlite3
import os
import sys
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grocery.db")

#Database

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS members (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE
        );
        CREATE TABLE IF NOT EXISTS lists (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE
        );
        CREATE TABLE IF NOT EXISTS items (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            list_id    INTEGER NOT NULL,
            member_id  INTEGER NOT NULL,
            item_name  TEXT NOT NULL,
            added_date TEXT NOT NULL,
            bought     INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (list_id)   REFERENCES lists(id),
            FOREIGN KEY (member_id) REFERENCES members(id)
        );
    """)
    conn.commit()
    conn.close()

#Members
def db_get_members():
    c = get_conn().cursor()
    c.execute("SELECT id, name FROM members ORDER BY name")
    return c.fetchall()

def db_add_member(name):
    conn = get_conn()
    try:
        conn.execute("INSERT INTO members (name) VALUES (?)", (name.strip(),))
        conn.commit(); return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def db_remove_member(mid):
    conn = get_conn()
    conn.execute("DELETE FROM items WHERE member_id=?", (mid,))
    conn.execute("DELETE FROM members WHERE id=?", (mid,))
    conn.commit(); conn.close()

#Lists
def db_get_lists():
    c = get_conn().cursor()
    c.execute("SELECT id, name FROM lists ORDER BY name")
    return c.fetchall()

def db_add_list(name):
    conn = get_conn()
    try:
        conn.execute("INSERT INTO lists (name) VALUES (?)", (name.strip(),))
        conn.commit(); return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def db_remove_list(lid):
    conn = get_conn()
    conn.execute("DELETE FROM items WHERE list_id=?", (lid,))
    conn.execute("DELETE FROM lists WHERE id=?", (lid,))
    conn.commit(); conn.close()

#Items
def db_get_items(lid):
    c = get_conn().cursor()
    c.execute("""
        SELECT i.id, m.name, i.item_name, i.added_date, i.bought
        FROM items i JOIN members m ON i.member_id=m.id
        WHERE i.list_id=?
        ORDER BY i.bought ASC, i.id ASC
    """, (lid,))
    return c.fetchall()

def db_add_item(lid, mid, item_name):
    conn = get_conn()
    date = datetime.now().strftime("%d %b %Y %H:%M")
    conn.execute(
        "INSERT INTO items (list_id,member_id,item_name,added_date,bought) VALUES (?,?,?,?,0)",
        (lid, mid, item_name.strip(), date)
    )
    conn.commit(); conn.close()

def db_delete_item(item_id):
    conn = get_conn()
    conn.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit(); conn.close()

def db_toggle_bought(item_id, current):
    conn = get_conn()
    conn.execute("UPDATE items SET bought=? WHERE id=?", (0 if current else 1, item_id))
    conn.commit(); conn.close()

#Dsiplay

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def line(char="─", width=56):
    print(char * width)

def header(title):
    clear()
    line("═")
    print(f"  🛒  {title}")
    line("═")
    print()

def pause():
    input("\n  Press Enter to continue...")

def ask(prompt, allow_empty=False):
    while True:
        val = input(f"  {prompt}: ").strip()
        if val or allow_empty:
            return val
        print("  ! Please enter a value.")

def pick(prompt, options, allow_back=True):
    """
    Show a numbered menu from `options` list of (id, label).
    Returns (id, label) or None if user goes back.
    """
    print()
    for i, (_, label) in enumerate(options, 1):
        print(f"  [{i}] {label}")
    if allow_back:
        print("  [0] Back")
    print()
    while True:
        raw = input(f"  {prompt}: ").strip()
        if raw == "0" and allow_back:
            return None
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(options):
                return options[idx - 1]
        print(f"  ! Enter a number between 0 and {len(options)}.")

#Screens

def screen_members():
    while True:
        header("Manage Members")
        members = db_get_members()

        if members:
            print("  Current members:")
            for i, (mid, name) in enumerate(members, 1):
                print(f"    [{i}] {name}")
        else:
            print("  No Members Yet.")

        print()
        print("  [A] Add member")
        print("  [R] Remove member")
        print("  [0] Back")
        print()

        choice = input("  Choice: ").strip().upper()

        if choice == "0":
            return
        elif choice == "A":
            name = ask("New member name")
            if db_add_member(name):
                print(f"\n  ✓ '{name}' added.")
            else:
                print(f"\n  ! '{name}' already exists.")
            pause()
        elif choice == "R":
            if not members:
                print("\n  ! No members to remove.")
                pause()
                continue
            result = pick("Remove member #", members)
            if result:
                mid, name = result
                confirm = input(f"\n  Remove '{name}' and all their items? (y/n): ").strip().lower()
                if confirm == "y":
                    db_remove_member(mid)
                    print(f"  ✓ '{name}' removed.")
                    pause()


def screen_manage_lists():
    while True:
        header("Manage Lists")
        lists = db_get_lists()

        if lists:
            print("  Grocery lists:")
            for _, lname in lists:
                print(f"    • {lname}")
        else:
            print("  No lists yet.")

        print()
        print("  [A] Create new list")
        print("  [D] Delete a list")
        print("  [0] Back")
        print()

        choice = input("  Choice: ").strip().upper()

        if choice == "0":
            return
        elif choice == "A":
            name = ask("List name")
            if db_add_list(name):
                print(f"\n  ✓ List '{name}' created.")
            else:
                print(f"\n  ! A list named '{name}' already exists.")
            pause()
        elif choice == "D":
            if not lists:
                print("\n  ! No lists to delete.")
                pause()
                continue
            result = pick("Delete list #", lists)
            if result:
                lid, lname = result
                confirm = input(f"\n  Delete '{lname}' and all its items? (y/n): ").strip().lower()
                if confirm == "y":
                    db_remove_list(lid)
                    print(f"  ✓ '{lname}' deleted.")
                    pause()


def screen_view_list(lid, lname):
    """Read-only view of a list."""
    header(f"📋  {lname}  [View Only]")
    items = db_get_items(lid)

    if not items:
        print("  This list is empty.")
        pause()
        return

    total  = len(items)
    bought = sum(1 for i in items if i[4])

    print(f"  {total} items  |  {total - bought} to buy  |  {bought} bought\n")
    line()

    for item_id, member, item_name, date, is_bought in items:
        status = "✓" if is_bought else "○"
        strike = f"({item_name})" if is_bought else item_name
        print(f"  {status}  {strike:<28}  {member}  ·  {date}")

    line()
    pause()


def screen_list(lid, lname, current_member_id, current_member_name):
    while True:
        header(f"📝  {lname}")
        items = db_get_items(lid)

        total  = len(items)
        bought = sum(1 for i in items if i[4])
        print(f"  Logged in as: {current_member_name}")
        print(f"  {total} items  |  {total - bought} to buy  |  {bought} bought\n")

        if items:
            line()
            print(f"  {'#':<4} {'S':<3} {'Item':<28} {'Added by':<14} {'Date'}")
            line()
            for idx, (item_id, member, item_name, date, is_bought) in enumerate(items, 1):
                status = "✓" if is_bought else "○"
                display = f"({item_name})" if is_bought else item_name
                print(f"  {idx:<4} {status:<3} {display:<28} {member:<14} {date}")
            line()
        else:
            print("  List is empty.\n")

        print()
        print("  [A]  Add item")
        print("  [B]  Mark item as bought / unbought")
        print("  [D]  Delete item")
        print("  [0]  Back")
        print()

        choice = input("  Choice: ").strip().upper()

        if choice == "0":
            return

        elif choice == "A":
            item_name = ask("Item name")
            db_add_item(lid, current_member_id, item_name)
            print(f"\n  ✓ '{item_name}' added.")
            pause()

        elif choice == "B":
            if not items:
                print("\n  ! No items."); pause(); continue
            raw = input("  Toggle bought for item #: ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(items):
                item = items[int(raw) - 1]
                db_toggle_bought(item[0], item[4])
                state = "unbought" if item[4] else "bought"
                print(f"\n  ✓ '{item[2]}' marked as {state}.")
            else:
                print("  ! Invalid number.")
            pause()

        elif choice == "D":
            if not items:
                print("\n  ! No items."); pause(); continue
            raw = input("  Delete item #: ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(items):
                item = items[int(raw) - 1]
                confirm = input(f"  Delete '{item[2]}'? (y/n): ").strip().lower()
                if confirm == "y":
                    db_delete_item(item[0])
                    print(f"  ✓ '{item[2]}' deleted.")
            else:
                print("  ! Invalid number.")
            pause()


def screen_choose_list(current_member_id, current_member_name):
    while True:
        header(f"Choose a List  —  {current_member_name}")
        lists = db_get_lists()

        if not lists:
            print("  No lists exist yet. Create one from the main menu.")
            pause()
            return

        result = pick("Open list #", lists)
        if result is None:
            return
        lid, lname = result
        screen_list(lid, lname, current_member_id, current_member_name)


def screen_view_choose_list():
    header("View a List  [Read Only]")
    lists = db_get_lists()
    if not lists:
        print("  No lists exist yet.")
        pause()
        return
    result = pick("View list #", lists)
    if result:
        screen_view_list(*result)


#Main Menu

def main_menu():
    while True:
        header("Household Grocery List")
        members = db_get_members()

        print("  Who are you?")
        if members:
            for i, (_, name) in enumerate(members, 1):
                print(f"  [{i}] {name}")
        else:
            print("  (No Members Yet)")

        print()
        print("  [V]  View a list  (Read Only)")
        print("  [M]  Manage members")
        print("  [L]  Manage lists")
        print("  [Q]  Quit")
        print()

        choice = input("  Choice: ").strip().upper()

        if choice == "Q":
            clear()
            print("  Bye!\n")
            sys.exit(0)

        elif choice == "V":
            screen_view_choose_list()

        elif choice == "M":
            screen_members()

        elif choice == "L":
            screen_manage_lists()

        elif choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(members):
                mid, mname = members[idx - 1]
                screen_choose_list(mid, mname)
            else:
                print("\n  ! Invalid choice."); pause()
        else:
            print("\n  ! Invalid choice."); pause()

if __name__ == "__main__":
    init_db()
    main_menu()