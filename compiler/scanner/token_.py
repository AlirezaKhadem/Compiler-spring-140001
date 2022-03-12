from .patterns import REVERSED_REGEX


class Token:
    def __init__(self, token_type, token_value, define=None):
        self.token_value = token_value
        if token_type == "RESERVED_OR_ID":
            if token_value in REVERSED_REGEX:
                if token_value in ["true", "false"]:
                    token_type = "T_BOOLEANLITERAL"
                else:
                    token_type = ""
            else:
                token_type = "T_ID"
        self.token_type = token_type
        self.define = define

    def __str__(self):
        if not self.token_type:
            return self.token_value
        return self.token_type + ' ' + self.token_value
