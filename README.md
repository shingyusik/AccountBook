# AccountBook

## Overview
AccountBook is a Python-based application designed for recording and managing personal financial data. It allows users to log their expenses, income, and savings in a simple and organized way. Utilizing PyQt, the application provides a straightforward graphical interface for ease of use.

The recorded results are automatically saved in the 'Result/' directory located in the same folder as `main.py`. Categories and methods can be edited by clicking the 'Edit' button in the application. The changes are saved in `categories.json` or `methods.json` respectively. This tool is aimed at individuals who wish to track their daily financial activities and maintain a clear record of their transactions.

## Features

- Recording expenses, income, and savings
- User-friendly graphical interface using PyQt

## Requirements

This project uses Python 3. Install the dependencies listed in `requirements.txt` to get started.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd AccountBook
   ```
3. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # For Linux/MacOS
   venv\Scripts\activate   # For Windows
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application using the following command:

```bash
python main.py
```

## Project Structure

```
AccountBook/
├── main.py          # Main entry point for the application
├── requirements.txt # Dependency list
└── src/             # Source code directory
    ├── __init__.py       # Initializes the module
    ├── controller.py     # Manages application logic and user interactions
    ├── file_manager.py   # Handles file operations such as saving and loading data
    ├── table.py          # Manages tabular data structures and interactions
    ├── utils.py          # Contains utility functions for various operations
    └── view.py           # Handles the graphical user interface components
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a clear description of your changes.

## Contact

For questions or suggestions, please contact paulqwe1018@gmail.com.

