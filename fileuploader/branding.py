BANNER = r"""
  ______ _ _      _    _       _                 _
 |  ____(_) |    | |  | |     | |               | |
 | |__   _| | ___| |  | |_ __ | | ___   __ _  __| | ___ _ __
 |  __| | | |/ _ \ |  | | '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|
 | |    | | |  __/ |__| | |_) | | (_) | (_| | (_| |  __/ |
 |_|    |_|_|\___|\____/| .__/|_|\___/ \__,_|\__,_|\___|_|
                        | |
                        |_|
"""

CREDIT_NAME = "j0rd1s3rr4n0"
CREDIT_SITE = "jordiserrano.me"
CREDIT_GITHUB = "github.com/j0rd1s3rr4n0"
CREDIT_LINE = f"by {CREDIT_NAME} | {CREDIT_SITE} | {CREDIT_GITHUB}"


def banner_text() -> str:
    return BANNER.strip("\n") + "\n" + CREDIT_LINE


def compact_credit() -> str:
    return CREDIT_LINE
