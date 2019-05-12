from typing import List

from ...requests import Request
from ...resolvers import Resolver
from .._resolvable_matcher import ResolvableMatcher
from ._logical_matcher import LogicalMatcher

__all__ = ("AllMatcher",)


class AllMatcher(LogicalMatcher):
    def __init__(self, matchers: List[ResolvableMatcher], *, resolver: Resolver) -> None:
        super().__init__(resolver=resolver)
        assert len(matchers) > 0
        self._matchers = matchers

    async def match(self, request: Request) -> bool:
        for matcher in self._matchers:
            if not await matcher.match(request):
                return False
        return True

    def __repr__(self) -> str:
        return (f"{self.__class__.__qualname__}"
                f"({self._matchers!r}, resolver={self._resolver!r})")
