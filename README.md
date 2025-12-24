# 🎯 GitHub Wrapped 2025

A modern web application that generates a Spotify Wrapped-style year-in-review for your GitHub activity.

![GitHub Wrapped](https://img.shields.io/badge/GitHub-Wrapped-purple?style=for-the-badge&logo=github)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green?style=for-the-badge&logo=flask)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker)

## ✨ Key Features

- 📊 **Detailed Statistics**: In-depth analysis of your 2025 commits, merges, repos, and activity.
- 🎭 **Developer Persona**: Discover if you are a "Night Owl 🦉", "Weekend Warrior ⚔️", or "Dawn Patrol 🚁" based on your coding habits.
- 🔒 **Privacy First**: Images are generated entirely client-side. No data is stored on the server.
- ⚡ **Private Repo Support**: Include your private contributions securely using a GitHub Personal Access Token.
- 🔄 **Merge Analysis**: Focus on merge stats instead of just stars received.
- 🎨 **Modern Sharing**: Vertical image format optimized for LinkedIn Stories and Posts.
- 📋 **Easy Sharing**: One-click copy-to-clipboard functionality with a preview modal.
- 🏆 **Top Stats**: Most active projects, favorite languages, and commit message analysis.

## 🛠️ Tech Stack

### Backend
- **Python 3.11**: Core programming language.
- **Flask 3.0**: Lightweight WSGI web application framework.
- **GitHub GraphQL API**: For fetching precise contribution data (including private repos) efficiently.
- **GitHub REST API**: For fetching public repository metadata.
- **Gunicorn**: Production-grade WSGI HTTP server.

### Frontend
- **HTML5 & CSS3**: Modern, responsive design with CSS Grid and Flexbox.
- **Vanilla JavaScript**: Lightweight client-side logic for interactivity and API communication.
- **Canvas API**: For generating the shareable image directly in the browser.

### DevOps & Infrastructure
- **Docker & Docker Compose**: Containerization for easy deployment and consistency.
- **GitHub Actions**: CI/CD pipeline for automated testing and building.

## 🚀 Quick Start

### Using Docker (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/4ni1ak/Git-Wrap.git
    cd Git-Wrap    ```

2.  **Configure Environment Variables:**
    Create a `.env` file from the example:
    ```bash
    cp .env.example .env
    ```
    *Optional:* Add your `GITHUB_TOKEN` in `.env` to include private repository stats.

3.  **Run with Docker Compose:**
    ```bash
    docker-compose up -d
    ```

4.  **Access the App:**
    Open your browser and navigate to `http://localhost:3020`.

### Manual Installation

1.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application:**
    ```bash
    python app.py
    ```

## 🔧 Configuration

### GitHub Token (Optional but Recommended)

To include private repository contributions and avoid API rate limits, you need a GitHub Personal Access Token.

1.  Go to [GitHub Settings > Tokens](https://github.com/settings/tokens).
2.  Generate a new token (classic).
3.  Select scopes: `repo` (for private repos) and `read:user`.
4.  Add it to your `.env` file: `GITHUB_TOKEN=ghp_...`

## 🤝 Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to submit a Pull Request.

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

**Made with ❤️ using GitHub GraphQL API**
