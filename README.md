# Rainbow

![](docs/images/banner_img.png?raw=true "Rainbow")

Repository for software detailed in 'RAINBOW: Automated Air-Liquid Interface Cell Culture Analysis Using Deep Optical Flow' Application Note. See Abstract [below](#application-note-abstract) for more details.

## Preliminary Information

Rainbow is portable and will run on Linux and Windows. Rainbow can also be run using a CPU but we recommend using a GPU for significant performance gains. Rainbow depends on TensorFlow for CPU or GPU based inference. Data can also be analyzed in parallel using multiprocessing.

## Installation

We recommend installing and running Rainbow within a virtual environment.

Tested on Windows 10 using Python 3.7.

### Pre-requisites

1. Download and install [miniconda3](https://docs.conda.io/en/latest/miniconda.html) for your system.
2. Download and install [Git](https://git-scm.com/downloads) for your system.

### Installing Rainbow
1. If the `conda` command cannot be directly called from a terminal then launch 'Anaconda Prompt (miniconda3)'
2. From a terminal session or 'Anaconda Prompt', create a virtual environment with Python 3.7 called 'rainbow_env':

    ```conda create -n rainbow_env python=3.7```

3. Activate the environment:

   ```conda activate rainbow_env```


4. Clone this repository into your desired directory:

   ```git clone https://github.com/AlphonsGwatimba/Automated-Air-Liquid-Interface-Cell-Culture-Analysis-Using-Deep-Optical-Flow.git```

5. Navigate into the cloned directory:

    ```cd Automated-Air-Liquid-Interface-Cell-Culture-Analysis-Using-Deep-Optical-Flow.git```
6. Install Rainbow:

   ```python setup.py install```
7.  Virtual environment can be exited using:

    ```conda deactivate rainbow_env```


**Note**: Windows users ensure [Microsoft Visual C++ 2008 Service Pack 1 Redistributable Package](https://www.microsoft.com/en-US/download/details.aspx?id=26368) is installed


## Additional Setup

### Configuration File

A default .yaml configuration file for Rainbow is provided [here](examples/configs/default_config.yaml). Please copy this file and make the necessary changes according to your requirements and environment. Please pass the path of your configuration file as an argument to ```rainbow``` when running.

### PWC-Net Pre-trained Models

The deep learning model used to compute optical flow depends on checkpoint files that need to be downloaded. The download location for these files is provided [here](rainbow/optical_flow/checkpoints/pwc_net/pwcnet-lg-6-2-multisteps-chairsthingsmix/Checkpoint%20Files%20Download%20Location.txt). Please download these files and place in one folder. The path of this folder needs to be specified in the .yaml configuration file.

### Report

Rainbow automatically generates a report after processing an image series. An example report is provided [here](examples/notebooks/report.ipynb) as a Jupyter Notebook (.ipynb file). The path of a .ipynb file needs to be specified in the .yaml configuration file for report generation.
## Usage

There is one main command line interface which you can use with the ```rainbow``` command

1. Within a terminal, activate the Rainbow virtual environment:

   ```conda activate rainbow_env```

2. Call the `rainbow` command with the required arguments to run. Enter `rainbow -h` for help.

## Examples

An example ALI cell culture image series is provided [here](examples/image_series_1). Calling the `rainbow` command with this folder as the `root-dir` argument, default .yaml configuration file as the `config` argument and `--non-recursive` option produces [this](examples/image_series_1/(tif)%20191018_HNA-ALI_d14.nd2%20-%20191018_HNA-ALI_d14.nd2%20(series%2003)0000_etc) results folder. Some of the generated images can be seen below.

### Raw Image Series (left) and Rainbow Optical Flow Visualisation (Right)

<img src="docs/images/raw_vs_flow.gif"/>

### Magnitude Heatmaps Across Image Series

<img src="docs/images/heatmap.gif" width="600"/>

### Quiver Plots Across Image Series

<img src="docs/images/quiver_plot.gif" width="600"/>

## License

[MIT License](LICENSE)

## Application Note <a name="application-note-abstract"></a>

### Title
RAINBOW: Automated Air-Liquid Interface Cell Culture Analysis Using Deep Optical Flow

### Abstract
The use of well differentiated, organotypic culture models of the airways, such as the Air-Liquid Interface (ALI) cell culture, has extended our understanding of airway epithelial cells and identified novel treatment strategies for chronic lung diseases such as asthma and cystic fibrosis. While the integration of real time imaging and cell culture models have continually provided novel insights into cell dynamics, the image analyses currently performed with ALI cultures are limited. We present here RAINBOW, a Python-based and open source ALI cell culture analysis tool that overcomes these limitations. For example, RAINBOW quantifies cell motion in ALI culture time lapse images using an established deep learning model with cutting edge accuracy instead of traditionally used costly and superseded approaches, such as handcrafted optical flow methods from MATLAB’s licenced computer vision toolbox. Furthermore, RAINBOW generates metrics which capture unique aspects of cell motion that are commonly overlooked and visualises cell motion using a novel method in this field that offers greater detail in comparison to traditional methods. Importantly, RAINBOW is the first complete software pipeline that can be efficiently and easily utilised by cell biologists and data scientists.
