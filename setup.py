from setuptools import setup, find_packages
import os

# Читаем README.md для long_description
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='TelegramTextApp',
    version='0.0.8.8',
    packages=find_packages(),
    install_requires=[
        'pyTelegramBotAPI',
        'pytz',
    ],
    entry_points={
        'console_scripts': [
            'TTA=TelegramTextApp.create_bot:create',
        ],
    },
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Falbue",
    author_email="cyansair05@gmail.com",
    description="Telegram Text App",
    url="https://github.com/Falbue/TelegramTextApp",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
