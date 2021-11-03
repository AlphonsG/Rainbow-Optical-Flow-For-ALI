import os
import shutil

from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.install import install

REQUIRED_PACKAGES = [
    'jupyterlab',
    'matplotlib',
    'moviepy',
    'natsort',
    'opencv-python',
    'pandas',
    'PIMS',
    'nd2reader',
    'PyYAML',
    'scikit-image',
    'tqdm',
    'ipympl',
    'einops',
    'pytest',
    'Gooey',
    'imutils'
]


def gooey_launcher_workaround():
    """Fix for https://github.com/chriskiehl/Gooey/issues/649"""
    if os.name != 'nt':
        return

    try:
        conda_prefix = os.environ['CONDA_PREFIX']
    except KeyError:
        return

    src = os.path.join(conda_prefix, 'Scripts', 'rainbow-script.py')
    dst = os.path.join(conda_prefix, 'Scripts', 'rainbow')
    try:
        shutil.copy2(src, dst)
    except IOError as e:
        msg = f'Could not apply Gooey Launcher bug workaround, reason: {e}'
        print(msg)


class PostDevelop(develop):
    """Pre-installation for development mode."""
    def run(self):
        develop.run(self)
        gooey_launcher_workaround()


class PostInstall(install):
    """Pre-installation for installation mode."""
    def run(self):
        install.run(self)
        gooey_launcher_workaround()


setup(
    name='rainbow',
    version='0.1.0',
    author='Alphons Gwatimba',
    author_email='alphonsg@protonmail.com',
    packages=find_packages(),
    url='https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI',
    license='LICENSE',
    description=('Automated air liquid interface cell culture analysis using '
                 'deep optical flow.'),
    long_description=open('README.md').read(),
    install_requires=REQUIRED_PACKAGES,
    entry_points={
        'console_scripts': [
            'rainbow = rainbow.__main__:main'
        ]
    },
    python_requires='>=3.6',
    cmdclass={
        'develop': PostDevelop,
        'install': PostInstall,
    }
)
