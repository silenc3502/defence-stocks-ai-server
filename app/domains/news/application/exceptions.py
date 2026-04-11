class DuplicateInterestArticleError(Exception):
    """동일 사용자가 동일 링크의 기사를 중복 저장하려 할 때 발생한다."""


class InterestArticleContentPersistError(Exception):
    """관심 기사 본문(PostgreSQL) 저장 실패. MySQL 메타데이터는 롤백된다."""


class ArticleFetchError(Exception):
    """기사 원문 링크 접근/파싱 실패."""
