import csv
import json
import math
import os
import warnings
from datetime import datetime

import cv2

import matplotlib.pyplot as plt

import nbconvert
from nbconvert.preprocessors import CellExecutionError, ExecutePreprocessor

import nbformat

import numpy as np

from rainbow.optical_flow.opt_flow import flow_to_img
from rainbow.util import (apply_metadata, cleanup_dir, comb_imgs, save_img_ser,
                          save_video)

import scipy.stats

from traitlets.config import Config as NotebookHTMLConfig


def analyze_data(queue, config):
    while True:
        data = queue.get()
        for d in data:
            if d is None:
                # put it back so that other consumers see it
                queue.put([None])
                return 0

            name, ext = os.path.splitext(d['Raw Images'][0].metadata[
                                         'img_name'])
            ser = (' Series {})'.format(d['Raw Images'][0].metadata[config[
                'nd2']['naming_axs'][0]]) if ext == '.nd2' else '')
            output_dir = '({}) {}{}_etc'.format(ext.replace('.', ''), name,
                                                ser)
            output_dir = os.path.join(d['Raw Images'][0].metadata[
                                      'img_ser_md']['dir'], output_dir)
            if not cleanup_dir(output_dir):
                continue
            os.mkdir(output_dir)

            d['Flow Images'] = [flow_to_img(pred) for pred in d['preds']]
            for i, (flow_img, raw_img) in enumerate(zip(d['Flow Images'],
                                                        d['Raw Images'])):
                flow_img = apply_metadata(flow_img, raw_img)
                d['Flow Images'][i] = flow_img

            d['Combined Images'] = [comb_imgs(img1, img2) for img1, img2 in
                                    zip(d['Raw Images'], d['Flow Images'])]
            for i, (comb_img, raw_img) in enumerate(zip(d['Combined Images'],
                                                        d['Raw Images'])):
                comb_img = apply_metadata(comb_img, raw_img)
                d['Combined Images'][i] = comb_img

            gen_base_metrics(d, config['mpp'])
            for key, unit in zip(['mag_stats', 'dirn_stats'], ['um', 'deg']):
                save_stats(d[key], os.path.join(output_dir, key + '.csv'),
                           unit)

            for key in ['Raw Images', 'Flow Images', 'Combined Images']:
                img_ser_dir = os.path.join(output_dir, key)
                os.mkdir(img_ser_dir)
                save_img_ser(d[key], img_ser_dir)
                save_video(img_ser_dir, os.path.join(img_ser_dir,
                           key.split()[0] + '.mp4v'))

            save_mag_scatter([s['mean'] for s in d['mag_stats']],
                             os.path.join(output_dir, 'Magnitude Scatter.png'))
            save_dirn_scatter([s['mean'] for s in d['mag_stats']],
                              os.path.join(output_dir,
                              'Direction Scatter.png'))

            heatmap_dir = os.path.join(output_dir, 'Heatmaps')
            os.mkdir(heatmap_dir)
            quiver_dir = os.path.join(output_dir, 'Quiver Plots')
            os.mkdir(quiver_dir)
            save_heatmaps(d['preds'], heatmap_dir)
            save_quiver_plots(d['preds'], quiver_dir)

            save_img_ser_metadata(d, output_dir)
            gen_report(output_dir, config['report_path'])


def gen_report(output_dir, report_path):
    with open(report_path) as f:
        nb = nbformat.read(f, as_version=4)
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        ep.allow_errors = True
        try:
            ep.preprocess(nb, {'metadata': {'path': output_dir}})
        except CellExecutionError:
            msg = ('Error generating report, see notebook {} for the trace'
                   'back.'.format(os.path.join(output_dir, 'report.ipynb')))
            warnings.warn(msg, UserWarning)
        finally:
            with open(os.path.join(output_dir, 'report.ipynb'), 'w',
                      encoding='utf-8') as f:
                nbformat.write(nb, f)

    with open(os.path.join(output_dir, 'report.ipynb')) as f:
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
                          notebook_name=os.path.join(output_dir, 'report'))


def save_img_ser_metadata(data, output_dir):
    metadata = data['Raw Images'][0].metadata['img_ser_md']
    now = datetime.now()
    dt_str = now.strftime('%d %B %Y, %H:%M:%S')
    metadata['analysis_timestamp'] = dt_str
    with open(os.path.join(output_dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=4, sort_keys=True, default=str)


def save_mag_scatter(mags, path, dpi=1000):
    times = list(range(1, len(mags) + 1))
    plt.figure()
    plt.scatter(times, mags)
    plt.title('Flow Magnitude')
    plt.xlabel('Frame')
    plt.ylabel('μm')
    plt.ylim(0, max(mags) * 1.5)
    plt.savefig(path, dpi=dpi)
    plt.close(plt.gcf())


def save_dirn_scatter(dirns, path, dpi=1000):
    times = list(range(1, len(dirns) + 1))
    plt.figure()
    plt.scatter(times, dirns)
    plt.title('Flow Angle')
    plt.xlabel('Frame')
    plt.ylabel('Degrees')
    # plt.ylim(0, 360)
    plt.savefig(path, dpi=dpi)
    plt.close(plt.gcf())


def save_heatmaps(preds, output_dir, step=0, dpi=1000, fps=5):
    for i, pred in enumerate(preds):
        fig = plt.figure(frameon=False)
        plt.xticks([])
        plt.yticks([])
        plt.Axes(fig, [0, 0, 1, 1])
        plt.axis('off')
        pred = np.copy(pred)
        pred[:, :, 1] = pred[:, :, 1] * -1
        u, v = ((pred[::step, ::step, 0].astype(np.float32),
                pred[::step, ::step, 1].astype(float)) if step != 0 else
                (pred[:, :, 0].astype(float), pred[:, :, 1].astype(float)))
        mag = cv2.cartToPolar(u, v, angleInDegrees=1)
        plt.pcolormesh(mag[0], cmap='hot')
        path = os.path.join(output_dir, 'heatmap_{}.png'.format(i))
        plt.savefig(path, dpi=dpi, bbox_inches=0)
        plt.close(plt.gcf())

    path = os.path.join(output_dir, 'heatmap.mp4v')
    try:
        save_video(output_dir, path, fps=fps)
    except Exception as e:
        msg = 'Could not save video, reason: {}.'.format(str(e))
        warnings.warn(msg, UserWarning)


def save_quiver_plots(preds, output_dir, step=70, dpi=1000, fps=5):
    for i, pred in enumerate(preds):
        fig = plt.figure(frameon=False)
        plt.xticks([])
        plt.yticks([])
        plt.Axes(fig, [0, 0, 1, 1])
        plt.axis('off')
        pred = np.copy(pred)
        pred[:, :, 1] = pred[:, :, 1] * -1
        plt.quiver(np.arange(0, pred.shape[1], step), np.arange(pred.shape[0],
                   -1, -step), pred[::step, ::step, 0],
                   pred[::step, ::step, 1])
        path = os.path.join(output_dir, 'quiver_plot_{}.png'.format(i))
        plt.savefig(path, dpi=dpi, bbox_inches=0)
        plt.close(plt.gcf())

    path = os.path.join(output_dir, 'quiver_plot.mp4v')
    try:
        save_video(output_dir, path, fps=fps)
    except Exception as e:
        msg = 'Could not save video, reason: {}.'.format(str(e))
        warnings.warn(msg, UserWarning)


def gen_base_metrics(data, mpp):
    for i, pred in enumerate(data['preds']):
        mag, dirn = cv2.cartToPolar(pred[..., 0].astype(float),
                                    pred[..., 1].astype(float),
                                    angleInDegrees=1)
        data['mags'].append(mag)
        data['dirns'].append(dirn)
        mag[np.isnan(mag)] = 0  # remove NaNs
        mag *= (data['Raw Images'][0].metadata['mpp'] if 'mpp' in
                data['Raw Images'][0].metadata else mpp)  # convert to um
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
