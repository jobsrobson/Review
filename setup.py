from setuptools import setup, find_packages

setup(
    name='review',
    version='2.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'PyGObject>=3.42.0',
        'cryptography>=42.0.0',
    ],
    entry_points={
        'console_scripts': [
            'review=main:main',
        ],
    },
    package_data={
        'review': [
            'icons/*.svg',
            'icons/*.png',
        ],
    },
    author='Robson Ricardo',
    description='Spaced Repetition Study Manager',
    long_description=open('README.md').read() if __import__('os').path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    url='https://github.com/jobsr/Review',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.10',
)
