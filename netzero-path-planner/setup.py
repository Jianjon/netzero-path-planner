from setuptools import setup, find_packages

setup(
    name='netzero-path-planner',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A web application for simulating corporate carbon reduction strategies.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'streamlit',
        'pandas',
        'matplotlib',
        'plotly',
        'pyyaml',
        'openpyxl',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)