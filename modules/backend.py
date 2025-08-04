import requests
import json
import os

def get_project_root():
    """Get the absolute path to the project root directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class ProfitabilityTool:
    def __init__(self, items_file="items.json"):
        self.items_file = items_file
        self.items = self.load_items()
        self.prices = self.get_latest_prices()

    def __str__(self):
        return f"{len(self.items)} items loaded!"

    def load_items(self):
        try:
            project_root = get_project_root()
            full_path = os.path.join(project_root, "resources", self.items_file)
            print(f"📂 Loading items from: {full_path}")
            with open(full_path, "r") as f:
                items = json.load(f)
                print(f"Loaded {len(items)} items. Sample: {dict(list(items.items())[:5])}")
                return items
        except Exception as e:
            print(f"❌ Error loading item ID file: {e}")
            return {}

    def get_latest_prices(self):
        """Fetch latest item prices from OSRS API."""
        url = "https://prices.runescape.wiki/api/v1/osrs/latest"
        headers = {
            "User-Agent": "profitability-tool/1.0 (alexb)"
        }

        print("🌐 Fetching latest prices...")
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            print(f"✅ Price data loaded.")
            return data.get("data", {})
        except requests.RequestException as e:
            print(f"❌ Error fetching prices: {e}")
            return {}

    def lookup(self, item_name):
        """Lookup and print price information for a given item name."""
        item_id = self.items.get(item_name)
        if item_id is None:
            print(f"❌ Item '{item_name}' not found in items.json.")
            return

        item_data = self.prices.get(str(item_id))
        if not item_data:
            print(f"❌ No price data found for item ID {item_id}.")
            return

        high = item_data["high"]
        low = item_data["low"]
        margin = high - low

        #print(f"✅ {item_name} (ID: {item_id})")
        #print(f"   High Price: {high:,} gp")
        #print(f"   Low Price:  {low:,} gp")
        #print(f"   Margin:     {margin:,} gp")

if __name__ == "__main__":
    tool = ProfitabilityTool()
    print(tool)  # Display how many items were loaded
    while True:
        item = input("\nEnter item name (or 'exit'): ").strip()
        if item.lower() == "exit":
            break
        tool.lookup(item)