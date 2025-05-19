# Personal Diary Application

A secure and private desktop application for writing and managing personal diary entries.

## Features

*   **Secure Storage:** All diary entries are encrypted locally to ensure privacy.
*   **Password Protection:** The application requires a password for access.
*   **Encryption:** Uses robust encryption algorithms to protect your data.
*   **Multiple Views:**
    *   Write new entries with mood tracking.
    *   View all entries in a chronological list.
    *   View entries grouped by date.
*   **Data Migration:** Supports migration of data from older versions.
*   **Cross-Platform:** Built with Python and Tkinter, making it potentially cross-platform (though specific OS features for key/data storage are handled).

## Requirements

The application requires the following Python packages:

*   cryptography
*   PyInstaller (for building)
*   pytest (for testing)
*   pytest-cov (for test coverage)

These can be found in `requirements.txt`.

## Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd personal-diary-project # Or your project's directory name
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install development dependencies (for contributors):**
    ```bash
    pip install -r requirements-dev.txt
    ```
4.  **Initial Run & Setup:**
    *   On the first run, the application will guide you through creating an encryption key and setting up a password if they don't already exist.
    *   The encryption key (`.key.key`) and password file (`.password.txt`) are stored in a platform-specific application data directory (e.g., `~/.local/share/PersonalDiary` on Linux, `~/Library/Application Support/PersonalDiary` on macOS, `%APPDATA%\PersonalDiary` on Windows).

## How to Run

To run the application:

```bash
python diary_app.py
```

## File Structure

*   `diary_app.py`: Main entry point for the application.
*   `diary/`: Core application modules.
    *   `auth.py`: Handles user authentication and password management.
    *   `crypto.py`: Manages encryption and decryption of data.
    *   `storage.py`: Handles reading and writing diary entries.
    *   `ui/`: Contains the user interface components (Tkinter based).
        *   `main_window.py`: The main application window.
        *   `write_tab.py`, `view_tab.py`, `date_tab.py`: UI for different sections.
*   `requirements.txt`: Lists project dependencies.
*   `setup.py`: Script for packaging (though PyInstaller is preferred for executables).
*   `build_app.py`: Script to facilitate building the application using PyInstaller.
*   `PersonalDiary.spec`: PyInstaller specification file.
*   `tests/`: Contains unit tests for the application.
*   `.github/`: Contains GitHub Actions workflows (e.g., for CI).
*   `LICENSE`: Project's license file.
*   `README.md`: This file.

## Building the Application

You can build a standalone executable using PyInstaller:

1.  **Ensure PyInstaller is installed:**
    ```bash
    pip install PyInstaller
    ```
2.  **Run the build script:**
    ```bash
    python build_app.py
    ```
    This will use the `PersonalDiary.spec` file to create a distributable application in the `dist` folder.

## Contributing

Contributions are welcome! If you'd like to contribute:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Add tests for your changes if applicable.
5.  Ensure all tests pass (`pytest`).
6.  Commit your changes (`git commit -m 'Add some feature'`).
7.  Push to the branch (`git push origin feature/your-feature-name`).
8.  Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
