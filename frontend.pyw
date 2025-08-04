import tkinter as tk
from tkinter import ttk
from modules.backend import ProfitabilityTool
import json
import os

class ProfitToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OSRS Profitability Tool")
        self.root.resizable(False, False)
        self.tool = ProfitabilityTool()
        self.tool.prices = self.tool.get_latest_prices()

        # Center the window on the screen
        window_width = 400
        window_height = 650
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Create scrollable canvas
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        # Configure canvas and scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Create a window in the canvas to hold the frame
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Update scroll region when frame size changes
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Store input/output items
        self.inputs = []
        self.outputs = []

        # Track row numbers for dynamic layout
        self.input_row = 5  # Adjusted for combobox
        self.output_row = 101  # Adjusted for combobox, +1 to maintain offset

        # Labels for CALCULATIONS and HOURLY RATE sections
        self.input_total_label = None
        self.output_total_label = None
        self.tax_label = None
        self.post_tax_label = None
        self.margin_label = None
        self.time_entry = None
        self.hourly_rate_label = None

        # Combobox for recipes
        self.recipe_combobox = None
        self.recipes = {}  # Store loaded recipes

        self.setup_widgets()
        self.load_recipes()

    def setup_widgets(self):
        # Configure grid columns for centering (12 columns, use 1-4 for content)
        for i in range(12):
            self.scrollable_frame.grid_columnconfigure(i, weight=1)

        # Recipe Selection
        tk.Label(self.scrollable_frame, text="Select Recipe:", font=("Arial", 12)).grid(row=0, column=1, columnspan=2, sticky='w', padx=5)
        self.recipe_combobox = ttk.Combobox(self.scrollable_frame, width=20, state="readonly")
        self.recipe_combobox.grid(row=0, column=3, columnspan=2, padx=5, pady=5)
        self.recipe_combobox.bind("<<ComboboxSelected>>", self.load_selected_recipe)

        # CALCULATIONS Section
        tk.Label(self.scrollable_frame, text="CALCULATIONS", font=("Arial", 16, "bold")).grid(row=195, column=0, columnspan=5, pady=(40, 0), sticky='ew')
        ttk.Separator(self.scrollable_frame, orient='horizontal').grid(row=196, column=1, columnspan=5, sticky='ew', pady=5)
        tk.Label(self.scrollable_frame, text="INPUT TOTAL:").grid(row=197, column=1, columnspan=2)
        self.input_total_label = tk.Label(self.scrollable_frame, text="0", width=10)
        self.input_total_label.grid(row=197, column=3, columnspan=2)
        tk.Label(self.scrollable_frame, text="OUTPUT TOTAL:").grid(row=198, column=1, columnspan=2)
        self.output_total_label = tk.Label(self.scrollable_frame, text="0", width=10)
        self.output_total_label.grid(row=198, column=3, columnspan=2)
        tk.Label(self.scrollable_frame, text="TAX:").grid(row=199, column=1, columnspan=2)
        self.tax_label = tk.Label(self.scrollable_frame, text="0", width=10)
        self.tax_label.grid(row=199, column=3, columnspan=2)
        tk.Label(self.scrollable_frame, text="POST-TAX:").grid(row=200, column=1, columnspan=2)
        self.post_tax_label = tk.Label(self.scrollable_frame, text="0", width=10)
        self.post_tax_label.grid(row=200, column=3, columnspan=2)
        tk.Label(self.scrollable_frame, text="Post-Tax Margin:").grid(row=201, column=1, columnspan=2)
        self.margin_label = tk.Label(self.scrollable_frame, text="0", width=10)
        self.margin_label.grid(row=201, column=3, columnspan=2)

        # HOURLY RATE Section
        tk.Label(self.scrollable_frame, text="HOURLY RATE", font=("Arial", 16, "bold")).grid(row=203, column=0, columnspan=5, pady=(20, 0), sticky='ew')
        ttk.Separator(self.scrollable_frame, orient='horizontal').grid(row=204, column=1, columnspan=5, sticky='ew', pady=5)
        tk.Label(self.scrollable_frame, text="Time per Iteration (s):").grid(row=205, column=1, columnspan=2)
        self.time_entry = tk.Entry(self.scrollable_frame, width=10)
        self.time_entry.insert(0, "0")
        self.time_entry.grid(row=205, column=3, columnspan=2)
        tk.Label(self.scrollable_frame, text="Hourly Rate:").grid(row=206, column=1, columnspan=2)
        self.hourly_rate_label = tk.Label(self.scrollable_frame, text="N/A", width=10)
        self.hourly_rate_label.grid(row=206, column=3, columnspan=2)

        # Save Button
        tk.Button(self.scrollable_frame, text="Save Recipe", command=self.save_recipe).grid(row=207, column=1, columnspan=4, pady=10)

        # Bind time entry change
        self.time_entry.bind("<FocusOut>", self.update_calculations)

        # INPUTS Section
        tk.Label(self.scrollable_frame, text="INPUTS", font=("Arial", 16, "bold")).grid(row=1, column=1, columnspan=3)
        tk.Button(self.scrollable_frame, text="+", command=self.add_input_item).grid(row=1, column=4, padx=(10, 5), pady=0)
        tk.Button(self.scrollable_frame, text="-", command=self.remove_input_item).grid(row=1, column=5, padx=(5, 10), pady=0)

        ttk.Separator(self.scrollable_frame, orient='horizontal').grid(row=2, column=1, columnspan=5, sticky='ew', pady=5)

        tk.Label(self.scrollable_frame, text="Item Name").grid(row=3, column=1)
        tk.Label(self.scrollable_frame, text="Qty").grid(row=3, column=2)
        tk.Label(self.scrollable_frame, text="Buy Price (ea)").grid(row=3, column=3)
        tk.Label(self.scrollable_frame, text="Item Total").grid(row=3, column=4)

        # Add first input item row by default
        self.add_input_item()

        # OUTPUTS Section
        tk.Label(self.scrollable_frame, text="OUTPUTS", font=("Arial", 16, "bold")).grid(row=97, column=1, columnspan=3, pady=(40, 0))
        tk.Button(self.scrollable_frame, text="+", command=self.add_output_item).grid(row=97, column=4, padx=(10, 5), pady=(40, 0))
        tk.Button(self.scrollable_frame, text="-", command=self.remove_output_item).grid(row=97, column=5, padx=(5, 10), pady=(40, 0))

        ttk.Separator(self.scrollable_frame, orient='horizontal').grid(row=98, column=1, columnspan=5, sticky='ew', pady=5)

        tk.Label(self.scrollable_frame, text="Item Name").grid(row=99, column=1)
        tk.Label(self.scrollable_frame, text="Qty").grid(row=99, column=2)
        tk.Label(self.scrollable_frame, text="Sell Price (ea)").grid(row=99, column=3)
        tk.Label(self.scrollable_frame, text="Item Total").grid(row=99, column=4)

        # Add first output item row by default
        self.add_output_item()

    def save_recipe(self):
        """Save the current INPUTS and OUTPUTS as a recipe named after the first output item."""
        if not self.outputs or not self.outputs[0][0].get().strip():
            return  # No output item to name the recipe after

        recipe_name = self.format_item_name(self.outputs[0][0].get().strip())
        if not recipe_name:
            return

        recipe_data = {
            "inputs": [
                {
                    "name": name.get().strip(),
                    "qty": qty.get().strip(),
                    "price": price.get().strip()
                } for name, qty, price, _ in self.inputs if name.get().strip()
            ],
            "outputs": [
                {
                    "name": name.get().strip(),
                    "qty": qty.get().strip(),
                    "price": price.get().strip()
                } for name, qty, price, _ in self.outputs if name.get().strip()
            ]
        }

        self.recipes[recipe_name] = recipe_data
        with open("recipes.json", "w") as f:
            json.dump(self.recipes, f, indent=4)

        # Update combobox values
        self.recipe_combobox["values"] = list(self.recipes.keys())
        self.recipe_combobox.set(recipe_name)

    def load_recipes(self):
        """Load saved recipes from the JSON file and populate the combobox."""
        if os.path.exists("recipes.json"):
            with open("recipes.json", "r") as f:
                self.recipes = json.load(f)
            self.recipe_combobox["values"] = list(self.recipes.keys())
        else:
            self.recipe_combobox["values"] = []

    def load_selected_recipe(self, event=None):
        """Load the selected recipe from the combobox into INPUTS and OUTPUTS."""
        selected_recipe = self.recipe_combobox.get()
        if not selected_recipe:
            return

        recipe_data = self.recipes.get(selected_recipe)
        if not recipe_data:
            return

        # Clear existing rows
        while self.inputs:
            self.remove_input_item()
        while self.outputs:
            self.remove_output_item()

        # Load inputs
        for item in recipe_data.get("inputs", []):
            if item["name"]:
                self.add_input_item()
                name, qty, price, total = self.inputs[-1]
                name.delete(0, tk.END)
                name.insert(0, item["name"])
                qty.delete(0, tk.END)
                qty.insert(0, item["qty"])
                price.delete(0, tk.END)
                price.insert(0, item["price"])
                self.on_change_input(name, qty, price, total)

        # Load outputs
        for item in recipe_data.get("outputs", []):
            if item["name"]:
                self.add_output_item()
                name, qty, price, total = self.outputs[-1]
                name.delete(0, tk.END)
                name.insert(0, item["name"])
                qty.delete(0, tk.END)
                qty.insert(0, item["qty"])
                price.delete(0, tk.END)
                price.insert(0, item["price"])
                self.on_change_output(name, qty, price, total)

        self.update_calculations()

    def update_calculations(self, _=None):
        """Calculate and update the input total, output total, tax, post-tax, margin, and hourly rate."""
        input_total = 0
        output_total = 0

        # Sum input totals
        for _, _, _, total in self.inputs:
            total_text = total.cget("text").replace(",", "")
            if total_text != "N/A":
                try:
                    input_total += int(total_text)
                except ValueError:
                    continue

        # Sum output totals
        for _, _, _, total in self.outputs:
            total_text = total.cget("text").replace(",", "")
            if total_text != "N/A":
                try:
                    output_total += int(total_text)
                except ValueError:
                    continue

        # Calculate tax (2%), post-tax output, and margin
        tax = output_total * 0.02
        post_tax_output = output_total * 0.98
        margin = post_tax_output - input_total

        # Calculate hourly rate
        try:
            time_per_iteration = float(self.time_entry.get())
            if time_per_iteration > 0:
                hourly_rate = (margin * 3600) / time_per_iteration
                self.hourly_rate_label.configure(text=f"{hourly_rate:,.0f}")
            else:
                self.hourly_rate_label.configure(text="N/A")
        except ValueError:
            self.hourly_rate_label.configure(text="N/A")

        # Update labels
        self.input_total_label.configure(text=f"{input_total:,.0f}")
        self.output_total_label.configure(text=f"{output_total:,.0f}")
        self.tax_label.configure(text=f"{tax:,.0f}")
        self.post_tax_label.configure(text=f"{post_tax_output:,.0f}")
        self.margin_label.configure(text=f"{margin:,.0f}")

    def format_item_name(self, name):
        """Format item name to match RuneScape convention: first letter of first word capitalized, rest lowercase."""
        return ' '.join(word.capitalize() if i == 0 else word.lower() for i, word in enumerate(name.split()))

    def on_change_input(self, name, qty, price, total):
        """Handle changes for input items."""
        item_name = self.format_item_name(name.get().strip())
        if not item_name:  # Skip if item name is empty
            return

        try:
            quantity = int(qty.get()) if qty.get().strip() else 1  # Default to 1 if qty is empty
        except ValueError:
            price.delete(0, tk.END)
            price.insert(0, "N/A")
            total.configure(text="N/A")
            self.update_calculations()
            return

        print(f"Input Item: {item_name}, Qty: {quantity}")  # Debug
        item_id = self.tool.items.get(item_name)
        print(f"Item ID: {item_id}")  # Debug
        if not item_id:
            price.delete(0, tk.END)
            price.insert(0, "N/A")
            total.configure(text="N/A")
            self.update_calculations()
            return

        item_data = self.tool.prices.get(str(item_id))
        print(f"Item Data: {item_data}")  # Debug
        if not item_data:
            price.delete(0, tk.END)
            price.insert(0, "N/A")
            total.configure(text="N/A")
            self.update_calculations()
            return

        # Check if price was manually edited
        price_text = price.get().strip().replace(",", "")
        if price_text and price_text != "N/A":
            try:
                current_price = int(price_text)
                print(f"Manual Buy Price: {current_price}")  # Debug
            except ValueError:
                price.delete(0, tk.END)
                price.insert(0, "N/A")
                total.configure(text="N/A")
                self.update_calculations()
                return
        else:
            current_price = item_data.get("high")
            print(f"API Buy Price: {current_price}")  # Debug
            if current_price is not None:
                price.delete(0, tk.END)
                price.insert(0, f"{current_price:,.0f}")
            else:
                price.delete(0, tk.END)
                price.insert(0, "N/A")
                total.configure(text="N/A")
                self.update_calculations()
                return

        if current_price is not None:
            total.configure(text=f"{current_price * quantity:,.0f}")
        else:
            total.configure(text="N/A")
        self.update_calculations()

    def on_change_output(self, name, qty, price, total):
        """Handle changes for output items."""
        item_name = self.format_item_name(name.get().strip())
        if not item_name:  # Skip if item name is empty
            return

        try:
            quantity = int(qty.get()) if qty.get().strip() else 1  # Default to 1 if qty is empty
        except ValueError:
            price.delete(0, tk.END)
            price.insert(0, "N/A")
            total.configure(text="N/A")
            self.update_calculations()
            return

        print(f"Output Item: {item_name}, Qty: {quantity}")  # Debug
        item_id = self.tool.items.get(item_name)
        print(f"Item ID: {item_id}")  # Debug
        if not item_id:
            price.delete(0, tk.END)
            price.insert(0, "N/A")
            total.configure(text="N/A")
            self.update_calculations()
            return

        item_data = self.tool.prices.get(str(item_id))
        print(f"Item Data: {item_data}")  # Debug
        if not item_data:
            price.delete(0, tk.END)
            price.insert(0, "N/A")
            total.configure(text="N/A")
            self.update_calculations()
            return

        # Check if price was manually edited
        price_text = price.get().strip().replace(",", "")
        if price_text and price_text != "N/A":
            try:
                current_price = int(price_text)
                print(f"Manual Sell Price: {current_price}")  # Debug
            except ValueError:
                price.delete(0, tk.END)
                price.insert(0, "N/A")
                total.configure(text="N/A")
                self.update_calculations()
                return
        else:
            current_price = item_data.get("low")
            print(f"API Sell Price: {current_price}")  # Debug
            if current_price is not None:
                price.delete(0, tk.END)
                price.insert(0, f"{current_price:,.0f}")
            else:
                price.delete(0, tk.END)
                price.insert(0, "N/A")
                total.configure(text="N/A")
                self.update_calculations()
                return

        if current_price is not None:
            total.configure(text=f"{current_price * quantity:,.0f}")
        else:
            total.configure(text="N/A")
        self.update_calculations()

    def add_input_item(self):
        name = tk.Entry(self.scrollable_frame, width=20)
        qty = tk.Entry(self.scrollable_frame, width=5)
        qty.insert(0, "1")  # Prefill Qty with 1
        price = tk.Entry(self.scrollable_frame, width=10)
        total = tk.Label(self.scrollable_frame, text="N/A", width=10)

        name.bind("<FocusOut>", lambda e: self.on_change_input(name, qty, price, total))
        qty.bind("<FocusOut>", lambda e: self.on_change_input(name, qty, price, total))
        price.bind("<FocusOut>", lambda e: self.on_change_input(name, qty, price, total))

        name.grid(row=self.input_row, column=1, padx=5, pady=2)
        qty.grid(row=self.input_row, column=2, padx=5, pady=2)
        price.grid(row=self.input_row, column=3, padx=5, pady=2)
        total.grid(row=self.input_row, column=4, padx=5, pady=2)

        self.inputs.append((name, qty, price, total))
        self.input_row += 1
        self.update_calculations()

    def remove_input_item(self):
        if self.inputs:  # Check if there are any input rows to remove
            name, qty, price, total = self.inputs.pop()  # Remove the last input row
            name.destroy()
            qty.destroy()
            price.destroy()
            total.destroy()
            self.input_row -= 1
            self.update_calculations()

    def add_output_item(self):
        name = tk.Entry(self.scrollable_frame, width=20)
        qty = tk.Entry(self.scrollable_frame, width=5)
        qty.insert(0, "1")  # Prefill Qty with 1
        price = tk.Entry(self.scrollable_frame, width=10)
        total = tk.Label(self.scrollable_frame, text="N/A", width=10)

        name.bind("<FocusOut>", lambda e: self.on_change_output(name, qty, price, total))
        qty.bind("<FocusOut>", lambda e: self.on_change_output(name, qty, price, total))
        price.bind("<FocusOut>", lambda e: self.on_change_output(name, qty, price, total))

        name.grid(row=self.output_row, column=1, padx=5, pady=2)
        qty.grid(row=self.output_row, column=2, padx=5, pady=2)
        price.grid(row=self.output_row, column=3, padx=5, pady=2)
        total.grid(row=self.output_row, column=4, padx=5, pady=2)

        self.outputs.append((name, qty, price, total))
        self.output_row += 1
        self.update_calculations()

    def remove_output_item(self):
        if self.outputs:  # Check if there are any output rows to remove
            name, qty, price, total = self.outputs.pop()  # Remove the last output row
            name.destroy()
            qty.destroy()
            price.destroy()
            total.destroy()
            self.output_row -= 1
            self.update_calculations()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProfitToolApp(root)
    root.mainloop()