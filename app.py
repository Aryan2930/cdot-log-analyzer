from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
from datetime import datetime

app = Flask(__name__)

# set QWEN_API_BASE and QWEN_API_KEY as env vars before running
c = OpenAI(
    base_url=os.environ.get("QWEN_API_BASE", "http://192.168.177.92:8080/v1"),
    api_key=os.environ.get("QWEN_API_KEY", "EMPTY"),
)
m = os.environ.get("QWEN_MODEL_NAME", "/workspace/Qwen3-Coder-Next-FP8")

sc = ".,;:()[]{}\"'!?"
sw = {"the", "and", "from", "with", "that", "this", "what",
      "show", "give", "tell", "find", "list", "who", "all"}
ipw = {"ip", "ips", "address", "addresses"}
pw = {"port", "ports"}
tw = {"time", "times", "timestamp", "timestamps", "when"}

def gw(t):
    # split text into clean lowercase words
    return [w.strip(sc).lower() for w in t.split()]

def hip(l):
    # check if line has an ip address
    for t in l.split():
        t = t.strip(sc)
        p = t.split(".")
        if len(p) == 4 and all(x.isdigit() and 0 <= int(x) <= 255 for x in p):
            return True
    return False

def hport(l):
    # check if line has a port number
    for t in l.split():
        t = t.strip(sc)
        if ":" in t:
            a = t.split(":")[-1]
            if a.isdigit() and 0 < int(a) <= 65535:
                return True
    return False

def htime(l):
    # check if line has a timestamp
    for t in l.split():
        t = t.strip(sc)
        if len(t) >= 10 and t[4] == "-" and t[7] == "-" and t[:4].isdigit():
            return True
        if len(t) == 8 and t[2] == ":" and t[5] == ":" and t.replace(":", "").isdigit():
            return True
    return False

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    x = request.json["question"]
    y = ""
    for i in os.listdir("logs"):
        if i == "conversation_history.log":
            continue  # don't feed our own past chat back in as log data
        if i.endswith(".txt") or i.endswith(".log"):
            data = open("logs/" + i, "r", encoding="utf-8", errors="ignore").read()
            for line in data.split("\n"):
                if line.strip():
                    y += f"[{i}] {line}\n"

    lines = y.split("\n")
    w = gw(x)
    kw = [a for a in w if len(a) > 3 and a not in sw]
    kw += [a for a in w if a in ipw]

    imp = []
    if any(a in ipw for a in w):
        for l in lines:
            if hip(l):
                imp.append(l)
    if any(a in pw for a in w):
        for l in lines:
            if hport(l):
                imp.append(l)
    if any(a in tw for a in w):
        for l in lines:
            if htime(l):
                imp.append(l)

    norm = [l for l in lines if any(k in l.lower() for k in kw)]

    f = []
    for l in imp + norm:
        if l not in f:
            f.append(l)
    if len(f) == 0:
        f = lines

    z = "\n".join(f[:5000])

    r = c.chat.completions.create(
        model=m,
        messages=[
            {
                "role": "system",
                "content": """You are a Linux log analysis expert.
                Read the logs carefully and answer ONLY what the user asked, nothing extra.
                Each log line you're given is prefixed with its source file in brackets, like [auth.log] the rest of the line.
                This bracket tag is ground truth — if asked which files you're reading, list exactly the distinct bracket tags you actually see, nothing invented.
                Do not include unrelated log lines or information the user did not ask about.
                For example, if asked about correct/successful logins, show only the successful ones and ignore failed login attempts.
                If asked about failed/incorrect logins, show only the failed ones and ignore successful attempts.
                Definition: a "correct" or "successful" login is any line containing "Accepted password for", "Accepted publickey for", or similar "Accepted ..." authentication lines (typically from sshd).
                A "failed" or "incorrect" login is any line containing "Failed password for", "authentication failure", or similar failure/rejection lines.
                If the logs contain no lines matching these patterns, say so plainly instead of guessing.
                Do not make up information.
                If the answer cannot be found in the logs, say so.
                Only include the specific field type the user asked for, and nothing else:
                - If they ask for IP addresses, list only IP addresses, exactly as they appear in the logs. Do not include port numbers or timestamps.
                - If they ask for port numbers, list only port numbers, exactly as they appear in the logs. Do not include IP addresses or timestamps.
                - If they ask for timestamps, list only timestamps, exactly as they appear in the logs. Do not include IP addresses or port numbers.
                - If they ask for a combination (e.g. "IPs and ports"), include only the fields explicitly requested, each clearly labeled.
                Explain the cause clearly, but keep the answer focused strictly on the question asked.""",
            },
            {
                "role": "user",
                "content": x + "\n" + z
            }
        ]
    )
    ans = r.choices[0].message.content

    with open("conversation_history.log", "a", encoding="utf-8") as h:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        h.write("\n")
        h.write(f"[{ts}] User: {x}\n")
        h.write("\n")
        h.write(f"[{ts}] AI: {ans}\n")
        h.write("\n")

    return jsonify({
        "answer": ans
    })

if __name__ == "__main__":
    app.run(debug=True)
