# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_utils.ipynb (unless otherwise specified).

__all__ = ['log_datadir_as_artifact', 'get_dicom_metadata', 'get_all_dicom_metadata', 'get_patient_id',
           'get_image_plane']

# Cell
import os
import wandb
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# pydicom related imports
import pydicom
from pydicom.pixel_data_handlers.util import apply_voi_lut

# Cell
def log_datadir_as_artifact(wandb_run, path_to_dir, artifact_name, artifact_type='dataset'):
    """
    Logs a data directory as an artifact in wandb.
    wandb_run: wandb.Run object
    path_to_dir: path to the data directory
    artifact_name: name of the artifact
    artifact_type: type of the artifact
    """

    artifact = wandb.Artifact(artifact_name, type=artifact_type)
    artifact.add_dir(path_to_dir)
    wandb_run.log_artifact(artifact)


# Cell
def get_dicom_metadata(path_to_dicom_file, meta_cols):
    """
    Returns the metadata of a single dicom file as a dictionary.

    Params:
        path_to_dicom_file: path to the dicom file
        meta_cols: list of metadata columns to extract
    """
    dicom_object = pydicom.dcmread(path_to_dicom_file)

    col_dict_train = dict()
    for col in meta_cols:
        try:
            col_dict_train[col] = str(getattr(dicom_object, col))
        except AttributeError:
            col_dict_train[col] = "NaN"

    return col_dict_train


# Cell
def get_all_dicom_metadata(df, meta_cols):
    """
    Retrieve metadata for each BraTS21ID and return as a dataframe.

    Params:
        df: dataframe with BraTS21IDs
        meta_cols: list of metadata columns to extract
    """
    meta_cols_dict = []
    for i in range(len(df)):
        row = df.iloc[i]
        path = Path(row.path)
        for scan_type in ['FLAIR', 'T1w', 'T1wCE', 'T2w']:
            dicomfile = os.listdir(path / scan_type)[0]
            dicom_metadata = get_dicom_metadata(path / scan_type / dicomfile, meta_cols)
            dicom_metadata['scan_type'] = scan_type
            dicom_metadata['id'] = row.BraTS21ID
            meta_cols_dict.append(dicom_metadata)

    return pd.DataFrame(meta_cols_dict)

# Cell
def get_patient_id(patient_id):
    """
    Returns the correct patient id of a dicom file.

    Parameters
    ----------
    patient_id: patient id of the dicom file
    """
    if patient_id < 10:
        return '0000'+str(patient_id)
    elif patient_id >= 10 and patient_id < 100:
        return '000'+str(patient_id)
    elif patient_id >= 100 and patient_id < 1000:
        return '00'+str(patient_id)
    else:
        return '0'+str(patient_id)

# Cell
def get_image_plane(data):
    '''
    Returns the MRI's plane from the dicom data.

    Params:
        data: dictionary of dicom metadata

    '''
    x1,y1,_,x2,y2,_ = [round(j) for j in ast.literal_eval(data.ImageOrientationPatient)]
    cords = [x1,y1,x2,y2]

    if cords == [1,0,0,0]:
        return 'coronal'
    if cords == [1,0,0,1]:
        return 'axial'
    if cords == [0,1,0,0]:
        return 'sagittal'