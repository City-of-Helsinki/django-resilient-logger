from typing import List


class MissingContextError(Exception):
    missing_fields: List[str]

    def __init__(self, missing_fields):
        self.missing_fields = missing_fields

    def __str__(self):
        return f"Log entry is missing required context entries: [{','.join(self.missing_fields)}]"
