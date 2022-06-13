import os
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pypeln as pl

from rainbow import OPTICAL_FLOW_FILENAME, RAW_IMGS_DIR_NAME
from rainbow.data_analysis import gen_report
from rainbow.optical_flow.model_manager import ModelManager
from rainbow.optical_flow.optical_flow import save_optical_flow
from rainbow.util import (cleanup_dir, load_nd2_imgs,
                          load_std_imgs, save_img_ser, save_img_ser_metadata)

from tqdm import tqdm

ND2_FEX = '.nd2'


def process_files(root_dir, config, num_workers=0, sub_dirs=False,
                  use_existing_flow=False, cleanup_output_dirs=True,
                  analyze_data=True, max_num_parl_preds=1):
    """Processes files located within root_dir.

    Finds valid files (image sequences) within root_dir from which to compute
    the optical flow from using an optical flow model and perform data
    analysis, if specificed.

    Args:
        root_dir (string): The path to an existing directory containing image
            sequences as .nd2 files or 2 or more image files in common formats
            (e.g. .png, .tiff).
        config (dict): A loaded Rainbow YAML configuration file.
        num_workers (int, optional): The maximum number of workers to utilize
            in parallel during execution. If set to 0, will automatically
            determine the number of workers that will utilize all available CPU
            cores.
        sub_dirs (bool, optional): If True, will search for image sequences in
            root_dir subfolders instead of the top level directory.
        use_existing_flow (bool, optional): If True, will use an already
        existing optical flow file, if one is found, for an image sequence
            instead of recomputing the optical flow.
        cleanup_output_dirs (bool, optional): If True, will remove all files
            and folders from existing output directories before saving new
            data.
        analyze_data (bool, optional): If True, will perform data analysis.
        max_num_parl_preds (int, optional): The maximum number of image
            sequences that can be fed to the optical flow model simultaneously.
    """
    # find potential image sequence directories
    # TODO is this optimal e.g. not sharing image sequences between workers?
    dirs = [curr_dir for curr_dir in Path(root_dir).iterdir() if len(files := [
        f for f in curr_dir.glob('*') if f.is_file()]) > 1 or len([
            f for f in files if f.suffix == ND2_FEX]) > 0] if sub_dirs else [
                Path(root_dir)]

    assert len(dirs) != 0, ('No directories containing image sequences could '
                            'be found.')

    # determine number of workers to utilize
    if num_workers == 0:
        num_workers = count - 1 if (count := os.cpu_count()) is not None else 1

    if num_workers > (num_dirs := len(dirs)):
        num_workers = num_dirs

    # get optical flow model ready
    model_manager = ModelManager(config['optical_flow_model'],
                                 config[config['optical_flow_model']],
                                 max_num_parl_preds, num_workers)
    model_manager.start()
    models = model_manager.models.copy()

    # begin parallel processing (but don't spawn new process if
    # num_workers = 1)
    worker = Worker(config, use_existing_flow, cleanup_output_dirs,
                    analyze_data)
    stage = (pl.process.map(worker, dirs, workers=num_workers,
             on_start=lambda: dict(model=models.pop())) if num_workers != 1
             else (worker(curr_dir, models[0]) for curr_dir in dirs))
    _ = (list(_ for _ in tqdm(stage, total=len(dirs))) if num_workers != 1 else
         [_ for _ in tqdm(stage, total=len(dirs))])

    model_manager.stop()


class Worker:
    """Worker that processes a directory containing image sequences.

    Image sequences can be in the form of .nd2 files or 2 or more image files
    in common formats (e.g. .png, .tiff). Will compute the optical flow in the
    image sequences and perform data analysis, if specified. Meant to be a
    called as a separate Python process.

    Attributes:
        config: A dict representing a loaded Rainbow YAML configuration file.
        use_existing_flow: A boolean indicating whether or not to use an
            existing optical flow file, if one is found, for an image sequence
            instead of recomputing the optical flow.
        cleanup: A boolean indicating whether or not to remove all files
            and folders from existing output directories before saving new
            data.
        analyze_data: A boolean indicating whether or not to perform data
            analysis.
    """
    def __init__(self, config, use_existing_flow=False,
                 cleanup_output_dirs=True, analyze_data=True):
        """Initializes the worker.

        Args:
            config (dict): A loaded Rainbow YAML configuration file.
            use_existing_flow (bool): If True, will use an already existing
                optical flow file for an image sequence, if found, instead of
                recomputing the optical flow.
            cleanup_output_dirs (bool): If True, will remove all files and
                folders from existing output directories before saving new
                data.
            analyze_data (bool): If True, will perform data analysis.
        """
        self.config = config
        self.use_existing_flow = use_existing_flow
        self.cleanup = cleanup_output_dirs
        self.analyze_data = analyze_data

    def __call__(self, curr_dir, model):
        img_seqs = self._load_image_sequences(curr_dir)
        for imgs in img_seqs:
            output_dir = Path(self._det_output_dir(imgs, self.config))
            output_dir.mkdir(exist_ok=True)
            f = output_dir / OPTICAL_FLOW_FILENAME
            raw_imgs_dir = output_dir / RAW_IMGS_DIR_NAME

            if not (self.use_existing_flow and f.is_file()):
                prepared_imgs = model.prepare(imgs)
                prepared_imgs.share_memory_()
                preds = model.run(prepared_imgs).numpy()
                save_optical_flow(preds, output_dir)
                self._save_raw_imgs(imgs, raw_imgs_dir)

            if self.cleanup:
                self._cleanup_output_dirs(f, raw_imgs_dir, output_dir)

            if self.analyze_data:
                gen_report(output_dir, self.config['report_path'])

    def _cleanup_output_dirs(self, f, raw_imgs_dir, output_dir):
        with NamedTemporaryFile(delete=False) as tmp_f:
            tmp_file = tmp_f.name

        with TemporaryDirectory() as tmp_dir:
            shutil.copy2(f, tmp_file)
            shutil.copytree(raw_imgs_dir, tmp_dir, dirs_exist_ok=True)
            if not cleanup_dir(output_dir):
                return
            output_dir.mkdir()
            shutil.copy2(tmp_file, f)
            shutil.copytree(tmp_dir, raw_imgs_dir, dirs_exist_ok=True)

        Path(tmp_file).unlink()

    def _load_image_sequences(self, curr_dir):
        img_seqs = ([imgs] if len(imgs := load_std_imgs(str(
            curr_dir.resolve()), self.config['mpp'])) > 1 else [])

        img_seqs += [imgs for nd2_imgs in [load_nd2_imgs(str(
            f.resolve()), self.config['nd2'], self.config['mpp']) for f in
            curr_dir.glob(f'*{ND2_FEX}')] for imgs in nd2_imgs if
            len(imgs) > 1]

        return img_seqs

    def _det_output_dir(self, imgs, config):
        name, ext = os.path.splitext(imgs[0].metadata['img_name'])
        ser = ('_Series_{})'.format(imgs[0].metadata[config['nd2'][
               'naming_axs'][0]]) if ext == '.nd2' else '')
        output_dir = '{}_{}{}_etc'.format(ext.replace('.', ''), name, ser)
        output_dir = output_dir.replace(' ', '_')
        output_dir = os.path.join(imgs[0].metadata['img_ser_md']['dir'],
                                  output_dir)

        return output_dir

    def _save_raw_imgs(self, imgs, raw_imgs_dir):
        if not cleanup_dir(raw_imgs_dir):
            return
        raw_imgs_dir.mkdir()
        save_img_ser(imgs, raw_imgs_dir)
        save_img_ser_metadata(imgs, raw_imgs_dir)
