from setuptools import find_packages, setup

REQUIRED_PACKAGES = [
    'jupyterlab',
    'matplotlib',
    'natsort',
    'numpy==1.18.5',
    'opencv-python',
    'pandas',
    'PIMS',
    'pims-nd2==1.0',
    'PyYAML',
    'scikit-image',
    'tensorflow==1.15.5',
    'tqdm'
]

setup(
    name='rainbow',
    version='0.1.0',
    author='Alphons Gwatimba',
    author_email='alphonsg@protonmail.com',
    packages=find_packages(),
    url=('https://github.com/AlphonsGwatimba/Automated-Air-Liquid-Interface-'
         'Cell-Culture-Analysis-Using-Deep-Optical-Flow'),
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
    python_requires='==3.7.*'
)
