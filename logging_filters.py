import logging
import re
from typing import Optional


EMAIL_RE = re.compile(r"([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")


class EmailObfuscationFilter(logging.Filter):
    """Logging filter that obfuscates email addresses in LogRecord messages.

    Behavior:
    - Masks the local-part of any email addresses found in the formatted message
      or in record.msg/record.args by replacing all but the first `show_local`
      characters with asterisks (or hides entirely in production).

    Configurable via dictConfig by passing `show_local` (int) and
    `replacement` (str).
    """

    def __init__(self, show_local: Optional[int] = 1, replacement: str = "***"):
        super().__init__()
        try:
            self.show_local = int(show_local)
        except Exception:
            self.show_local = 1
        self.replacement = replacement or "***"

    def _obfuscate_match(self, m: re.Match) -> str:
        local = m.group(1)
        domain = m.group(2)
        if self.show_local <= 0:
            obf_local = self.replacement
        elif len(local) <= self.show_local:
            obf_local = local[0:self.show_local]
        else:
            obf_local = local[0:self.show_local] + self.replacement
        return f"{obf_local}@{domain}"

    def obfuscate(self, text: str) -> str:
        if not text:
            return text
        # Replace any email-like patterns
        return EMAIL_RE.sub(self._obfuscate_match, text)

    def filter(self, record: logging.LogRecord) -> bool:
        # Obfuscate the message (if it's a string). We try to handle both
        # record.msg (which may be the format string) and record.getMessage().
        try:
            if isinstance(record.msg, str):
                record.msg = self.obfuscate(record.msg)

            # If args are present, attempt to obfuscate string args so that
            # formatting won't reintroduce cleartext emails.
            if record.args:
                if isinstance(record.args, tuple):
                    record.args = tuple(self.obfuscate(a) if isinstance(a, str) else a for a in record.args)
                elif isinstance(record.args, dict):
                    record.args = {k: (self.obfuscate(v) if isinstance(v, str) else v) for k, v in record.args.items()}

            # Also attempt to obfuscate commonly used attributes
            for attr in ("message", "msg", "name"):
                val = getattr(record, attr, None)
                if isinstance(val, str) and EMAIL_RE.search(val):
                    setattr(record, attr, self.obfuscate(val))
        except Exception:
            # Never let logging break the application; on error, allow the
            # original record through.
            pass

        return True
