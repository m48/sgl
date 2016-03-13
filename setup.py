import setuptools
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(here, 'README.rst')
readme_text = codecs.open(path, encoding='utf-8').read()

setuptools.setup(
    name="sgl",
    version="0.0.1.dev1",
    # Valid version cheat sheet:
    # 1.2.0.dev1   Development release
    # 1.2.0a1      Alpha Release
    # 1.2.0b1      Beta Release
    # 1.2.0rc1     Release Candidate
    # 1.2.0        Final Release
    # 1.2.0.post1  Post Release

    description="A backend agnostic python game framework.",
    long_description=readme_text,

    author="m48",
    author_email="matson48@gmx.com",

    license="LGPL",

    packages=setuptools.find_packages(), # exclude=[]),

    package_data={
        '': ['*.txt', '*.png'],
    },

    install_requires=["pygame"],

    extras_require={
        "extra": ["Pillow", "numpy"],
        "HTML5": ["pyjs"],
        "video": ["moviepy"],
    },

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 1 - Planning",

        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",

        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",

        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",

        "Topic :: Artistic Software",
        "Topic :: Education",
        "Topic :: Games/Entertainment",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: System :: Software Distribution",
    ],

    keywords="pygame game graphics multimedia development framework",
)
