"""
Evaluación del pipeline RAG con Ragas (estilo práctica de clase).
Métricas: faithfulness, answer_relevancy, context_precision, context_recall.

Uso:
    python -m eval.run_ragas
    python -m eval.run_ragas --top_k 6 --run_name topk6
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from datasets import Dataset

from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.rag_chain import (
    rag_pipeline,
    parse_json_safe,
    get_embeddings,
    get_llm,
    TOP_K,
)

load_dotenv()

EVAL_PATH = Path(__file__).resolve().parent / "eval_dataset.json"
RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def load_eval_set():
    with open(EVAL_PATH, encoding="utf-8") as f:
        return json.load(f)


def run_rag_on_dataset(items, top_k: int = TOP_K):
    """Ejecuta el RAG sobre cada pregunta y recolecta contextos + respuestas."""
    questions, answers, contexts, ground_truths = [], [], [], []

    for i, item in enumerate(items):
        q = item["question"]
        gt = item["ground_truth"]
        print(f"[{i+1}/{len(items)}] {q[:60]}...")

        try:
            result = rag_pipeline(q, k=top_k)
            raw_ans = result["respuesta"]
            parsed = parse_json_safe(raw_ans)

            if parsed.get("diagnostico", "").startswith("No encuentro"):
                answer_text = parsed["diagnostico"]
            else:
                parts = [parsed.get("diagnostico", "")]
                if parsed.get("pasos_solucion"):
                    parts.append("Pasos: " + "; ".join(parsed["pasos_solucion"]))
                if parsed.get("comandos"):
                    parts.append("Comandos: " + "; ".join(parsed["comandos"]))
                if parsed.get("advertencias"):
                    parts.append("Advertencias: " + "; ".join(parsed["advertencias"]))
                answer_text = " | ".join(p for p in parts if p)

            ctx_list = [d.page_content for d in result["fragmentos"]]
        except Exception as e:
            print(f"  ERROR: {e}")
            answer_text = "Error en la generación"
            ctx_list = []

        questions.append(q)
        answers.append(answer_text)
        contexts.append(ctx_list)
        ground_truths.append(gt)

    return {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    }


def evaluate_rag(dataset_dict, run_name: str = "baseline"):
    """Ejecuta Ragas y guarda resultados."""
    ds = Dataset.from_dict(dataset_dict)

    llm = get_llm()
    embeddings = get_embeddings()
    llm_juez = LangchainLLMWrapper(llm)
    emb_juez = LangchainEmbeddingsWrapper(embeddings)

    metrics = [faithfulness, answer_relevancy, context_precision, context_recall]

    print("\nEjecutando evaluación Ragas (consume tokens de Groq)...")
    result = evaluate(
        ds,
        metrics=metrics,
        llm=llm_juez,
        embeddings=emb_juez,
    )

    df = result.to_pandas()
    summary = {
        "run_name": run_name,
        "timestamp": datetime.now().isoformat(),
        "n_samples": len(dataset_dict["question"]),
        "faithfulness": float(df["faithfulness"].mean()) if "faithfulness" in df else None,
        "answer_relevancy": float(df["answer_relevancy"].mean()) if "answer_relevancy" in df else None,
        "context_precision": float(df["context_precision"].mean()) if "context_precision" in df else None,
        "context_recall": float(df["context_recall"].mean()) if "context_recall" in df else None,
    }

    out_csv = RESULTS_DIR / f"ragas_{run_name}.csv"
    out_json = RESULTS_DIR / f"ragas_{run_name}_summary.json"
    df.to_csv(out_csv, index=False)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n=== Resultados Ragas ===")
    for k, v in summary.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")
    print(f"\nDetalle guardado en {out_csv}")
    return summary, df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--top_k", type=int, default=TOP_K)
    parser.add_argument("--run_name", type=str, default="baseline")
    args = parser.parse_args()

    items = load_eval_set()
    print(f"Cargadas {len(items)} preguntas de evaluación (top_k={args.top_k})")
    data = run_rag_on_dataset(items, top_k=args.top_k)
    evaluate_rag(data, run_name=args.run_name)


if __name__ == "__main__":
    main()
