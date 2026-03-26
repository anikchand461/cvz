"""
setup.py
Overrides the pip install command to auto-download en_core_web_md
immediately after the package is installed — no manual step needed.
"""

import subprocess
import sys
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop


def _download_spacy_model():
    """Download en_core_web_md if not already present."""
    try:
        import spacy
        spacy.load("en_core_web_md")
        print("✔ spaCy model en_core_web_md already installed — skipping download.")
    except OSError:
        print("⬇ Downloading spaCy model en_core_web_md (~43 MB)...")
        result = subprocess.run(
            [sys.executable, "-m", "spacy", "download", "en_core_web_md"],
            check=False,
        )
        if result.returncode == 0:
            print("✔ en_core_web_md downloaded successfully.")
        else:
            print(
                "⚠ spaCy model download failed. "
                "Run manually: python -m spacy download en_core_web_md"
            )


class PostInstall(install):
    """pip install cvscan  →  also pulls the spaCy model."""
    def run(self):
        super().run()
        _download_spacy_model()


class PostDevelop(develop):
    """pip install -e .  →  also pulls the spaCy model."""
    def run(self):
        super().run()
        _download_spacy_model()


setup(
    cmdclass={
        "install": PostInstall,
        "develop": PostDevelop,
    },
)
