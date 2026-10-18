from setuptools import setup, find_packages

setup(
    name="cyberium-cli",
    version="1.0.0",
    description="Cyberium Academy Terminal Client & Live Submission CLI",
    author="Denis Albin",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "cyberium=cyberium.cli:main",
            "cyberium-tui=cyberium.tui:start_tui",
        ],
    },
    python_requires=">=3.8",
)
