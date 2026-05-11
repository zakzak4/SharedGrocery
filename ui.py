import tkinter as tk
from tkinter import messagebox
from grocery_app import (init_db, db_get_members, db_add_member, db_remove_member,
    db_get_lists, db_add_list, db_remove_list, db_get_items, db_add_item,
    db_delete_item, db_toggle_bought)

init_db()

# ── Palette & Hover States 
BG            = "#1C1C1E"
CARD          = "#2C2C2E"
CARD2         = "#3A3A3C"
ACCENT        = "#30D158"
ACCENT2       = "#0A84FF"
DANGER        = "#FF453A"
TEXT          = "#F2F2F7"
MUTED         = "#8E8E93"
BOUGHT        = "#1C3829"
BORDER        = "#3A3A3C"

HOVER_ACCENT  = "#42E86B"
HOVER_ACCENT2 = "#299BFF"
HOVER_DANGER  = "#FF6159"
HOVER_CARD2   = "#48484A"

FONT_FAM      = "Segoe UI"

# ── UI Helpers
def clear(f):
    for w in f.winfo_children(): w.destroy()

def bind_hover(widget, normal_bg, hover_bg):
    widget.bind("<Enter>", lambda e: widget.config(bg=hover_bg))
    widget.bind("<Leave>", lambda e: widget.config(bg=normal_bg))

def create_card(parent, accent_color=ACCENT2, bg_color=CARD):
    """Creates a modern card with a left colored accent bar."""
    card = tk.Frame(parent, bg=bg_color)
    card.pack(fill="x", pady=5)
    tk.Frame(card, bg=accent_color, width=4).pack(side="left", fill="y")
    content = tk.Frame(card, bg=bg_color, padx=14, pady=12)
    content.pack(side="left", fill="both", expand=True)
    return card, content

def sep(p, color=BORDER, pady=12):
    tk.Frame(p, height=1, bg=color).pack(fill="x", pady=pady)

def heading(p, t):
    tk.Label(p, text=t, bg=BG, fg=TEXT,
             font=(FONT_FAM, 18, "bold"), anchor="center").pack(fill="x", pady=(0, 2))

def caption(p, t):
    tk.Label(p, text=t.upper(), bg=BG, fg=MUTED,
             font=(FONT_FAM, 8, "bold"), anchor="center").pack(fill="x")

def inline_btn(parent, text, cmd, bg_color, hover_color, fg_color=BG, w=None):
    b = tk.Button(parent, text=text, command=cmd,
                  font=(FONT_FAM, 9, "bold"),
                  bg=bg_color, fg=fg_color, relief="flat",
                  activebackground=hover_color, activeforeground=fg_color,
                  cursor="hand2", padx=12, pady=6, bd=0)
    if w: b.config(width=w)
    bind_hover(b, bg_color, hover_color)
    return b

def ghost_btn(parent, text, cmd):
    b = tk.Button(parent, text=text, command=cmd,
                  font=(FONT_FAM, 10, "bold"),
                  bg=BG, fg=MUTED, relief="flat",
                  activebackground=CARD, activeforeground=TEXT,
                  cursor="hand2", padx=10, pady=4, bd=0)
    bind_hover(b, BG, CARD)
    return b

def styled_entry(p, var, cmd, btn_text="➕ Add", btn_color=ACCENT, hover_color=HOVER_ACCENT):
    """A sleek, unified input bar."""
    r = tk.Frame(p, bg=CARD2, bd=0)
    r.pack(fill="x", pady=8)
    e = tk.Entry(r, textvariable=var, font=(FONT_FAM, 11),
                 bg=CARD2, fg=TEXT, insertbackground=ACCENT,
                 relief="flat", bd=0)
    e.pack(side="left", fill="x", expand=True, padx=12, ipady=10)
    e.bind("<Return>", lambda _: cmd())
    e.focus()
    
    b = tk.Button(r, text=btn_text, command=cmd,
                  font=(FONT_FAM, 10, "bold"),
                  bg=btn_color, fg=BG, relief="flat",
                  activebackground=hover_color, cursor="hand2",
                  padx=16, bd=0)
    b.pack(side="right", fill="y")
    bind_hover(b, btn_color, hover_color)
    return e


# ── App 
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Household Grocery List")
        self.geometry("560x660")
        self.resizable(False, False)
        self.configure(bg=BG)
        # Top vibrant accent line
        tk.Frame(self, bg=ACCENT, height=4).pack(fill="x")
        self.main = tk.Frame(self, bg=BG, padx=35, pady=20)
        self.main.pack(fill="both", expand=True)
        self.show_home()

    # ── Home 
    def show_home(self):
        clear(self.main)
        tk.Label(self.main, text="🛒", bg=BG, font=(FONT_FAM, 32)).pack(pady=(0, 5))
        heading(self.main, "Household Groceries")
        caption(self.main, "Select your profile")
        sep(self.main)

        members = db_get_members()
        if members:
            for mid, name in members:
                card, content = create_card(self.main, ACCENT)
                tk.Label(content, text=name, bg=CARD, fg=TEXT, 
                         font=(FONT_FAM, 12, "bold")).pack(side="left")
                
                btn_frame = tk.Frame(content, bg=CARD)
                btn_frame.pack(side="right")
                open_btn = inline_btn(btn_frame, "Open ➔", 
                                      lambda i=mid, n=name: self.show_lists(i, n), 
                                      ACCENT, HOVER_ACCENT)
                open_btn.pack(side="left", padx=(0, 4))
                del_btn = inline_btn(btn_frame, "🗑", 
                                     lambda i=mid, n=name: self.remove_member(i, n), 
                                     DANGER, HOVER_DANGER)
                del_btn.pack(side="left")
        else:
            tk.Label(self.main, text="No members yet — add one below.",
                     bg=BG, fg=MUTED, font=(FONT_FAM, 11)).pack(pady=10)

        sep(self.main)
        caption(self.main, "Add New Member")
        self.mvar = tk.StringVar()
        styled_entry(self.main, self.mvar, self.add_member, btn_color=ACCENT, hover_color=HOVER_ACCENT)
        sep(self.main)

        nav = tk.Frame(self.main, bg=BG)
        nav.pack()
        inline_btn(nav, "📋 Manage Lists", self.show_manage_lists, CARD, HOVER_CARD2, fg_color=TEXT).pack(side="left", padx=5)
        inline_btn(nav, "👁 View Lists", self.show_view_pick, CARD, HOVER_CARD2, fg_color=TEXT).pack(side="left", padx=5)

    def add_member(self):
        n = self.mvar.get().strip()
        if not n: return
        if not db_add_member(n): messagebox.showerror("Error", f"'{n}' already exists.")
        else: self.show_home()

    def remove_member(self, mid, name):
        if messagebox.askyesno("Remove", f"Remove '{name}' and all their items?"):
            db_remove_member(mid); self.show_home()

    # ── Choose List 
    def show_lists(self, mid, mname):
        clear(self.main)
        nav = tk.Frame(self.main, bg=BG)
        nav.pack(fill="x", pady=(0, 10))
        ghost_btn(nav, "⬅ Home", self.show_home).pack(side="left")
        
        tk.Label(self.main, text="👤", bg=BG, font=(FONT_FAM, 28)).pack()
        heading(self.main, f"Welcome, {mname}")
        caption(self.main, "Choose a list to open")
        sep(self.main, pady=8)

        lists = db_get_lists()
        if lists:
            for lid, n in lists:
                card, content = create_card(self.main, ACCENT2)
                tk.Label(content, text=f"📋 {n}", bg=CARD, fg=TEXT, 
                         font=(FONT_FAM, 12, "bold")).pack(side="left")
                inline_btn(content, "Open ➔", 
                           lambda i=lid, l=n: self.show_list(i, l, mid, mname), 
                           ACCENT2, HOVER_ACCENT2).pack(side="right")
        else:
            tk.Label(self.main, text="No lists yet — create one below.",
                     bg=BG, fg=MUTED, font=(FONT_FAM, 11)).pack(pady=10)

        sep(self.main)
        caption(self.main, "Create New List")
        self.nlvar = tk.StringVar()
        styled_entry(self.main, self.nlvar,
                     lambda: self.add_list_here(mid, mname), 
                     btn_text="➕ Create", btn_color=ACCENT2, hover_color=HOVER_ACCENT2)

    def add_list_here(self, mid, mname):
        n = self.nlvar.get().strip()
        if not n: return
        if not db_add_list(n): messagebox.showerror("Error", f"'{n}' already exists.")
        else: self.show_lists(mid, mname)

    # ── Manage Lists 
    def show_manage_lists(self):
        clear(self.main)
        nav = tk.Frame(self.main, bg=BG)
        nav.pack(fill="x", pady=(0, 10))
        ghost_btn(nav, "⬅ Home", self.show_home).pack(side="left")

        heading(self.main, "Manage Lists")
        sep(self.main, pady=8)

        lists = db_get_lists()
        if lists:
            for lid, n in lists:
                card, content = create_card(self.main, ACCENT2)
                tk.Label(content, text=n, bg=CARD, fg=TEXT,
                         font=(FONT_FAM, 12, "bold")).pack(side="left")
                inline_btn(content, "🗑 Delete", 
                           lambda i=lid, l=n: self.delete_list(i, l), 
                           DANGER, HOVER_DANGER).pack(side="right")
        else:
            tk.Label(self.main, text="No lists yet.", bg=BG, fg=MUTED, font=(FONT_FAM, 11)).pack(pady=10)

        sep(self.main)
        caption(self.main, "Create New List")
        self.lvar = tk.StringVar()
        styled_entry(self.main, self.lvar, self.add_list, 
                     btn_text="➕ Create", btn_color=ACCENT2, hover_color=HOVER_ACCENT2)

    def add_list(self):
        n = self.lvar.get().strip()
        if not n: return
        if not db_add_list(n): messagebox.showerror("Error", f"'{n}' already exists.")
        else: self.show_manage_lists()

    def delete_list(self, lid, name):
        if messagebox.askyesno("Delete", f"Delete '{name}' and all its items?"):
            db_remove_list(lid); self.show_manage_lists()

    # ── View Only Picker 
    def show_view_pick(self):
        clear(self.main)
        nav = tk.Frame(self.main, bg=BG)
        nav.pack(fill="x", pady=(0, 10))
        ghost_btn(nav, "⬅ Home", self.show_home).pack(side="left")

        heading(self.main, "View a List")
        caption(self.main, "Read Only Mode")
        sep(self.main, pady=8)

        lists = db_get_lists()
        if lists:
            for lid, n in lists:
                card, content = create_card(self.main, ACCENT2)
                tk.Label(content, text=f"📋 {n}", bg=CARD, fg=TEXT, 
                         font=(FONT_FAM, 12, "bold")).pack(side="left")
                inline_btn(content, "View ➔", 
                           lambda i=lid, l=n: self.show_list(i, l, None, None, True), 
                           ACCENT2, HOVER_ACCENT2).pack(side="right")
        else:
            tk.Label(self.main, text="No lists yet.", bg=BG, fg=MUTED, font=(FONT_FAM, 11)).pack(pady=10)

    # ── Main List Screen 
    def show_list(self, lid, lname, mid, mname, readonly=False):
        clear(self.main)
        

        nav = tk.Frame(self.main, bg=BG)
        nav.pack(fill="x")
        back_cmd = self.show_view_pick if readonly else lambda: self.show_lists(mid, mname)
        ghost_btn(nav, "⬅ Back", back_cmd).pack(side="left")
        
        header = tk.Frame(self.main, bg=BG)
        header.pack(fill="x", pady=(10, 0))
        tk.Label(header, text=lname, bg=BG, fg=TEXT, 
                 font=(FONT_FAM, 22, "bold")).pack(side="left")
        
        if not readonly:
            tag = tk.Frame(header, bg=CARD2, padx=8, pady=4)
            tag.pack(side="right")
            tk.Label(tag, text=f"👤 {mname}", bg=CARD2, fg=MUTED, 
                     font=(FONT_FAM, 9, "bold")).pack()

        items = db_get_items(lid)
        bought = sum(1 for i in items if i[4])
        remaining = len(items) - bought

        stats = tk.Frame(self.main, bg=BG)
        stats.pack(fill="x", pady=15)
        for val, label, color in [
            (len(items), "TOTAL", MUTED),
            (remaining,  "TO BUY", ACCENT),
            (bought,     "BOUGHT", ACCENT2),
        ]:
            cell = tk.Frame(stats, bg=CARD, padx=10, pady=8)
            cell.pack(side="left", fill="x", expand=True, padx=2)
            tk.Label(cell, text=str(val), bg=CARD, fg=color,
                     font=(FONT_FAM, 18, "bold")).pack()
            tk.Label(cell, text=label, bg=CARD, fg=MUTED,
                     font=(FONT_FAM, 8, "bold")).pack()

        frame = tk.Frame(self.main, bg=BG, height=260)
        frame.pack(fill="x")
        frame.pack_propagate(False)
        canvas = tk.Canvas(frame, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=BG)
        
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw", width=460)
        canvas.configure(yscrollcommand=sb.set)
        
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        if not items:
            tk.Label(sf, text="It's empty in here. Add some items!",
                     bg=BG, fg=MUTED, font=(FONT_FAM, 11)).pack(pady=40)

        for iid, mem, iname, date, ib in items:
            row_bg = BOUGHT if ib else CARD
            accent_c = MUTED if ib else ACCENT
            
            card, content = create_card(sf, accent_color=accent_c, bg_color=row_bg)

            left = tk.Frame(content, bg=row_bg)
            left.pack(side="left", fill="x", expand=True)

            title_font = (FONT_FAM, 12, "overstrike" if ib else "bold")
            tk.Label(left, text=iname, bg=row_bg, fg=MUTED if ib else TEXT, 
                     font=title_font).pack(anchor="w")
            tk.Label(left, text=f"Added by {mem} · {date}", bg=row_bg, fg=MUTED, 
                     font=(FONT_FAM, 8)).pack(anchor="w")

            if not readonly:
                right = tk.Frame(content, bg=row_bg)
                right.pack(side="right")
                
                toggle_txt = "↺ Undo" if ib else "✓ Bought"
                toggle_c = CARD2 if ib else ACCENT
                toggle_hov = HOVER_CARD2 if ib else HOVER_ACCENT
                fg_c = TEXT if ib else BG
                
                inline_btn(right, toggle_txt, 
                           lambda i=iid, b=ib: self._toggle(i, b, lid, lname, mid, mname), 
                           toggle_c, toggle_hov, fg_c).pack(side="left", padx=4)
                
                inline_btn(right, "✕", 
                           lambda i=iid, n=iname: self._delete(i, n, lid, lname, mid, mname), 
                           DANGER, HOVER_DANGER).pack(side="left")

        if not readonly:
            sep(self.main, pady=10)
            self.ivar = tk.StringVar()
            styled_entry(self.main, self.ivar,
                         lambda: self._add(lid, lname, mid, mname), 
                         btn_text="➕ Add Item", btn_color=ACCENT, hover_color=HOVER_ACCENT)

    def _add(self, lid, lname, mid, mname):
        n = self.ivar.get().strip()
        if n: db_add_item(lid, mid, n); self.show_list(lid, lname, mid, mname)

    def _delete(self, iid, name, lid, lname, mid, mname):
        if messagebox.askyesno("Delete", f"Delete '{name}'?"):
            db_delete_item(iid); self.show_list(lid, lname, mid, mname)

    def _toggle(self, iid, cur, lid, lname, mid, mname):
        db_toggle_bought(iid, cur); self.show_list(lid, lname, mid, mname)

if __name__ == "__main__":
    App().mainloop()