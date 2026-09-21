# C-DOT Log Analyzer

An AI-powered web application for searching and analyzing log files using Python, Flask and Large Language Models (LLMs).

## Features

- Search and analyze log files using natural-language questions
- Identify relevant log entries based on user queries
- Extract IP addresses, port numbers and timestamps
- Filter relevant log information before sending it to the LLM
- AI-generated responses based on the provided logs
- Web-based interface using Flask

## Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- OpenAI-compatible API
- Large Language Models (LLMs)

## How It Works

1. User enters a question through the web interface.
2. The application reads the available log files.
3. Relevant log entries are identified using keyword and pattern-based filtering.
4. The selected information is sent to the configured LLM.
5. The AI analyzes the logs and returns a focused response.

## Project Structure

```text
cdot-log-analyzer/
├── app.py
├── index.html
└── README.md
