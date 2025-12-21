from hashlib import md5


def get_md5_bytes(data: bytes) -> str:
    return md5(data).hexdigest().upper()
