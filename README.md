OSRS Profitability Tool
A Python-based desktop application for calculating the profitability of crafting or trading items in Old School RuneScape (OSRS). The tool allows users to input materials (inputs) and products (outputs), fetches real-time prices from an API, and calculates profit margins and hourly rates. Users can save recipes (named after the first output item) and load them later via a dropdown menu.
Features

Dynamic Input/Output Fields: Add or remove input and output items to calculate costs and revenues.
Real-Time Price Fetching: Integrates with an API to retrieve current buy and sell prices for OSRS items.
Profit Calculations: Computes input total, output total, tax (2%), post-tax profit, and post-tax margin.
Hourly Rate Estimation: Calculates potential hourly profit based on user-defined time per iteration.
Recipe Management: Save recipes (named after the first output item) and load them later using a combobox.
Scrollable Interface: Handles multiple items with a scrollable canvas for a clean user experience.

Prerequisites

Python 3.6 or higher
Required Python libraries:
tkinter (usually included with Python)
requests (for API calls, assumed to be used in ProfitabilityTool)



Installation

Clone the Repository:
git clone https://github.com/your-username/osrs-profitability-tool.git
cd osrs-profitability-tool


Install Dependencies:Ensure you have Python installed, then install the required libraries:
pip install requests


Set Up the Backend:The app relies on a ProfitabilityTool class in modules/backend.py to fetch item prices. Ensure this module is properly configured with access to an OSRS price API (e.g., OSRS Grand Exchange API). You may need to:

Obtain an API key (if required).
Update modules/backend.py with your API endpoint and credentials.


Run the Application:Execute the main script:
python profit_tool_app.py



Usage

Launch the App:Run the script to open the GUI window.

Add Inputs and Outputs:

Inputs: Add materials used in crafting/trading by clicking the "+" button in the INPUTS section. Enter the item name, quantity, and optionally override the buy price (defaults to API's high price).
Outputs: Add products by clicking the "+" button in the OUTPUTS section. Enter the item name, quantity, and optionally override the sell price (defaults to API's low price).
Use the "-" buttons to remove the last added input or output row.


Calculate Profits:

The app automatically calculates:
Input Total: Sum of input item costs (quantity × buy price).
Output Total: Sum of output item revenues (quantity × sell price).
Tax: 2% of the output total (Grand Exchange tax).
Post-Tax Profit: Output total minus tax and input total.
Post-Tax Margin: Post-tax profit displayed for clarity.


Enter the time per iteration (in seconds) in the HOURLY RATE section to estimate the hourly profit rate.


Save and Load Recipes:

Click "Save Recipe" to save the current inputs and outputs. The recipe is named after the first output item's name and stored in recipes.json.
Use the "Select Recipe" dropdown to load a previously saved recipe, which will populate the inputs and outputs fields and update calculations.


Notes:

Item names must match the API's naming convention (case-insensitive, formatted as first word capitalized, others lowercase, e.g., "Dragon bones").
Saved recipes are stored in recipes.json in the project directory.
The app centers on the screen and is non-resizable for a consistent experience.



File Structure

profit_tool_app.py: Main application script containing the GUI and logic.
modules/backend.py: Backend module for fetching item prices (not included in this repository; must be implemented separately).
recipes.json: Generated file storing saved recipes (created after saving a recipe).

Example
To calculate the profitability of making a potion:

Add inputs (e.g., "Vial of water", qty: 1; "Ranarr weed", qty: 1).
Add output (e.g., "Prayer potion (3)", qty: 1).
The app fetches prices, calculates totals, applies a 2% tax, and shows the profit margin.
Enter the time taken (e.g., 10 seconds) to see the hourly rate.
Click "Save Recipe" to save as "Prayer potion (3)".
Later, select "Prayer potion (3)" from the dropdown to reload the recipe.

Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a new branch (git checkout -b feature/your-feature).
Make changes and commit (git commit -m "Add your feature").
Push to the branch (git push origin feature/your-feature).
Open a pull request.

Please ensure your code follows Python PEP 8 style guidelines and includes appropriate comments.
License
This project is licensed under the MIT License. See the LICENSE file for details.
Acknowledgments

Built with Python and Tkinter for a lightweight, cross-platform GUI.
Designed for OSRS players to optimize in-game trading and crafting strategies.
