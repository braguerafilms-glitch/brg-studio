#!/usr/bin/env python3
"""
BRG Studio — Backend de Produção
Deploy: Railway / Render / Fly.io
"""

import os
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Em produção o frontend é servido pelo Vercel — libera o domínio deles
# Em dev libera localhost
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:8080,http://localhost:5000").split(",")
CORS(app, origins=ALLOWED_ORIGINS)

# API keys via variável de ambiente (nunca hardcoded em produção)
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "")

HF_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"

# ── Geração de imagem ──
@app.route("/gerar", methods=["POST"])
def gerar():
    data      = request.json or {}
    prompt    = data.get("prompt", "").strip()
    hf_token  = data.get("hf_token", "").strip()   # cliente manda a própria key
    width     = int(data.get("width",  1024))
    height    = int(data.get("height", 1024))

    if not prompt:
        return jsonify({"error": "Prompt vazio"}), 400
    if not hf_token:
        return jsonify({"error": "HuggingFace token não informado"}), 400

    try:
        r = requests.post(
            HF_URL,
            headers={"Authorization": f"Bearer {hf_token}"},
            json={"inputs": prompt, "parameters": {
                "width": width, "height": height, "num_inference_steps": 4
            }},
            timeout=120
        )
        if not r.ok:
            return jsonify({"error": r.text}), r.status_code

        b64 = base64.b64encode(r.content).decode("utf-8")
        return jsonify({"image": f"data:image/jpeg;base64,{b64}"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Proxy Groq (IA de texto — gratuito) ──
GROQ_KEY = os.environ.get("GROQ_KEY", "")

@app.route("/ia", methods=["POST"])
def ia():
    data = request.json or {}
    prompt_text = ""
    for msg in data.get("messages", []):
        if msg.get("role") == "user":
            prompt_text = msg.get("content", "")
            break
    system_text = data.get("system", "")
    max_tokens  = data.get("max_tokens", 1000)

    try:
        groq_payload = {
            "model": "llama-3.1-8b-instant",
            "max_tokens": max_tokens,
            "messages": []
        }
        if system_text:
            groq_payload["messages"].append({"role": "system", "content": system_text})
        groq_payload["messages"].append({"role": "user", "content": prompt_text})

        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_KEY}",
                "Content-Type": "application/json"
            },
            json=groq_payload,
            timeout=60
        )
        if not r.ok:
            return jsonify({"error": r.text}), r.status_code

        groq_data = r.json()
        text = groq_data["choices"][0]["message"]["content"]

        # Return in Anthropic format so frontend doesn't need changes
        return jsonify({
            "content": [{"type": "text", "text": text}],
            "model": "llama-3.1-8b-instant",
            "role": "assistant"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Health check ──
@app.route("/ia", methods=["POST"])
def ia():
    data = request.json or {}
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json=data,
            timeout=60
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "service": "BRG Studio API"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🎬 BRG Studio API — http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
