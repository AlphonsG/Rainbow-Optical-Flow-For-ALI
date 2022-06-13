import os

import cv2

import numpy as np

OPTICAL_FLOW_FILENAME = 'optical_flow.npy'


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


def save_optical_flow(preds, output_dir):
    """Saves optical flow predictions to a file in output_dir.

    Args:
        preds (np.array): Optical flow predictions as a numpy array.
        output_dir (string): The path to the output directory.
    """
    np.save(os.path.join(output_dir, OPTICAL_FLOW_FILENAME), preds,
            allow_pickle=False)


def load_optical_flow(flow_path):
    """Loads optical flow predictions from a file.

    Args:
        flow_path (string): The path to a .npy file containing saved optical
            flow predictions.

    Returns:
        list: A list of optical flow predictions as numpy arrays.
    """
    raw_preds = np.load(flow_path)
    preds = []
    for i in range(0, raw_preds.shape[0]):
        preds.append(raw_preds[i, ...])

    return preds


def get_img_pairs(imgs):
    """Returns image pairs.

    Duplicates every image of an image sequence, except the first and last,
    and groups pairs of images.

    Args:
        imgs (list): A list of images.

    Returns:
        list: A list of images pairs.
    """
    img_pairs = [[imgs[i][0], imgs[i + 1][0]] for i in range(
        0, len(imgs) - 1)]

    return img_pairs
