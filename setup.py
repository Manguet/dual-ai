from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="dual-ai-orchestrator",
    version="1.0.0",
    author="Dual AI Contributors",
    author_email="contact@dual-ai.dev",
    description="Un orchestrateur intelligent qui unifie Claude Code et Gemini Code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dual-ai-orchestrator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rich>=13.0.0",
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "click>=8.1.0",
        "colorama>=0.4.6",
        "pathlib>=1.0.1",
    ],
    entry_points={
        "console_scripts": [
            "dual-ai=dual_ai.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)