import tkinter as tk
import random

# ═══════════════════════════════════════════════════════════════════════════════
# RPG Merchant Simulator — Code in Place Final Project
#
# A graphical shop simulator where you buy and sell RPG items with
# rarity tiers, dynamic stats, and a dark-themed UI.
# ═══════════════════════════════════════════════════════════════════════════════

# ─── Item Database ────────────────────────────────────────────────────────────
# Each item is a dictionary with name, price, attack bonus, and defense bonus.

ALL_ITEMS = [
    {"name": "Sword",    "price": 50, "attack": 5,  "defense": 0},
    {"name": "Shield",   "price": 40, "attack": 0,  "defense": 5},
    {"name": "Potion",   "price": 20, "attack": 2,  "defense": 0},
    {"name": "Bow",      "price": 60, "attack": 7,  "defense": 0},
    {"name": "Armor",    "price": 80, "attack": 0,  "defense": 8},
    {"name": "Ring",     "price": 30, "attack": 3,  "defense": 2},
    {"name": "Dagger",   "price": 25, "attack": 3,  "defense": 0},
    {"name": "Helmet",   "price": 45, "attack": 0,  "defense": 4},
    {"name": "Boots",    "price": 35, "attack": 0,  "defense": 3},
]

# ─── Rarity System ────────────────────────────────────────────────────────────
# Each rarity has: name, display color, and probability weight (must sum to 1.0).

RARITIES = [
    ("Common",    "#ffffff", 0.50),
    ("Rare",      "#4a9eff", 0.30),
    ("Epic",      "#a855f7", 0.15),
    ("Legendary", "#f59e0b", 0.05),
]

RARITY_COLORS = {name: color for name, color, _ in RARITIES}


def roll_rarity():
    """Pick a rarity based on configured probabilities.

    Returns a (name, color) tuple. Probabilities are:
    Common 50%, Rare 30%, Epic 15%, Legendary 5%.
    """
    roll = random.random()
    cumulative = 0.0
    for name, color, prob in RARITIES:
        cumulative += prob
        if roll <= cumulative:
            return name, color
    return "Common", "#ffffff"  # fallback (should never reach)


def build_shop(count=6):
    """Create a random shop inventory.

    Picks *count* unique items from ALL_ITEMS and assigns each a
    random rarity. Returns a list of item dicts enriched with
    'rarity' and 'rarity_color' keys.
    """
    selected = random.sample(ALL_ITEMS, min(count, len(ALL_ITEMS)))
    shop = []
    for item in selected:
        rarity_name, rarity_color = roll_rarity()
        shop.append({
            "name":         item["name"],
            "price":        item["price"],
            "attack":       item["attack"],
            "defense":      item["defense"],
            "rarity":       rarity_name,
            "rarity_color": rarity_color,
        })
    return shop


# ─── Player Data ──────────────────────────────────────────────────────────────

player = {
    "gold":      100,
    "attack":    0,
    "defense":   0,
    "inventory": [],
}

shop_items = build_shop(6)


# ═══════════════════════════════════════════════════════════════════════════════
# UI Constants
# ═══════════════════════════════════════════════════════════════════════════════

WINDOW_W = 800
WINDOW_H = 600

CARD_W   = 110
CARD_H   = 130
CARD_GAP = 15

# Vertical layout positions
STATS_Y       = 15
SEP_Y         = 48
SHOP_TITLE_Y  = 66
SHOP_CARDS_Y  = 88
INV_TITLE_Y   = 243
INV_CARDS_Y   = 265

# Color palette
BG_COLOR      = "#1a1a2e"
CARD_BG       = "#16213e"
CARD_BORDER   = "#0f3460"
GOLD_COLOR    = "#f5c842"
ATK_COLOR     = "#ff6b35"
DEF_COLOR     = "#4fc3f7"
MSG_COLOR     = "#ff6b6b"
TITLE_COLOR   = "#a0a0a0"
EMPTY_COLOR   = "#555577"
SEP_COLOR     = "#333355"


# ═══════════════════════════════════════════════════════════════════════════════
# Application Class
# ═══════════════════════════════════════════════════════════════════════════════

class RPGMerchant:
    """Main application — draws the UI and handles all interactions."""

    def __init__(self, root):
        self.root = root
        self.root.title("RPG Merchant Simulator")
        self.root.resizable(False, False)
        self._center_window()

        self.canvas = tk.Canvas(
            root,
            width=WINDOW_W,
            height=WINDOW_H,
            bg=BG_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.message = ""
        self._msg_job = None          # tracks the after() timer for message

        # Mouse bindings
        self.canvas.bind("<Button-1>", self.on_left_click)   # buy
        self.canvas.bind("<Button-3>", self.on_right_click)  # sell (right-click)

        self.draw_ui()

    # ─── Window helpers ───────────────────────────────────────────────────

    def _center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - WINDOW_W) // 2
        y = (screen_h - WINDOW_H) // 2
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}+{x}+{y}")

    # ─── Drawing ──────────────────────────────────────────────────────────

    def draw_ui(self):
        """Full UI redraw: stats bar, shop, and inventory."""
        self.canvas.delete("all")
        self._draw_stats_bar()
        self._draw_separator()
        self.draw_shop()
        self.draw_inventory()

    def _draw_stats_bar(self):
        """Draw the top bar showing gold, attack, defense, and messages."""
        y = STATS_Y

        # Gold
        self.canvas.create_text(
            20, y, anchor="w",
            text=f"Gold: {player['gold']}",
            fill=GOLD_COLOR,
            font=("Courier New", 16, "bold"),
        )

        # Attack
        self.canvas.create_text(
            200, y, anchor="w",
            text=f"ATK: {player['attack']}",
            fill=ATK_COLOR,
            font=("Courier New", 16, "bold"),
        )

        # Defense
        self.canvas.create_text(
            340, y, anchor="w",
            text=f"DEF: {player['defense']}",
            fill=DEF_COLOR,
            font=("Courier New", 16, "bold"),
        )

        # Temporary message (right-aligned)
        if self.message:
            self.canvas.create_text(
                WINDOW_W - 20, y, anchor="e",
                text=self.message,
                fill=MSG_COLOR,
                font=("Courier New", 14, "bold"),
            )

    def _draw_separator(self):
        """Horizontal rule separating stats from shop."""
        self.canvas.create_line(
            20, SEP_Y, WINDOW_W - 20, SEP_Y,
            fill=SEP_COLOR, width=2,
        )

    def draw_shop(self):
        """Draw the SHOP section title and item cards."""
        self.canvas.create_text(
            20, SHOP_TITLE_Y, anchor="w",
            text="═══ SHOP ═══",
            fill=TITLE_COLOR,
            font=("Courier New", 14, "bold"),
        )

        if not shop_items:
            self.canvas.create_text(
                WINDOW_W // 2, SHOP_TITLE_Y + 50,
                text="Sold out! All items have been purchased.",
                fill=EMPTY_COLOR,
                font=("Courier New", 12),
            )
            return

        for i, item in enumerate(shop_items):
            x = self._card_x(i, len(shop_items))
            self._draw_card(x, SHOP_CARDS_Y, item)

    def draw_inventory(self):
        """Draw the INVENTORY section title and owned item cards."""
        self.canvas.create_text(
            20, INV_TITLE_Y, anchor="w",
            text="═══ INVENTORY ═══  (right-click to sell)",
            fill=TITLE_COLOR,
            font=("Courier New", 14, "bold"),
        )

        inv = player["inventory"]
        if not inv:
            self.canvas.create_text(
                WINDOW_W // 2, INV_TITLE_Y + 50,
                text="(empty — buy something from the shop!)",
                fill=EMPTY_COLOR,
                font=("Courier New", 12),
            )
            return

        for i, item in enumerate(inv):
            x = self._card_x(i, len(inv))
            self._draw_card(x, INV_CARDS_Y, item)

    # ─── Card layout and rendering ────────────────────────────────────────

    def _card_x(self, index, total):
        """Compute the X position of a card, centered in the window.

        *index* is 0-based position, *total* is the total number of cards
        in this row.
        """
        total_w = total * CARD_W + (total - 1) * CARD_GAP
        start_x = (WINDOW_W - total_w) // 2
        return start_x + index * (CARD_W + CARD_GAP)

    def _draw_card(self, x, y, item):
        """Draw a single item card at the given (x, y) position.

        The card shows:
          - Name (rarity-colored)
          - Price in gold
          - Rarity label
          - ATK and/or DEF bonuses
        """
        rarity_color = item.get("rarity_color", "#ffffff")

        # Background rectangle with rarity-colored border
        self.canvas.create_rectangle(
            x, y, x + CARD_W, y + CARD_H,
            fill=CARD_BG,
            outline=rarity_color,
            width=2,
        )

        # Item name
        self.canvas.create_text(
            x + CARD_W // 2, y + 18,
            text=item["name"],
            fill=rarity_color,
            font=("Courier New", 12, "bold"),
        )

        # Price
        self.canvas.create_text(
            x + CARD_W // 2, y + 40,
            text=f"{item['price']}g",
            fill=GOLD_COLOR,
            font=("Courier New", 11, "bold"),
        )

        # Rarity label
        rarity = item.get("rarity", "")
        if rarity:
            self.canvas.create_text(
                x + CARD_W // 2, y + 58,
                text=rarity,
                fill=rarity_color,
                font=("Courier New", 9),
            )

        # ATK bonus
        if item["attack"] > 0:
            self.canvas.create_text(
                x + CARD_W // 2, y + 80,
                text=f"ATK +{item['attack']}",
                fill=ATK_COLOR,
                font=("Courier New", 11, "bold"),
            )

        # DEF bonus
        if item["defense"] > 0:
            self.canvas.create_text(
                x + CARD_W // 2, y + 100,
                text=f"DEF +{item['defense']}",
                fill=DEF_COLOR,
                font=("Courier New", 11, "bold"),
            )

    # ─── Interaction handlers ─────────────────────────────────────────────

    def on_left_click(self, event):
        """Left-click on a shop card triggers a purchase."""
        x, y = event.x, event.y
        for i, item in enumerate(shop_items):
            cx = self._card_x(i, len(shop_items))
            cy = SHOP_CARDS_Y
            if cx <= x <= cx + CARD_W and cy <= y <= cy + CARD_H:
                self.buy_item(item)
                return

    def on_right_click(self, event):
        """Right-click on an inventory card triggers a sale."""
        x, y = event.x, event.y
        inv = player["inventory"]
        for i, item in enumerate(inv):
            cx = self._card_x(i, len(inv))
            cy = INV_CARDS_Y
            if cx <= x <= cx + CARD_W and cy <= y <= cy + CARD_H:
                self.sell_item(item)
                return

    def buy_item(self, item):
        """Attempt to buy *item*.

        If the player has enough gold, the item is added to inventory,
        gold and stats are updated, and the item is removed from the shop.
        Otherwise a "Not enough gold!" message is shown.
        """
        if player["gold"] >= item["price"]:
            player["gold"]     -= item["price"]
            player["attack"]   += item["attack"]
            player["defense"]  += item["defense"]
            player["inventory"].append(item)
            shop_items.remove(item)
            self.show_message(f"Bought {item['name']}!")
        else:
            self.show_message("Not enough gold!")
        self.draw_ui()

    def sell_item(self, item):
        """Sell *item* from inventory for half its purchase price.

        Gold and player stats are adjusted accordingly.
        """
        price = item["price"] // 2
        player["gold"]    += price
        player["attack"]  -= item["attack"]
        player["defense"] -= item["defense"]
        player["inventory"].remove(item)
        self.show_message(f"Sold {item['name']} for {price}g!")
        self.draw_ui()

    def update_stats(self):
        """Refresh the displayed stats.

        Stats are recalculated from the player dict each time draw_ui()
        runs, so this is a no-op kept for spec completeness.
        """
        pass

    def show_message(self, text):
        """Display a temporary message in the top-right corner.

        The message auto-clears after 2.5 seconds.
        """
        self.message = text
        if self._msg_job:
            self.root.after_cancel(self._msg_job)
        self._msg_job = self.root.after(2500, self._clear_message)
        self.draw_ui()

    def _clear_message(self):
        """Clear the temporary message and redraw."""
        self.message = ""
        self._msg_job = None
        self.draw_ui()


# ═══════════════════════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    app = RPGMerchant(root)
    root.mainloop()
