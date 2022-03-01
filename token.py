from patterns import REVERSED_REGEX


class Token:
    def __init__(self, token_type, token_value):
        self.token_value = token_value
        if token_type == "RESERVED_OR_ID":
            if token_value in REVERSED_REGEX:
                if token_value in ["true", "false"]:
                    token_type = "T_BOOLEANLITERAL"
                else:
                    token_type = token_value
            else:
                token_type = "T_ID"
        self.token_type = token_type
