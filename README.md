# Rainbow

![](https://img.shields.io/badge/Rainbow-2022.4.5-blue)
![](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macOS-lightgrey)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Python package](https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/actions/workflows/python-package.yaml/badge.svg?branch=main)](https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/actions/workflows/python-package.yaml)
[![DOI](https://joss.theoj.org/papers/10.21105/joss.04080/status.svg)](https://doi.org/10.21105/joss.04080)

<p style="text-align:center;">
   <img src="https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/raw/main/misc/images/banner_img.png" alt="centered image" />
</p>

Software for automated Air-Liquid Interface cell culture image analysis using deep optical flow. See <a href="#software-paper">below</a> for more details.

## Table of contents
1. <a href="#installation">Installation</a>
2. <a href="#usage">Usage</a>
3. <a href="#additional-information">Additional Information</a>
4. <a href="#examples">Examples</a>
5. <a href="#community-guidelines">Community Guidelines</a>
6. <a href="#license">License</a>
7. <a href="#software-paper">Software Paper</a>
8. <a href="#our-team">Our Team</a>
9. <a href="#acknowledgements">Acknowledgements</a>

## Installation <a id="installation"></a>

Rainbow can be installed on Linux, Windows & macOS and supports Python 3.8 and above. We recommend installing and running Rainbow within a [virtual environment](https://docs.python.org/3/tutorial/venv.html). Although it is not a requirement, we also recommend installing and running Rainbow on a GPU-enabled system to minimize processing times.

1. Download and install [Python](https://www.python.org/downloads/) (Rainbow was tested using [Python version 3.8.10](https://www.python.org/downloads/release/python-3810/)).

2. Launch the terminal (*Linux* and *macOS* users) or command prompt (*Windows* users). The proceeding commands will be entered into the opened window<sup>1</sup>.

3. (Optional but recommended) Create and activate a virtual environment called 'rainbow-env' in your desired directory:

   ```python -m venv rainbow-env```

   ```. rainbow-env/bin/activate``` (*Linux* and *macOS* users) or ```rainbow-env\Scripts\activate.bat``` (*Windows* users)

   ```python -m pip install -U pip```

4. Install PyTorch by specifying your system configuration using the official [PyTorch get started tool](https://pytorch.org/get-started/locally/) and running the generated command:
   <p style="text-align:center;">
    <img src="https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/raw/main/misc/images/pytorch_get_started.png" width="750" alt="centered image" />
    </p>
   For example, Windows users without a GPU (i.e. CPU only) will run:

   ```pip install torch torchvision torchaudio```

Next, proceed wth either option A or B.
### Option A - Install from PyPI

This is the simplest and fastest way to install Rainbow, recommended for normal users.


5. Install Rainbow:

   ```pip install rainbow-optical-flow```


### Option B - Install from Source

Developers may wish to install Rainbow from source. Please ensure [Git](https://git-scm.com/downloads) and [Git LFS](https://git-lfs.github.com/) are installed before proceeding.

5. Clone this repository into your desired directory:

   ```git clone https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI.git```

6. Navigate into the cloned directory:

    ```cd Rainbow-Optical-Flow-For-ALI```

7. Install Rainbow:

   ```pip install -e .```

8. Finalize the installation by running the following commands:

   ```
   git submodule sync

   git submodule update --init --recursive
   ```

Notes:
  - <sup>1</sup>Confirm the correct python version for Rainbow has been installed using the `python -V` command in the terminal. If this command does not report the correct python version, try using the `python3 -v` command instead. If the second command produces the expected result, replace all `python` and `pip` commands in this guide with `python3` and `pip3`, respectively.

  - The virtual environment can be deactivated using:

      ```deactivate```

  - If Rainbow fails to install on Linux, it may be because `wxpython` could not be built (look for clues in the error messages printed on the terminal e.g. "Running setup.py install for wxpython ... error"). Instead, try installing `wxpython` first by following [these](https://wxpython.org/pages/downloads/) instructions (specifically "Yes, we have Linux Wheels. Sort of.") and then attempt to install Rainbow again via ```pip install rainbow-optical-flow``` (option A) or ```pip install -e .``` (option B).

## Usage <a id="usage"></a>

### Command Line Interface (CLI)

Once installed, Rainbow can be used through a CLI. Run `rainbow --help` or `rainbow -h` (within the `rainbow-env` environment if applicable) for a list of available command arguments and descriptions.

To test Rainbow using an example Air-Liquid Interface cell culture image series, follow the instructions under option B of the <a href="#installation">installation</a> procedure (except for step 7) and run the following commands in the terminal:

```
cd rainbow
rainbow ../examples/example_image_series ../misc/configs/default_config.yaml
```

After processing is finished, a folder containing similar outputs (e.g. a HTML report,  videos, images, CSV files) to those in [this](https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/tree/main/examples/example_output/(tif)_191018_HNA-ALI_d14.nd2_-_191018_HNA-ALI_d14.nd2_(series_03)0000_etc) example output folder should be generated in [this](https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/tree/main/examples/example_image_series) folder.
### Graphical User Interface (GUI)

Once installed, Rainbow can be be used through a GUI, which can be launched by running the command `rainbow` (within the `rainbow-env` environment if applicable).

To test Rainbow using an example Air-Liquid Interface cell culture image series, follow the instructions under option B of the <a href="#installation">installation</a> procedure (except for step 7) and run the following commands in the terminal::

 ```
 cd rainbow
 rainbow
 ```

 Then, in the GUI that opens, select [this](https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/tree/main/examples/example_image_series) folder as the input image series and [this](https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/blob/main/misc/configs/default_config.yaml) file as the configuration file in the GUI under 'Required Arguments' and click the 'Start' button. After processing is finished, a folder containing similar outputs (e.g. a HTML report,  videos, images, CSV files) to those in [this](https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/tree/main/examples/example_output/(tif)_191018_HNA-ALI_d14.nd2_-_191018_HNA-ALI_d14.nd2_(series_03)0000_etc) example output folder should be generated in [this](https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/tree/main/examples/example_image_series) folder.

## Additional Information <a id="additional-information"></a>

### Optical Flow

Rainbow uses a deep learning model called [GMA](https://arxiv.org/abs/2104.02409) to compute the optical flow in an image series. This model can be replaced with any other method for computing optical flow by writing a custom class that implements the [base_model](https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/blob/main/rainbow/optical_flow/base_model.py) interface ([gma.py](https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/blob/main/rainbow/optical_flow/gma.py) is an example of that).

### Analysis

Rainbow can automatically generate an analysis report after computing the optical flow in an image series. A base report file that can be modified is provided [here](https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/blob/main/misc/notebooks/report.ipynb) as a Jupyter notebook. The path of a Jupyter notebook needs to specified in the config for automatic report generation (default provided).

### Scripts

The [scripts](https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/raw/main/scripts) folder contains python scripts to enable additional functionality such as the ability to combine reports from multiple experiments into one file for simpler viewing and comparisons. Run `python <script-name>.py --help` in the terminal to view the usage instructions for a script.

### Automated Testing

To perform and check the status of the automated tests locally, run the command `pytest` in the terminal, with Rainbow installed, from the root directory of this repository after cloning.

## Examples <a id="examples"></a>

Examples of some of the data generated by Rainbow can be seen below.

### Raw Image Series (left) and Rainbow Optical Flow Visualisation (Right)

<img src="https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/raw/main/misc/images/raw_vs_flow.gif" width="780" />

### Magnitude Heatmaps (Left) and Quiver Plots (Right) Across Image Series

<img src="https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/raw/main/misc/images/heatmap.gif" width="390" hstyle="border:0px;margin:0px;float:left"/> <img src="https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/raw/main/misc/images/quiver_plot.gif" width="390" style="border:0px;margin:0px;float:left"/>

### Experimental Methods

Primary tracheobronchial epithelial cells were isolated through trans‐laryngeal, non‐bronchoscopic cytologic brushings via an endotracheal tube from two children (3.3 and 4.1 years), as previously described (Looi et al., 2018; Martinovich et al., 2017). The use of tracheobronchial epithelial cells for these studies were approved by the Human Research Ethics Committees of St John of God Hospital and The University of Western Australia. Cells were imaged (20x objective) on day 2 post air-lift for 2.5 hrs every 8 mins with a Nikon C2+ inverted microscope incubated at 37° C with humidified 95% air/5% CO2 using an Okolab live cell imaging chamber to generate time lapse images of maximally migrating cells as previously described (Park et al., 2015; Mitchel et al., 2020). The example image series provided in this repository contains 20 image frames at 1280 x 1024 px resolution.

#### References

Looi,K. et al. (2018) Effects of human rhinovirus on epithelial barrier integrity and function in children with asthma. Clinical & Experimental Allergy, 48, 513–524.

Martinovich,K.M. et al. (2017) Conditionally reprogrammed primary airway epithelial cells maintain morphology, lineage and disease specific functional characteristics. Scientific Reports, 7, 17971.

Mitchel,J.A. et al. (2020) In primary airway epithelial cells, the unjamming transition is distinct from the epithelial-to-mesenchymal transition. Nature Communications, 11, 5053.
Park,J.-A. et al. (2015) Unjamming and cell shape in the asthmatic airway epithelium. Nature Materials, 14, 1040–1048.

## Community guidelines <a id="community-guidelines"></a>

 Guidelines for third-parties wishing to:

- Contribute to the software
- Report issues or problems with the software
- Seek support

can be found [here](https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/blob/main/CONTRIBUTING.md).

## License <a id="license"></a>

[MIT License](https://github.com/AlphonsG/Rainbow-Optical-Flow-For-ALI/blob/main/LICENSE)

## Software Paper <a id="software-paper"></a>

### Title
Rainbow: Automated Air-Liquid Interface Cell Culture Analysis Using Deep Optical Flow

### Access

https://joss.theoj.org/papers/10.21105/joss.04080

## Our Team <a id="our-team"></a>
[Learn more](https://walyanrespiratory.telethonkids.org.au/our-research/focus-areas/artifical-intelligence/)

## Acknowledgements <a id="acknowledgements"></a>

- https://github.com/philferriere/tfoptflow
- https://docs.opencv.org/3.4/d4/dee/tutorial_optical_flow.html
- https://github.com/zacjiang/GMA
