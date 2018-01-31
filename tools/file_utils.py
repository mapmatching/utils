# coding: utf-8
import hashlib


def md5(file_path):
    sh_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sh_md5.update(chunk)
    return sh_md5.hexdigest()
