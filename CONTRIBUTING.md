# Contributing to GitHub Wrapped

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to GitHub Wrapped. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## 🛠️ How to Contribute

### Reporting Bugs

This section guides you through submitting a bug report. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

*   **Use a clear and descriptive title** for the issue to identify the problem.
*   **Describe the exact steps which reproduce the problem** in as many details as possible.
*   **Provide specific examples** to demonstrate the steps.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion, including completely new features and minor improvements to existing functionality.

*   **Use a clear and descriptive title** for the issue to identify the suggestion.
*   **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
*   **Explain why this enhancement would be useful** to most users.

### Pull Requests

1.  **Fork the repo** and create your branch from `main`.
2.  **Clone the project** to your own machine.
3.  **Commit changes** to your own branch.
4.  **Push** your work back up to your fork.
5.  Submit a **Pull Request** so that we can review your changes.

NOTE: Be sure to merge the latest from "upstream" before making a pull request!

## 💻 Development Setup

1.  **Clone the repo**:
    ```bash
    git clone https://github.com/4ni1ak/Git-Wrap.git
    cd Git-Wrap    ```

2.  **Set up virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the app**:
    ```bash
    python app.py
    ```

## 🧪 Testing

Currently, we rely on manual testing. Before submitting a PR, please ensure:
1.  The analysis works for both public and private repos (if you have a token).
2.  The image generation works correctly on the client side.
3.  The UI looks good on both Desktop and Mobile.

## 🎨 Style Guide

*   **Python**: Follow PEP 8 guidelines.
*   **JavaScript**: Use modern ES6+ syntax.
*   **CSS**: Keep it clean and organized. Use CSS variables for colors.

## 📜 License

By contributing, you agree that your contributions will be licensed under its MIT License.
