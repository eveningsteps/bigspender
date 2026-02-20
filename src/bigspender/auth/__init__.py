import sys

import browser_cookie3


def cookies_for_domains(*domains):
    cookies = {}
    for domain in domains:
        cc = browser_cookie3.firefox(domain_name=domain)
        cookies.update({c.name: c.value for c in cc})
    print(f"found {len(cookies)} cookie(s) for {domains}", file=sys.stderr)
    return cookies
