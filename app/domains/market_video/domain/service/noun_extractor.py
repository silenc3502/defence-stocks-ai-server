from collections import Counter

from kiwipiepy import Kiwi

from app.domains.market_video.domain.service.synonym_merger import merge_synonyms

_kiwi = Kiwi()

MIN_NOUN_LENGTH = 2
STOPWORDS = {
    "것", "거", "수", "때", "말", "분", "중", "더", "안", "좀",
    "그", "이", "저", "뭐", "왜", "어디", "누구", "언제",
    "진짜", "정말", "완전", "그냥", "계속", "지금", "우리",
    "사람", "얘기", "이야기", "생각", "느낌", "부분", "정도",
}


def extract_nouns(texts: list[str]) -> list[tuple[str, int]]:
    all_nouns = []

    for text in texts:
        tokens = _kiwi.tokenize(text)
        nouns = [
            t.form for t in tokens
            if t.tag.startswith("NN")
            and len(t.form) >= MIN_NOUN_LENGTH
            and t.form not in STOPWORDS
        ]
        all_nouns.extend(nouns)

    counter = Counter(all_nouns)
    raw_counts = counter.most_common()

    return merge_synonyms(raw_counts)
