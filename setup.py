from setuptools import setup

setup(
    name='monipy',
    description='A tool for monitoring multiple files in the same terminal',
    url='https://github.com/miicck/monipy',
    author='Michael Hutcheon',
    author_email='michael.hutcheon@hotmail.co.uk',
    exclude=["build*"],
    packages=setuptools.find_namespace_packages(),
    python_requires='>=3',
    install_requires=[],
    entry_points={
        "console_scripts": [
            "monipy = monipy.main:main",
        ]
    }
)
