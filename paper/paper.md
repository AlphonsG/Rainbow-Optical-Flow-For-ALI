---
title: 'Rainbow: Automated Air-Liquid Interface Cell Culture Analysis Using Deep Optical Flow'
tags:
  - python
  - jupyter notebook
  - bioinformatics
  - deep learning
  - biology
  - optical flow
  - image analysis
  - bioimage informatics
authors:
  - name: Alphons Gwatimba^[corresponding author]
    orcid: 0000-0002-9607-2839
    affiliation: "1, 2"
  - name: Joseph Ho
    orcid: 0000-0002-9496-506X
    affiliation: "1, 2"
  - name: Thomas Iosifidis^[co-second author]
    orcid: 0000-0001-8462-5865
    affiliation: "1, 3, 4"
  - name: Yuliya V. Karpievitch^[co-second author]
    orcid: 0000-0003-2586-3358
    affiliation: "1, 5"

affiliations:
  - name: Wal-yan Respiratory Research Centre, Telethon Kids Institute, University of Western Australia, Nedlands, 6009, Western Australia, Australia
    index: 1
  - name: School of Computer Science and Software Engineering, University of Western Australia, Nedlands, 6009, Western Australia, Australia
    index: 2
  - name: Centre for Cell Therapy and Regenerative Medicine, School of Medicine, University of Western Australia, Nedlands, 6009, Western Australia, Australia
    index: 3
  - name: School of Public Health, Curtin University, Bentley, 6102, Western Australia, Australia
    index: 4
  - name: School of Molecular Sciences, University of Western Australia, Nedlands, 6009, Western Australia, Australia
    index: 5
date: 19 November 2021
bibliography: paper.bib
---

# Summary

`Rainbow` is a free, open-source and cross-platform Python-based tool for Air-Liquid Interface (ALI) cell culture time-lapse image analysis. `Rainbow` accepts time-lapse input images in standard image formats, such as TIFF, or microscopy file formats, such as ND2, and then computes the optical flow, that is: the apparent motion of individual pixels in an image [@turagaAdvancesVideoBasedHuman2010; @beauchemin1995computation; @ZHAI2021107861], across multiple frames using a deep learning based pretrained optical flow model [@jiangLearningEstimateHidden2021]. `Rainbow` then uses the pixel-level optical flow information and applies circular data analysis to calculate the average magnitude [0, ∞] (μm) and direction [0, 360) (°) of motion between adjacent frames to quantify cell motility. Additionally, the variance of the magnitude [0, ∞] (μm) and direction [0, ∞] (°) of motion between adjacent frames is calculated to quantitatively capture the degree of heterogeneity in cell motility.

For each experiment, a CSV file with the minimum, maximum, mean, standard deviation and variance of the magnitude and direction of cell movement between adjacent frames in an image sequence is produced. Multiple CSV files from different experiments can be combined into one file that can be analysed for differences in cell motility across multiple experiments. `Rainbow` also includes a high-resolution and easily readable unified hue/saturation-based visualisation scheme for the instantaneous vector field of motion between adjacent frames of an image sequence to qualitatively show cell motion. `Rainbow` can be used through a graphical user interface or command line interface and can generate a HTML report containing output images, videos, publication ready figures, and CSV files detailing cell dynamics (refer to Examples folder on GitHub). Importantly, our software is not limited to ALI culture image analysis, and developers can extend the software’s existing pipeline to other use cases. For example, the optical flow model can be readily substituted with different models, as we utilised the Factory Method creational software design pattern. The data analyses and report generated can be adjusted through interactive Jupyter Notebooks, allowing for a flexible and versatile system. Some of `Rainbow`’s visualizations are shown in \autoref{fig1}.

# Statement of need

Assessment of airway epithelial cell (AEC) function in disease utilise in vitro models such as the ALI cell culture [@chenAirliquidInterfaceCell2019; @looiEffectsHumanRhinovirus2018; @martinovichConditionallyReprogrammedPrimary2017]. The integration of image analysis and ALI cultures has provided novel insights into cell dynamics, such as the recently identified unjammed-to-jammed transition of AEC characterised by changes in cell motility [@mitchelPrimaryAirwayEpithelial2020; @parkUnjammingCellShape2015]. In chronic respiratory diseases like asthma, increased cell motility and AEC unjamming have been linked to airway remodelling and disease development [@mitchelPrimaryAirwayEpithelial2020; @parkUnjammingCellShape2015]. However, the image analyses performed in these studies are limited. For example, handcrafted methods from the MATLAB Computer Vision Toolbox that compute optical flow have been used to extract cell motion information from ALI culture images [@mitchelPrimaryAirwayEpithelial2020]. This approach requires licenced software and handcrafted optical flow estimation methods have been outperformed in terms of accuracy by deep learning methods [@savianOpticalFlowEstimation2020]. Furthermore, commonly used cell motion metrics, such as average cell speed, do not capture all unique aspects of cell motion, such as the heterogeneity of cell migration patterns across time. Cell motion is commonly visualised using vector fields, which are useful but bound by an inverse relationship between resolution and readability [@henkesDenseActiveMatter2020; @nnetuImpactJammingBoundaries2012; @osullivanIrradiationInducesEpithelial2020].

To increase understanding of lung disease mechanisms and development of new treatment options for patients, there is a need for open-source solutions for ALI culture image analyses that can be broadly implemented across cell biology laboratories. To the best of our knowledge, `Rainbow` is the first easy-to-use software tool that performs all the above analyses automatically for efficient utilisation by non-programmers. `Rainbow` produces automatic cell motion quantifications, figures, and reports that are all easily transferrable into publications. We anticipate that `Rainbow` will provide cell motion characterization for each experiment and allow for easy comparisons among multiple experiments to uncover cell migration mechanisms previously undetermined in health and disease.

# Figures

![`Rainbow` optical flow visualisation. **A:** The direction of motion at any position within `Rainbow` generated optical flow images is measured clockwise from the initial horizontal position of a unit circle (left) and is shown using hue values (right). **B:** The magnitude of motion at any position within optical flow images is shown using saturation values. High saturation (100%) corresponds to high magnitude of motion and low saturation (25%) corresponds to low magnitude of motion. **C, G:** Still frames taken from two separate ALI culture image sequences. **D, H:** Unified visualisation of optical flow magnitude and direction between adjacent frames of two ALI culture image sequences using `Rainbow`. The arrow indicates the average direction of motion across the image sequence. The circles indicate three localised vortexes that the cells move around in a swirl-like motion as they change direction. **E, I:** Traditional visualisation of optical flow between adjacent frames of two ALI culture image sequences using quiver plots containing vector arrows at every 70 px. **F, J:** Polar plots visualising motion magnitude (concentric circles; µm) and direction (azimuthal angle; degrees) in the same frame of two ALI culture image sequences. Colour scale indicates the number of points migrating towards given direction. All left positioned subfigures from row 2 onwards correspond to the same ALI culture image sequence while right positioned subfigures correspond to a different image sequence. For complete insight, refer to Examples folder on GitHub containing videos. \label{fig1}](figure_1.png){width=65%}

# Acknowledgements

We would like to thank the contribution and assistance of all the respiratory fellows, anaesthetists, nurses, hospital staff at St John of God Hospital, Subiaco (Human Research Ethics Committee study approval #901) and Western Australian Epithelial Research Program (WAERP) members. We would also like to thank the families and children participating in this project. This work was supported by the Wal-Yan Respiratory Research Centre Inspiration Award, Cystic Fibrosis Charitable Endowment Charles Bateman Charitable Trust, Western Australian Department of Health Merit Award and BHP-Telethon Kids Blue Sky Award. Furthermore, this project relies on high quality open source Python packages: NumPy [@harris2020array], matplotlib [@Hunter:2007], pandas [@mckinney-proc-scipy-2010], [PyYaml](https://pyyaml.org/wiki/PyYAMLDocumentation), [ND2Reader](https://github.com/Open-Science-Tools/nd2reader), [Gooey](https://github.com/chriskiehl/Gooey), [Physt](https://physt.readthedocs.io/en/latest/index.html#), [imutils](https://github.com/PyImageSearch/imutils), [MoviePy](https://zulko.github.io/moviepy/), [natsort](https://github.com/SethMMorton/natsort), [PIMS](http://soft-matter.github.io/pims/v0.5/#), tqdm [@tqdmref], pytest [@pytest], FFmpeg [@tomar2006converting], OpenCV [@opencv_library], Jupyter Notebook [@jupyter], Astropy [@astropy:2013; @astropy:2018], PyTorch [@NEURIPS2019_9015] and scikit-image [@scikit-image].

# References

