# Rainbow

![](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macOS-lightgrey)
![](https://img.shields.io/github/languages/top/AlphonsG/Rainbow-Optical-Flow-For-ALI)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python package](https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/actions/workflows/python-package.yaml/badge.svg?branch=dev2)](https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/actions/workflows/python-package.yaml)

![](misc/images/banner_img.png?raw=true "Rainbow")

Repository for software detailed in 'Automated Air-Liquid Interface Cell Culture Analysis Using Deep Optical Flow' software paper. See Abstract [below](#software-paper-abstract) for more details.

## Table of contents
1. [Installation](#installation)
2. [Usage](#usage)
3. [Additional Information](#additional-information)
4. [Examples](#examples)
6. [Community Guidelines](#community-guidelines)
7. [License](#license)
9. [Software Paper](#software-paper-abstract)
10. [Our Team](#our-team)
11. [Acknowledgements](#acknowledgements)

## Installation <a name="installation"></a>

Rainbow can be installed on Linux, Windows & macOS and supports Python 3.6 and up. We recommend installing and running Rainbow within a virtual environment. Although it is not a requirement, we also recommend installing and running Rainbow on a GPU-enabled system to minimize processing times.

1. Download and install [Miniconda3](https://docs.conda.io/en/latest/miniconda.html). Detailed official installation instructions can be found [here](https://conda.io/projects/conda/en/latest/user-guide/install/index.html), if needed.

2. Launch the terminal (*Linux* and *macOS* users) or start the program 'Anaconda Prompt (miniconda3)' (*Windows* users). The proceeding commands will be entered into the opened window.


3. Create and prepare a virtual environment with Python 3.8 called 'rainbow_env':

   ```
   conda create -n rainbow_env python=3.8 git git-lfs

   conda activate rainbow_env

   git lfs install
   ```


4. Clone this repository into your desired directory:

   ```git clone https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI.git```

5. Navigate into the cloned directory:

    ```cd Rainbow-Optical-Flow-For-ALI```

6. Install Rainbow:

   ```python setup.py install```

7. Install PyTorch by specifying your system configuration using the official [PyTorch get started tool](https://pytorch.org/get-started/locally/) and running the generated command:
   <p style="text-align:center;">
    <img src="misc/images/pytorch_get_started.png" width="750" alt="centered image" />
    </p>
   For example, Linux users without a GPU (i.e. CPU only) will run:

   ```conda install pytorch torchvision torchaudio cpuonly -c pytorch```

8. Finalize the installation by running the following commands:

   ```
   git submodule sync

   git submodule update --init --recursive
   ```

- Note: Virtual environment can be deactivated using:

   ```conda deactivate```

## Usage <a name="usage"></a>

### Command Line Interface (CLI)

Rainbow can be used rainbow through a CLI. Run `rainbow --help` or `rainbow -h` within the `rainbow_env` environment for a list of available command arguments and descriptions.

To test rainbow using the provided Air-Liquid Interface cell culture example image series, run the following command from within the cloned repository directory:

`rainbow examples/example_image_series misc/configs/default_config.yaml`

After processing is finished, a folder containing similar outputs (e.g. a HTML report,  videos, images, CSV files) to those in [this](examples/example_output/(tif)_191018_HNA-ALI_d14.nd2_-_191018_HNA-ALI_d14.nd2_(series_03)0000_etc) example output folder should be generated in `examples/example_image_series`.
### Graphical User Interface (GUI)

Rainbow can be also be used through a GUI, which can be launched by running the command `rainbow` within the `rainbow_env` environment.

To test rainbow using the provided Air-Liquid Interface cell culture example image series, select `examples/example_image_series` as the input image series and `misc/configs/default_config.yaml`  as the configuration file in the GUI under 'Required Arguments'. After processing is finished, a folder containing similar outputs (e.g. a HTML report,  videos, images, CSV files) to those in [this](examples/example_output/(tif)_191018_HNA-ALI_d14.nd2_-_191018_HNA-ALI_d14.nd2_(series_03)0000_etc) example output folder should be generated in `examples/example_image_series`.

## Additional Information <a name="additional-information"></a>

### Optical Flow

Rainbow uses a deep learning model called [GMA](https://arxiv.org/abs/2104.02409) to compute the optical flow in an image series. This model can be replaced with any other method for computing optical flow by writing a custom class that implements the [base_model](rainbow/optical_flow/base_model.py) interface ([gma.py](rainbow/optical_flow/gma.py) is an example of that).

### Analysis

Rainbow can automatically generate an analysis report after computing the optical flow in an image series. A base report file that can be modified is provided [here](misc/notebooks/report.ipynb) as a Jupyter notebook. The path of a Jupyter notebook needs to specified in the config for automatic report generation (default provided).

## Examples <a name="examples"></a>

 Examples of some of the data generated by Rainbow can be seen below.

### Raw Image Series (left) and Rainbow Optical Flow Visualisation (Right)

<img src="misc/images/raw_vs_flow.gif" width="780"/>

### Magnitude Heatmaps (Left) and Quiver Plots (Right) Across Image Series

<p float="left">
  <img src="misc/images/heatmap.gif" width="390" />
  <img src="misc/images/quiver_plot.gif" width="390" />
</p>

## Community guidelines <a name="community-guidelines"></a>

 Guidelines for third-parties wishing to:

- Contribute to the software
- Report issues or problems with the software
- Seek support

can be found [here](CONTRIBUTING.md).

## License <a name="license"></a>

[MIT License](LICENSE)

## Software Paper <a name="software-paper-abstract"></a>

### Title
Automated Air-Liquid Interface Cell Culture Analysis Using Deep Optical Flow

### Abstract
To be released

### Access
To be released

## Our Team <a name="our-team"></a>
[Learn more](https://walyanrespiratory.telethonkids.org.au/our-research/focus-areas/artifical-intelligence/)

## Acknowledgements <a name="acknowledgements"></a>

- https://github.com/philferriere/tfoptflow
- https://docs.opencv.org/3.4/d4/dee/tutorial_optical_flow.html
- https://github.com/zacjiang/GMA
