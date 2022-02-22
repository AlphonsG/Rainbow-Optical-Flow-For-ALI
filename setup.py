from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.install import install

REQUIRED_PACKAGES = [
    'moviepy',
    'matplotlib',
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
    'imutils',
    'astropy',
    'physt',
    'jupyterlab'
]


class PostDevelop(develop):
    """Pre-installation for development mode."""
    def run(self):
        develop.run(self)


class PostInstall(install):
    """Pre-installation for installation mode."""
    def run(self):
        install.run(self)


setup(
    name='rainbow',
    author='Alphons Gwatimba',
    author_email='alphonsg@protonmail.com',
    packages=find_packages(),
    url='https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI',
    license='MIT',
    description=('Automated air liquid interface cell culture analysis using '
                 'deep optical flow.'),
    long_description=open('README.md', encoding='UTF-8').read(),
    install_requires=REQUIRED_PACKAGES,
    entry_points={
        'console_scripts': [
            'rainbow = rainbow.__main__:main'
        ]
    },
    python_requires='>=3.8',
    cmdclass={
        'develop': PostDevelop,
        'install': PostInstall,
    },
    use_calver=True,
    setup_requires=['calver']
)
