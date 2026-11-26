import urllib.request


def fetch_remote(endpoint, token):
    req = urllib.request.Request(
        endpoint,
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")


def sync_targets(targets, content):
    for target_path in targets:
        with open(target_path, "w", encoding="utf-8") as fh:
            fh.write(content)
