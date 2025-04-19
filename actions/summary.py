from rouge_score import rouge_scorer

def evaluate_summary(summary: str, chunks: list[str]):
        synthetic_ref = " ".join([doc.page_content for doc in chunks])
        scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
        scores = scorer.score(synthetic_ref, summary)

        print("\n📊 ROUGE SCORE:")
        for key, val in scores.items():
            print(f"{key}: P={val.precision:.3f}, R={val.recall:.3f}, F1={val.fmeasure:.3f}")
        return scores