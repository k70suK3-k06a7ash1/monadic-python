from typing import TypeVar, Generic, Callable, Optional, Iterable 

# --- Monad-Compliant Maybe Class (from previous answer) ---
T = TypeVar('T')
U = TypeVar('U')

class Maybe(Generic[T]):
    """
    Maybe Monadの実装。値が存在する (Just) か、存在しない (Nothing) かを表す。
    """
    def __init__(self, value: Optional[T], is_just: bool):
        self._value = value
        self._is_just = is_just

    @classmethod
    def just(cls, value: T) -> 'Maybe[T]':
        if value is None:
            raise ValueError("Cannot create Just(None). Use Maybe.nothing() for absence of value.")
        return cls(value, True)

    @classmethod
    def nothing(cls) -> 'Maybe[Any]': # Nothing は任意の型に適合するように Any を使う
        # シングルトン実装も可能だが、簡単のため毎回生成
        return cls(None, False)

    def is_just(self) -> bool:
        return self._is_just

    def is_nothing(self) -> bool:
        return not self._is_just

    def bind(self, func: Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        if self.is_just():
            try:
                result = func(self._value)
                if not isinstance(result, Maybe):
                    raise TypeError(f"The function passed to bind must return a Maybe instance, but got {type(result)}")
                return result
            except Exception as e:
                print(f"Warning: Exception during bind operation: {e}. Returning Nothing.")
                return Maybe.nothing()
        else:
            return Maybe.nothing()

    def map(self, func: Callable[[T], U]) -> 'Maybe[U]':
        if self.is_just():
            try:
                mapped_value = func(self._value)
                if mapped_value is None:
                     return Maybe.nothing()
                return Maybe.just(mapped_value)
            except Exception as e:
                print(f"Warning: Exception during map operation: {e}. Returning Nothing.")
                return Maybe.nothing()
        else:
            return Maybe.nothing()

    def get_or_else(self, default: T) -> T:
        return self._value if self.is_just() else default

    def get_or_raise(self, exception: Exception = ValueError("Cannot get value from Nothing")) -> T:
        if self.is_just():
            return self._value
        else:
            raise exception

    def __or__(self, other: 'Maybe[T]') -> 'Maybe[T]':
        return self if self.is_just() else other

    def __str__(self) -> str:
        return f"Just({self._value})" if self.is_just() else "Nothing"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other) -> bool:
        if isinstance(other, Maybe):
            return self._is_just == other._is_just and self._value == other._value
        return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __bool__(self) -> bool:
        return self.is_just()
