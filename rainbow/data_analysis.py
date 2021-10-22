import csv
import math
import os
import warnings

from pathlib import Path

import cv2

import matplotlib.pyplot as plt

import nbconvert
from nbconvert.preprocessors import CellExecutionError, ExecutePreprocessor

import nbformat

import numpy as np

import scipy.stats

from traitlets.config import Config as NotebookHTMLConfig

SENTINEL = 'STOP'


def analyze_data(queue, config):
    while True:
        output_dir = queue.get()
        if output_dir == SENTINEL:
            # put it back so that other consumers see it
            queue.put(SENTINEL)
            return 0

        gen_report(output_dir, config['report_path'])


def gen_report(output_dir, report_path, html=True):
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
            with open(gend_report_path, 'w',
                      encoding='utf-8') as f:
                nbformat.write(nb, f)
            if html:
                save_html(output_dir, gend_report_path)


def save_html(output_dir, gend_report_path):
    with open(gend_report_path) as f:
        c = NotebookHTMLConfig()
        # Configure our tag removal
        c.TagRemovePreprocessor.enabled = True
        c.TagRemovePreprocessor.remove_cell_tags = ('remove_cell',)
        c.TagRemovePreprocessor.remove_all_outputs_tags = ('remove_output',)
        c.TagRemovePreprocessor.remove_input_tags = ('remove_input',)

        # Configure and run out exporter
        c.HTMLExporter.preprocessors = ['nbconvert.preprocessors.'
                                        'TagRemovePreprocessor']
        nb = nbformat.read(f, as_version=4)
        exporter = nbconvert.HTMLExporter(config=c)
        body, resources = exporter.from_notebook_node(nb)
        file_writer = nbconvert.writers.FilesWriter()
        file_writer.write(output=body, resources=resources,
                          notebook_name=os.path.join(output_dir, Path(
                                                     gend_report_path).stem))


def mag_scatter(mags):
    times = list(range(1, len(mags) + 1))
    plt.figure()
    plt.scatter(times, mags)
    plt.title('Flow Magnitude')
    plt.xlabel('Frame Number (Frame)')
    plt.ylabel('Average Distance (μm)')
    plt.ylim(0, max(mags) * 1.5)


def dirn_scatter(dirns):
    times = list(range(1, len(dirns) + 1))
    plt.figure()
    plt.scatter(times, dirns)
    plt.title('Flow Direction')
    plt.xlabel('Frame Number (Frame)')
    plt.ylabel('Average Angle (Deg)')
    plt.ylim(0, max(dirns) * 1.5)


def save_heatmaps(preds, output_dir, step=0, dpi=1000, fps=5):
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


def save_quiver_plots(preds, output_dir, step=70, dpi=1000, fps=5):
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
    for i, pred in enumerate(data['preds']):
        mag, dirn = cv2.cartToPolar(pred[..., 0].astype(float),
                                    pred[..., 1].astype(float),
                                    angleInDegrees=1)
        data['mags'].append(mag)
        data['dirns'].append(dirn)
        mag[np.isnan(mag)] = 0  # remove NaNs
        mag *= data['raw_imgs'][0].metadata['mpp']  # convert to um, calib?
        for key, metric in zip(['mag_stats', 'dirn_stats'], [mag, dirn]):
            data[key].append(gen_stats(metric, i))


def gen_stats(metric, i):
    stats = scipy.stats.describe(metric, axis=None)
    stats = {'frame': i, 'min': stats[1][0],
             'max': stats[1][1], 'mean': stats[2],
             'std': math.sqrt(stats[3]), 'var': stats[3]}

    return stats


def save_stats(stats, csv_path, unit):
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
        msg = 'Could not create stats file. Message: {}'.format(str(e))
        warnings.warn(msg, UserWarning)
