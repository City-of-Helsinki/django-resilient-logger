class MissingContextError(Exception):
    missing_fields: list[str]

    def __init__(self, missing_fields):
        self.missing_fields = missing_fields

    def __str__(self):
        entries = ",".join(self.missing_fields)
        return f"Log entry is missing required context entries: [{entries}]"
