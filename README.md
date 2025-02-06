# Documentation

## Prerequisites
Ensure you have Python installed (preferably Python 3.8 or later). You can check your Python version by running:

```sh
python3 --version
```

## Installation
1. Create a virtual environment (optional but recommended):

   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

2. Install the required packages:

   ```sh
   python3 -m pip install flask flask-cors playwright requests pandas
   ```

3. Install Playwright and Chromium:

   ```sh
   playwright install chromium
   playwright install-deps  # Linux/macOS users may need this
   ```

## Running Playwright with Two Instances
1. Launch two instances:

   ```sh
   python3 app.py &
   python3 backend.py
   ```

   If running on Windows (without `&`):

   ```sh
   start cmd /k python app.py
   start cmd /k python backend.py
   ```
