import glob
import json
import os
from io import StringIO
import time

import pandas as pd
import requests


def split_eyetracking_file():
    # Read in the data
    df = pd.read_csv('data/EyeTrackingData.csv')

    # Split by sessionId
    session_ids = df['sessionId'].unique()

    for session_id in session_ids:
        # Get the data for this session
        session_df = df[df['sessionId'] == session_id]

        # Save the data to a file with the session id as the name
        if not os.path.exists('data/eye_tracking'):
            os.mkdir('data/eye_tracking')
        session_df.to_csv(f'data/eye_tracking/{session_id}.csv', index=False, )


def send_request(file_path):
    # Define the column mapping
    column_mapping = {
        'left_x': 'LeftEyeX',
        'left_y': 'LeftEyeY',
        'right_x': 'RightEyeX',
        'right_y': 'RightEyeY',
        'time': 'timestamp',
    }

    with open(file_path, 'rb') as f:
        file_content = f.read()

    request_url = 'https://eyetracking-01-hubii.k8s.iism.kit.edu/eyetracking/'
    request_body = {
        'column_mapping': json.dumps(column_mapping),
        'sep:': ',',
    }
    files = {'file': ('file.csv', file_content, 'type=text/csv')}

    # Send the request to the server
    response = requests.post(request_url, data=request_body, files=files)
    return response.json()["task"]


def get_fixation_data(for_task_id):
    request_url = f'https://eyetracking-01-hubii.k8s.iism.kit.edu/eyetracking/result/fixation'
    response = requests.get(request_url, params={'task_id': for_task_id})
    return response.text


def get_saccade_data(for_task_id):
    request_url = f'https://eyetracking-01-hubii.k8s.iism.kit.edu/eyetracking/result/saccades'
    response = requests.get(request_url, params={'task_id': for_task_id})
    return response.text


if __name__ == '__main__':

    if not os.path.exists('data/eye_tracking'):
        print("Splitting eyetracking file")
        split_eyetracking_file()

    # Get all csv files
    print("Loading files")
    eyetracking_files = glob.glob('data/eye_tracking/*.csv')
    eyetracking_filenames = [os.path.basename(file).split(".")[0] for file in eyetracking_files]
    task_ids = []

    for index, eyetracking_file in enumerate(eyetracking_files):
        print(f"Sending request for file {index + 1}/{len(eyetracking_files)}")
        task_id = send_request(eyetracking_file)
        task_ids.append(task_id)

    all_tasks = []
    time.sleep(100)
    for index, task_id in enumerate(task_ids):
        print(f"Getting data for task {index + 1}/{len(task_ids)}")

        fixations_data = StringIO(get_fixation_data(task_id))
        saccades_data = StringIO(get_saccade_data(task_id))

        fixations_df = pd.read_csv(fixations_data)
        saccades_df = pd.read_csv(saccades_data)

        task_data = {
            'fixations': fixations_df,
            'saccades': saccades_df,
        }

        if not os.path.exists('data/eye_tracking/results'):
            os.mkdir('data/eye_tracking/results')

        fixations_df.to_csv(f'data/eye_tracking/results/{eyetracking_filenames[index]}_fixations.csv', index=False)
        saccades_df.to_csv(f'data/eye_tracking/results/{eyetracking_filenames[index]}_saccades.csv', index=False)

        all_tasks.append(task_data)

    all_fixations_df = pd.concat([task['fixations'] for task in all_tasks])
    all_saccades_df = pd.concat([task['saccades'] for task in all_tasks])

    all_fixations_df.to_csv('data/eye_tracking/results/all_fixations.csv', index=False)
    all_saccades_df.to_csv('data/eye_tracking/results/all_saccades.csv', index=False)

    print("Done")
