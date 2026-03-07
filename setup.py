from setuptools import setup, find_packages

setup(
    name="pdf-numbering-tool",
    version="0.1.0",
    description="Merge and add page numbers to PDFs",
    author="soopn",
    # root modules
    py_modules=["pdfjoin", "utilities"],
    install_requires=["reportlab", "pypdf"],
    python_requires=">=3.9",
)
