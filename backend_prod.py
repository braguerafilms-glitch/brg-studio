#!/usr/bin/env python3
"""
BRG Studio — Backend de Produção
Deploy: Railway
"""

import os
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

GROQ_KEY = os.environ.get("GROQ_KEY", "")
HF_URL   = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

# ── IA de texto via Groq (gratuito) ──
@app.route("/ia", methods=["POST"])
def ia():
    data        = request.json or {}
    system_text = data.get("system", "")
    max_tokens  = data.get("max_tokens", 1000)
    messages    = data.get("messages", [])
    prompt_text = ""
    for msg in messages:
        if msg.get("role") == "user":
            prompt_text = msg.get("content", "")
            break
    try:
        groq_messages = []
        if system_text:
            groq_messages.append({"role": "system", "content": system_text})
        groq_messages.append({"role": "user", "content": prompt_text})
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.1-8b-instant", "max_tokens": max_tokens, "messages": groq_messages},
            timeout=60
        )
        if not r.ok:
            return jsonify({"error": r.text}), r.status_code
        text = r.json()["choices"][0]["message"]["content"]
        return jsonify({"content": [{"type": "text", "text": text}], "model": "llama-3.1-8b-instant", "role": "assistant"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Geração de imagem via HuggingFace ──
@app.route("/gerar", methods=["POST"])
def gerar():
    data     = request.json or {}
    prompt   = data.get("prompt", "").strip()
    hf_token = data.get("hf_token", "").strip()
    width    = int(data.get("width",  1024))
    height   = int(data.get("height", 1024))
    if not prompt:
        return jsonify({"error": "Prompt vazio"}), 400
    if not hf_token:
        return jsonify({"error": "HuggingFace token não informado"}), 400
    try:
        r = requests.post(
            HF_URL,
            headers={"Authorization": f"Bearer {hf_token}"},
            json={"inputs": prompt, "parameters": {"width": width, "height": height, "num_inference_steps": 4}},
            timeout=120
        )
        if not r.ok:
            return jsonify({"error": r.text}), r.status_code
        b64 = base64.b64encode(r.content).decode("utf-8")
        return jsonify({"image": f"data:image/jpeg;base64,{b64}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Health check ──
@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "service": "BRG Studio API"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🎬 BRG Studio API — http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
