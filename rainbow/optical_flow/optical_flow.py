import os

import cv2

import numpy as np

import rainbow
from rainbow.optical_flow.model_factory import ModelFactory
from rainbow.util import (cleanup_dir, save_img_ser, save_img_ser_metadata,
                          save_optical_flow)

OPTICAL_FLOW_FILENAME = 'optical_flow.npy'


def compute_optical_flow(imgs, output_dir, model_name, model_config,
                         reuse_model=True, save_raw_imgs=True,
                         overwrite_flow=False):
    """Computes the optical flow.

    Computes the optical flow in an image sequence using the chosen optical
    flow model and saves the flow as a file in output_dir.

    Args:
        imgs (list): A list of images.
        output_dir (string): The path to the output directory.
        model_name (string): The name of the optical flow model to use.
        model_config (dict): The configuration of the optical flow model.
        reuse_model (bool, optional): If True, multiple calls of this function
            with the same model name will use the same optical model instance.
            Defaults to True.
        save_raw_imgs (bool, optional): If True, saves the image sequence in
            output_dir. Defaults to True.
        overwrite_flow (bool, optional): If True, will re-compute optical flow
            even if the flow file already exists in output_dir.
            Defaults to False.
    """
    mdl_fcty = ModelFactory()
    model = mdl_fcty.get_model(model_name, model_config, reuse_model)
    preds = model.predict(imgs)

    if not (os.path.isfile(os.path.join(output_dir,
            OPTICAL_FLOW_FILENAME)) and not overwrite_flow):
        if not cleanup_dir(output_dir):
            return
        os.mkdir(output_dir)
        save_optical_flow(preds, output_dir)

        if save_raw_imgs:  # TODO remove
            raw_imgs_dir = os.path.join(output_dir, rainbow.RAW_IMGS_DIR_NAME)
            os.mkdir(raw_imgs_dir)
            save_img_ser(imgs, raw_imgs_dir)
            save_img_ser_metadata(imgs, output_dir)


def flow_to_img(flow, normalize=True, info=None, flow_mag_max=None):
    """Visualizes optical flow (https://github.com/philferriere/tfoptflow).

    Convert flow to viewable image, using color hue to encode flow vector
    orientation, and color saturation to encode vector length. This is similar
    to the OpenCV tutorial on dense optical flow, except that they map vector
    length to the value plane of the HSV color model, instead of the saturation
    plane, as we do here.
    [Ref] OpenCV 3.0.0-dev documentation » OpenCV-Python Tutorials » Video
        Analysis »
        https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_video/
            py_lucas_kanade/py_lucas_kanade.html

    Args:
        flow (numpy array): The optical flow.
        normalize (bool, optional): If True, normalizes flow to 0..255.
            Defaults to True.
        info (string, optional): Text to superimpose on image (typically, the
            epe for the predicted flow). Defaults to None.
        flow_mag_max (int, optional): Max flow to map to 255. Defaults to None.

    Returns:
        numpy array: Viewable representation of the dense optical flow in RGB
            format.
    """
    hsv = np.zeros((flow.shape[0], flow.shape[1], 3), dtype=np.uint8)
    flow_magnitude, flow_angle = (cv2.cartToPolar(flow[..., 0].astype(
                                  float), flow[..., 1].astype(float)))

    # A couple times, we've gotten NaNs out of the above...
    nans = np.isnan(flow_magnitude)
    if np.any(nans):
        nans = np.where(nans)
        flow_magnitude[nans] = 0.

    # Normalize.
    hsv[..., 0] = flow_angle * 180 / np.pi / 2
    if normalize is True:
        if flow_mag_max is None:
            hsv[..., 1] = cv2.normalize(flow_magnitude, None, 0, 255,
                                        cv2.NORM_MINMAX)
        else:
            hsv[..., 1] = flow_magnitude * 255 / flow_mag_max
    else:
        hsv[..., 1] = flow_magnitude
    hsv[..., 2] = 255
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    # Add text to the image, if requested.
    if info is not None:
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, info, (20, 20), font, 0.8, (0, 0, 0), 2, cv2.LINE_AA)

    return img
