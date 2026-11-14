"""
Klasifikasi permintaan HTTP menggunakan LLM lokal via Ollama (Task 5).
Payload hanya diklasifikasikan, tidak pernah dijalankan atau dikirim ke sistem lain.
"""

import time

import requests

from src.config import (
    LLM_TIMEOUT_S,
    MAX_REQUEST_CHARS,
    OLLAMA_HOST,
    OLLAMA_MODEL,
)


def build_prompt(request: str) -> str:
    """Potong permintaan ke MAX_REQUEST_CHARS lalu susun prompt yang meminta satu kata NORMAL atau ATTACK."""
    potongan = request[:MAX_REQUEST_CHARS]
    prompt = (
        "Kamu adalah detektor serangan web. "
        "Klasifikasikan permintaan HTTP berikut sebagai NORMAL atau ATTACK. "
        "Jawab HANYA dengan satu kata: NORMAL atau ATTACK.\n\n"
        f"Permintaan:\n{potongan}"
    )
    return prompt


def parse_label(raw: str) -> int | None:
    """Ambil token pertama dari respons LLM: ATTACK→1, NORMAL→0, selain itu→None."""
    # Ambil token pertama (kata pertama) lalu bandingkan tanpa membedakan huruf besar/kecil
    token = raw.strip().split()[0].upper() if raw.strip() else ""
    # Hapus tanda baca di akhir token (misalnya "ATTACK." atau "NORMAL,")
    token = token.rstrip(".,!?:")
    if token == "ATTACK":
        return 1
    if token == "NORMAL":
        return 0
    return None


def classify_request(request: str, model: str = OLLAMA_MODEL) -> tuple[int | None, float]:
    """Kirim permintaan ke Ollama dan kembalikan (label, detik); ConnectionError diubah jadi RuntimeError."""
    prompt = build_prompt(request)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 5,
        },
    }

    mulai = time.monotonic()
    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=LLM_TIMEOUT_S,
        )
        resp.raise_for_status()
    except requests.ConnectionError:
        raise RuntimeError(f"Ollama tidak berjalan di {OLLAMA_HOST}")
    selesai = time.monotonic() - mulai

    data = resp.json()
    raw_text = data.get("response", "")
    label = parse_label(raw_text)

    return label, selesai
