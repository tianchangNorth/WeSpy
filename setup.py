from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='wespy',
    version='0.1.2',
    description='A Python tool for fetching web articles and converting them to Markdown format',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='tianchang',
    author_email='',
    url='https://github.com/tianchangNorth/WeSpy',
    packages=find_packages(),
    install_requires=[
        'requests>=2.20.0',
        'beautifulsoup4>=4.9.0',
    ],
    entry_points={
        'console_scripts': [
            'wespy = wespy.__main__:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Browsers',
        'Topic :: Text Processing :: Markup :: HTML',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    keywords='web scraping, article extraction, markdown converter, weixin',
)