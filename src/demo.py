"""Demo CLI untuk detektor serangan web (Task 7).

Mengklasifikasikan permintaan HTTP menggunakan model klasik dan opsi LLM lokal.
"""

import argparse
import sys

import joblib

from src.llm_classifier import classify_request


def predict_classic(request: str, pipeline) -> tuple[int, float]:
    """Prediksi label dan probabilitas serangan menggunakan pipeline klasik."""
    pred = int(pipeline.predict([request])[0])
    if hasattr(pipeline, "predict_proba"):
        proba = pipeline.predict_proba([request])[0]
        classes = list(getattr(pipeline, "classes_", [0, 1]))
        if 1 in classes:
            p_attack = float(proba[classes.index(1)])
        else:
            p_attack = 1.0 if pred == 1 else 0.0
    else:
        p_attack = 1.0 if pred == 1 else 0.0
    return pred, p_attack


def main(argv: list[str] | None = None) -> int:
    """Jalankan antarmuka baris perintah (CLI) untuk deteksi serangan web."""
    parser = argparse.ArgumentParser(description="Demo CLI Detektor Serangan Web")
    parser.add_argument("--request", type=str, required=True, help="Teks permintaan HTTP")
    parser.add_argument("--llm", action="store_true", help="Gunakan LLM lokal (Ollama) sebagai pembanding")
    parser.add_argument("--model-path", type=str, default="models/logreg.joblib", help="Path ke model klasik (.joblib)")

    args = parser.parse_args(argv)

    # Muat model klasik dan lakukan prediksi
    pipeline = joblib.load(args.model_path)
    label, prob = predict_classic(args.request, pipeline)
    verdict = "ATTACK" if label == 1 else "NORMAL"
    print(f"Model klasik: {verdict} (p={prob:.2f})")

    # Jika opsi LLM diaktifkan, jalankan klasifikasi via Ollama
    if args.llm:
        try:
            llm_label, duration = classify_request(args.request)
            if llm_label == 1:
                llm_verdict = "ATTACK"
            elif llm_label == 0:
                llm_verdict = "NORMAL"
            else:
                llm_verdict = "UNKNOWN"
            print(f"LLM: {llm_verdict} ({duration:.1f} s)")
        except RuntimeError as e:
            print(f"Peringatan: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
