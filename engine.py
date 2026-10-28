import re
import pandas as pd

CRIT = {"Critical": 30, "High": 20, "Medium": 10, "Low": 5}
STOPWORDS = {"the","and","or","to","of","a","an","for","with","in","on","is","are","be","this","that","from","into","can","will","modify","change","logic","o2c"}

def tokenize(text):
    return {t for t in re.findall(r"[a-z0-9-]+", str(text).lower()) if len(t) > 2 and t not in STOPWORDS}

def pre_score_tests(df: pd.DataFrame, change_text: str) -> pd.DataFrame:
    change_tokens = tokenize(change_text)
    out = df.copy()
    scores, overlaps = [], []
    for _, row in out.iterrows():
        corpus = " ".join([str(row.get("process","")), str(row.get("description","")), str(row.get("tags",""))])
        test_tokens = tokenize(corpus)
        overlap = sorted(change_tokens.intersection(test_tokens))
        score = CRIT.get(str(row.get("criticality","Medium")), 10)
        if str(row.get("financial_impact","No")).strip().lower() in {"yes","true","1"}:
            score += 20
        try:
            score += min(int(row.get("historical_defects",0))*2, 16)
        except Exception:
            pass
        score += min(len(overlap)*6, 24)
        scores.append(min(score,100))
        overlaps.append(", ".join(overlap) if overlap else "none")
    out["pre_score"] = scores
    out["keyword_overlap"] = overlaps
    return out.sort_values("pre_score", ascending=False)
