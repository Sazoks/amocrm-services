from typing import (
    Any,
    Iterator,
)
from seleniumwire import webdriver


class LocalStorage:
    """
    Класс-обертка для работы с localStorage клиента.
    """

    def __init__(self, driver: webdriver.Chrome) -> None:
        self.driver = driver

    def __len__(self) -> int:
        return self.driver.execute_script("return window.localStorage.length;")

    def items(self) -> dict[str, str]:
        return self.driver.execute_script(
            "var ls = window.localStorage, items = {}; "
            "for (var i = 0, k; i < ls.length; ++i) "
            "  items[k = ls.key(i)] = ls.getItem(k); "
            "return items; "
        )

    def keys(self) -> list[str]:
        return self.driver.execute_script(
            "var ls = window.localStorage, keys = []; "
            "for (var i = 0; i < ls.length; ++i) "
            "  keys[i] = ls.key(i); "
            "return keys; "
        )

    def get(self, key: str) -> str:
        return self.driver.execute_script(
            "return window.localStorage.getItem(arguments[0]);", key
        )

    def set(self, key: str, value: str) -> None:
        self.driver.execute_script(
            "window.localStorage.setItem(arguments[0], arguments[1]);", key, value
        )

    def has(self, key: str) -> bool:
        return key in self.keys()

    def remove(self, key: Any) -> None:
        self.driver.execute_script("window.localStorage.removeItem(arguments[0]);", key)

    def clear(self) -> None:
        self.driver.execute_script("window.localStorage.clear();")

    def __getitem__(self, key: str) -> str:
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key: str, value: str) -> None:
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        return key in self.keys()

    def __iter__(self) -> Iterator[str]:
        return self.items().__iter__()

    def __repr__(self) -> str:
        return self.items().__str__()
