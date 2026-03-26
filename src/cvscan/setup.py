def download_model():
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_md"], check=True)
