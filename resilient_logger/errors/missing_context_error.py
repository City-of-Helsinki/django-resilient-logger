class MissingContextError(Exception):
    def __init__(self, missing_fields: list[str]):
        self.missing_fields = missing_fields

    def __str__(self):
        entries = ",".join(self.missing_fields)
        return f"Log entry is missing required context entries: [{entries}]"
