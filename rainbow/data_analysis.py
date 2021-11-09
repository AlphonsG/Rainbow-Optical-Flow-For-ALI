import csv
import math
import os
import warnings
from itertools import chain
from pathlib import Path

import cv2

import matplotlib.pyplot as plt

import nbconvert
from nbconvert.preprocessors import CellExecutionError, ExecutePreprocessor

import nbformat

import numpy as np

from physt import polar

import scipy.stats

SENTINEL = 'STOP'
NOTEBOOK_DIR = 'misc/notebooks'


def analyze_data(queue, config):
    """Performs data analysis.

    Receives directories from worker processes via queue and generates an
    analysis report of data stored in those directories.

    Args:
        queue (multiprocessing.Queue): The queue that will be used to receive
            directory paths from workers.
        config (string): The path to a .yaml configuration file.

    Returns:
        int: 0 when data analysis has successfully finished.
    """
    while True:
        output_dir = queue.get()
        if output_dir == SENTINEL:
            # put it back so that other consumers see it
            queue.put(SENTINEL)
            return 0

        gen_report(output_dir, config['report_path'])


def gen_report(output_dir, report_path, html=True):
    """Generate a report.

    Execute a jupyter notebook in output_dir.

    Args:
        output_dir (string): The path to the output directory.
        report_path (string): The path to the jupyter notebook.
        html (bool, optional): If True, will also save executed jupyter
            notebook as a html file in output_dir. Defaults to True.
    """
    if not os.path.isfile(report_path):
        report_path = os.path.join(os.path.abspath(os.path.dirname(
            __file__)), '..', NOTEBOOK_DIR, report_path)
        if not os.path.isfile(report_path):
            return

    with open(report_path) as f:
        nb = nbformat.read(f, as_version=4)
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        ep.allow_errors = True
        gend_report_path = os.path.join(output_dir,
                                        Path(report_path).name)
        try:
            ep.preprocess(nb, {'metadata': {'path': output_dir}})
        except CellExecutionError:
            msg = (f'Could not generate report, see \'{gend_report_path}\' '
                   'for error.')
            warnings.warn(msg, UserWarning)
        finally:
            with open(gend_report_path, 'w', encoding='utf-8') as f:
                nbformat.write(nb, f)
            if html:
                save_html(output_dir, gend_report_path)


def save_html(output_dir, gend_report_path):
    """Saves jupyter notebook as a html file in output_dir.

    Args:
        output_dir (string): The path to the output directory.
        gend_report_path (string): The path to the jupyter notebook.
    """
    with open(gend_report_path) as f:
        nb = nbformat.read(f, as_version=4)
        exporter = nbconvert.HTMLExporter()
        exporter.exclude_input = True
        body, resources = exporter.from_notebook_node(nb)
        file_writer = nbconvert.writers.FilesWriter()
        file_writer.write(output=body, resources=resources,
                          notebook_name=os.path.join(output_dir, Path(
                                                     gend_report_path).stem))


def mag_scatter(mags):
    """Creates a magnitude scatter plot.

    Args:
        mags (list): A list of floats representing vector magnitudes.
    """
    times = list(range(1, len(mags) + 1))
    plt.figure()
    plt.scatter(times, mags)
    plt.title('Flow Magnitude')
    plt.xlabel('Frame Number (Frame)')
    plt.ylabel('Average Distance (μm)')
    plt.ylim(0, max(mags) * 1.5)


def dirn_scatter(dirns):
    """Creates a direction scatter plot.

    Args:
        dirns (list): A list of floats representing vector directions.
    """
    times = list(range(1, len(dirns) + 1))
    plt.figure()
    plt.scatter(times, dirns)
    plt.title('Flow Direction')
    plt.xlabel('Frame Number (Frame)')
    plt.ylabel('Average Angle (Deg)')
    plt.ylim(0, max(dirns) * 1.5)


def save_heatmaps(preds, output_dir, step=0, dpi=1000):
    """Saves heatmaps.

    Writes images visualizing the magnitude of optical flow of an image
    sequence to output_dir.

    Args:
        preds (list): The optical flow across an image sequence.
        output_dir (string): The path to the output directory.
        step (int, optional): The amount of infomation discarded when
            visualizing heatmaps. Defaults to 0.
        dpi (int, optional): The dots per inch of the saved heatmap images.
            Defaults to 1000.
    """
    for i, pred in enumerate(preds):
        plt.xticks([])
        plt.yticks([])
        plt.Axes(plt.figure(frameon=False), [0, 0, 1, 1])
        plt.axis('off')
        pred = np.copy(pred)
        pred[:, :, 1] = pred[:, :, 1] * -1
        u, v = ((pred[::step, ::step, 0].astype(np.float32),
                pred[::step, ::step, 1].astype(float)) if step != 0 else
                (pred[:, :, 0].astype(float), pred[:, :, 1].astype(float)))
        mag = cv2.cartToPolar(u, v, angleInDegrees=1)
        plt.pcolormesh(mag[0], cmap='hot')
        path = os.path.join(output_dir, 'Image_{}.png'.format(i))
        plt.savefig(path, dpi=dpi, bbox_inches=0)
        plt.close()


def save_quiver_plots(preds, output_dir, step=70, dpi=1000):
    """Saves quiver plots.

    Writes images visualizing the direction of optical flow of an image
    sequence to output_dir.

    Args:
        preds (list): The optical flow across an image sequence.
        output_dir (string): The path to the output directory.
        step (int, optional): The pixel seperation of the vectors visualized in
            the quiver plots.
        dpi (int, optional): The dots per inch of the saved quiver plot images.
            Defaults to 1000.
    """
    for i, pred in enumerate(preds):
        plt.xticks([])
        plt.yticks([])
        plt.Axes(plt.figure(frameon=False), [0, 0, 1, 1])
        plt.axis('off')
        pred = np.copy(pred)
        pred[:, :, 1] = pred[:, :, 1] * -1
        plt.quiver(np.arange(0, pred.shape[1], step), np.arange(pred.shape[0],
                   -1, -step), pred[::step, ::step, 0],
                   pred[::step, ::step, 1])
        path = os.path.join(output_dir, 'Image_{}.png'.format(i))
        plt.savefig(path, dpi=dpi, bbox_inches=0)
        plt.close(plt.gcf())


def gen_base_metrics(data):
    """Generates metrics for the optical flow data of an image sequence.

    Args:
        data (Defaultdict(list)): Contains an image sequence under the key
            'raw_imgs' and the corresponding optical flow under the key
            'preds'.
    """
    for i, pred in enumerate(data['preds']):
        mag, dirn = cv2.cartToPolar(pred[..., 0].astype(float),
                                    pred[..., 1].astype(float),
                                    angleInDegrees=1)
        data['mags'].append(mag)
        data['dirns'].append(dirn)
        mag[np.isnan(mag)] = 0  # remove NaNs
        mag *= data['raw_imgs'][0].metadata['mpp']  # convert to um, calib?
        for key, metric in zip(['mag_stats', 'dirn_stats'], [mag, dirn]):
            circ = True if key == 'dirn_stats' else False
            data[key].append(gen_stats(metric, i, circ))


def gen_stats(metric, i, circ=False):
    """Calculates statistics for a given metric.

    The statistics (e.g. mean, variance, etc.) are for a given metric in a
    frame of an image sequence.

    Args:
        metric (list): A list of values for the given metric.
        i (int): The corresponding frame number for the values of the given
            metric.
        circ (bool, optional): If true, treats metric as circular data.
            Defaults to False.
    Returns:
        dict: The statistics for the given metric.
    """
    if circ:
        metric = list(chain.from_iterable(metric.tolist()))
        mini, maxi = min(metric), max(metric)
        metric = np.deg2rad(metric)
        mean, std, var = scipy.stats.circmean(metric), scipy.stats.circstd(
            metric), scipy.stats.circvar(metric)
        mean, std, var = np.rad2deg(mean), np.rad2deg(std), np.rad2deg(var)
        stats = {'frame': i, 'min': mini, 'max': maxi, 'mean': mean,
                 'std': std, 'var': var}
    else:
        stats = scipy.stats.describe(metric, axis=None)
        stats = {'frame': i, 'min': stats[1][0],
                 'max': stats[1][1], 'mean': stats[2],
                 'std': math.sqrt(stats[3]), 'var': stats[3]}

    return stats


def save_stats(stats, csv_path, unit):
    """Saves statistics to a csv file.

    The statistics are for a given metric in one or more frames of an image
    sequence.

    Args:
        stats (list): A list of statistics.
        csv_path (string): The path of the csv file to create.
        unit (string): The unit of measurement for the given metric.
    """
    try:
        with open(csv_path, 'w', newline='') as csv_file:
            fields = ['frame', 'min', 'max', 'mean', 'std', 'var']  # outside?
            fields = ['{} ({})'.format(fd, unit) if fd != 'frame' else fd for
                      fd in fields]
            writer = csv.writer(csv_file)
            writer.writerow(fields)
            for s in stats:
                writer.writerow(list(s.values()))
    except (OSError, csv.Error, ValueError) as e:
        msg = 'Could not create stats file. Message: {}.'.format(str(e))
        warnings.warn(msg, UserWarning)


def save_polar_plots(preds, output_dir, dpi=1000, mpp=None):
    """Saves polar plots.

    Writes polar plots visualizing the optical flow circular data of an image
    sequence to output_dir.

    Args:
        preds (list): The optical flow across an image sequence.
        output_dir (string): The path to the output directory.
        dpi (int, optional): The dots per inch of the saved quiver plot images.
            Defaults to 1000.
        mpp (float, optional): The micrometres per pixel value of the
            image sequence, if None will use pixel units. Defaults to None.
    """
    if mpp is None:
        mpp = 1
    for i, pred in enumerate(preds):
        x, y = pred[..., 0].flatten() * mpp, pred[..., 1].flatten() * mpp
        hist = polar(x, y)
        hist.plot.polar_map(cmap="rainbow")
        path = os.path.join(output_dir, 'Image_{}.png'.format(i))
        plt.savefig(path, dpi=dpi, bbox_inches=0)
        plt.close()
