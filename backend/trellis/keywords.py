"""Extract and rank one-to-three-word keyword candidates from scraped pages."""

import re
from collections import Counter
from dataclasses import dataclass

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer


TOKEN_PATTERN = re.compile(r"[a-z][a-z0-9'-]{1,}")


@dataclass(frozen=True)
class KeywordResult:
    phrase: str
    frequency: int
    tfidf_score: float


def tokenize(text: str) -> list[str]:
    return [token for token in TOKEN_PATTERN.findall(text.lower()) if token not in ENGLISH_STOP_WORDS]


def ngrams(tokens: list[str], size: int) -> list[str]:
    return [" ".join(tokens[index:index + size]) for index in range(len(tokens) - size + 1)]


def extract_keywords(page_texts: list[str], limit: int = 100) -> list[KeywordResult]:
    """Rank candidates by frequency and TF-IDF, filtering uniform boilerplate."""

    tokenized_documents = [tokenize(text) for text in page_texts]
    documents = [" ".join(tokens) for tokens in tokenized_documents if tokens]
    if not documents:
        return []

    page_counts: list[Counter[str]] = []
    total_counts: Counter[str] = Counter()
    for document in documents:
        tokens = document.split()
        counts: Counter[str] = Counter()
        for size in (1, 2, 3):
            counts.update(ngrams(tokens, size))
        page_counts.append(counts)
        total_counts.update(counts)

    vectorizer = TfidfVectorizer(ngram_range=(1, 3), token_pattern=r"(?u)\b[a-z][a-z0-9'-]+\b")
    matrix = vectorizer.fit_transform(documents)
    features = vectorizer.get_feature_names_out()
    tfidf_scores = dict(zip(features, matrix.max(axis=0).toarray().ravel(), strict=True))

    results: list[KeywordResult] = []
    for phrase, frequency in total_counts.items():
        occurrences = [counts.get(phrase, 0) for counts in page_counts]
        # Shared phrases with effectively identical counts are navigation/footer boilerplate.
        if len(documents) > 1 and all(occurrences) and max(occurrences) - min(occurrences) <= 1:
            continue
        results.append(KeywordResult(phrase, frequency, float(tfidf_scores.get(phrase, 0.0))))

    return sorted(results, key=lambda item: (-item.frequency, -item.tfidf_score, item.phrase))[:limit]
