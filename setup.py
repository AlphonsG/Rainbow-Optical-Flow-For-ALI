from setuptools import find_packages, setup

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
    'jupyterlab',
    'physt',
    'bumpver',
    'Pillow < 9.1.0 ; platform_system=="Darwin"'
]

CLASSIFIERS = [
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Operating System :: OS Independent',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: MacOS',
    'Operating System :: POSIX :: Linux',
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Science/Research',
    'Natural Language :: English',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'Topic :: Scientific/Engineering :: Image Processing',
    'Topic :: Scientific/Engineering :: Visualization',
]

setup(
    name='rainbow-optical-flow',
    author='Alphons Gwatimba',
    author_email='0go0vdp95@mozmail.com',
    packages=find_packages(exclude=['tests*']) + ['misc'],
    version="2022.4.7",
    url='https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI',
    license='MIT',
    classifiers=CLASSIFIERS,
    description=('Automated air liquid interface cell culture analysis using '
                 'deep optical flow.'),
    long_description=open('README.md', encoding='UTF-8').read(),
    long_description_content_type='text/markdown',
    install_requires=REQUIRED_PACKAGES,
    entry_points={
        'console_scripts': [
            'rainbow = rainbow.__main__:main'
        ]
    },
    python_requires='>=3.8',
    include_package_data=True,
    setup_requires=['wheel', 'setuptools']
)
