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

`Rainbow` is a free, open-source and cross-platform Python-based tool for Air-Liquid Interface (ALI) cell culture image analysis. `Rainbow` quantifies cell motion in image sequences using a recent state-of-the-art deep learning based optical flow model  [@jiangLearningEstimateHidden2021]. Optical flow is the apparent motion of individual pixels on an image plane across frames [@turagaAdvancesVideoBasedHuman2010]. Our software generates motion magnitude and direction variance-based metrics to provide quantitative insight into heterogeneous cell dynamics observed in the ALI culture images, in addition to commonly used metrics such as average cell speed. We also include a unified hue/saturation-based visualisation scheme for cell motion which offers increased resolution as every coordinate on an image is utilised. `Rainbow` performs data analysis detailing cell dynamics by generating a HTML report containing output images, videos, publication ready figures, and p-values from input images provided in standard image formats, such as TIFF, and microscopy file formats, such as ND2. `Rainbow` can be easily used through a graphical user interference or command line interface by non-programmers. Importantly, `Rainbow` is not limited to ALI culture image analysis, and developers can extend the software’s existing pipeline to other use cases. For example, the optical flow model can be readily substituted with different models, as we utilised object orientated software design principles and data analyses and generated reports can be adjusted through interactive Jupyter Notebook documents, allowing for a flexible and versatile system. Some of `Rainbow`’s visualizations are shown in \autoref{fig1}.

# Statement of need

Research efforts to assess the function of airway epithelial cells (AEC) in disease utilise in vitro models such as the ALI cell culture [@chenAirliquidInterfaceCell2019; @looiEffectsHumanRhinovirus2018; @martinovichConditionallyReprogrammedPrimary2017]. The integration of image analysis and ALI cultures has provided novel insights into cell dynamics, such as the recently identified unjammed-to-jammed transition of AEC which has been linked to the pathobiology of asthma [@mitchelPrimaryAirwayEpithelial2020; @parkUnjammingCellShape2015]. However, the image analyses performed in these studies are limited. For example, handcrafted methods from the MATLAB Computer Vision Toolbox that compute optical flow have been used to extract cell motion information from ALI culture images [@mitchelPrimaryAirwayEpithelial2020]. However, this approach requires licenced software and handcrafted optical flow estimation methods have been outperformed in terms of accuracy by deep learning methods [@savianOpticalFlowEstimation2020]. Furthermore, commonly used metrics such as average cell speed are estimated using cell motion information, but do not capture all unique aspects of cell motion, such as the heterogeneity of cell migration patterns throughout the images. Cell motion is commonly visualised using vector fields, which are useful but bound by an inverse relationship between detail and readability [@henkesDenseActiveMatter2020; @nnetuImpactJammingBoundaries2012; @osullivanIrradiationInducesEpithelial2020]. Importantly, there is no single easy-to-use software that performs the preceding analyses automatically for efficient utilisation by non-programmers. `Rainbow` overcomes all the previously mentioned limitations and includes cell migration angular distribution metrics and circular statistics to allow users to assess differences in cell migration within each experiment and among multiple experiments. We anticipate that `Rainbow` users will be able to characterise cell migration more thoroughly across multiple experiments and uncover cellular migration mechanisms previously undetermined in health and disease.

# Figures

![`Rainbow` optical flow visualisation. **A:** The direction of motion at any position within `Rainbow` generated optical flow images is measured clockwise from the initial horizontal position of a unit circle (left) and is shown using hue values (right). **B:** The magnitude of motion at any position within optical flow images is shown using saturation values. High saturation (100%) corresponds to high magnitude of motion and low saturation (25%) corresponds to low magnitude of motion. **C, G:** Still frames taken from two separate ALI culture image sequences. **D, H:** Unified visualisation of optical flow magnitude and direction between adjacent frames of two ALI culture image sequences using `Rainbow`. The arrow indicates the average direction of motion across the image sequence. The circles indicate three localised vortexes that the cells move around in a swirl-like motion as they change direction. **E, I:** Traditional visualisation of optical flow between adjacent frames of two ALI culture image sequences using quiver plots containing vector arrows at every 70 px. **F, J:** Polar plots visualising motion magnitude (concentric circles; µm) and direction (azimuthal angle; degrees) in the same frame of two ALI culture image sequences. Colour scale indicates the number of points migrating towards given direction. All left positioned subfigures from row 2 onwards correspond to the same ALI culture image sequence while right positioned subfigures correspond to a different image sequence. \label{fig1}](figure_1.png){width=60%}

# Acknowledgements

We would like to thank the contribution and assistance of all the respiratory fellows, anaesthetists, nurses, hospital staff at St John of God Hospital, Subiaco (Human Research Ethics Committee study approval #901) and Western Australian Epithelial Research Program (WAERP) members. We would also like to thank the families and children participating in this project. This work was supported by the Wal-Yan Respiratory Research Centre Inspiration Award, Cystic Fibrosis Charitable Endowment Charles Bateman Charitable Trust, Western Australian Department of Health Merit Award and BHP-Telethon Kids Blue Sky Award.

# References

