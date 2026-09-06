from trellis.keywords import extract_keywords, ngrams, tokenize


def test_tokenize_and_build_unigrams_bigrams_and_trigrams() -> None:
    tokens = tokenize("Practical community garden planning")
    assert tokens == ["practical", "community", "garden", "planning"]
    assert ngrams(tokens, 1) == tokens
    assert "community garden" in ngrams(tokens, 2)
    assert "community garden planning" in ngrams(tokens, 3)


def test_frequency_is_primary_ranking_signal() -> None:
    results = extract_keywords(["garden garden garden compost compost native seeds"])
    assert results[0].phrase == "garden"
    assert results[0].frequency == 3
    assert next(result for result in results if result.phrase == "compost").frequency == 2


def test_multi_page_tfidf_filters_uniform_boilerplate() -> None:
    results = extract_keywords([
        "home programs donate native seed library pollinator habitat",
        "home programs donate compost workshop soil health compost",
        "home programs donate youth garden education planting",
    ])
    phrases = {result.phrase for result in results}
    assert "home" not in phrases
    assert "home programs donate" not in phrases
    assert "compost" in phrases
    assert "native seed library" in phrases


def test_empty_pages_return_no_keywords() -> None:
    assert extract_keywords(["", "the and or"]) == []
