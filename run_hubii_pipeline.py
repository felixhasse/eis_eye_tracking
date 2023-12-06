import glob
import json
import os
import requests

from split_eyetracking_file import split_eyetracking_file


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
    request_url = f'https://eyetracking-01-hubii.k8s.iism.kit.edu/eyetracking/fixation'
    response = requests.get(request_url, params={'task_id': for_task_id})
    return response.json()


def get_saccade_data(for_task_id):
    request_url = f'https://eyetracking-01-hubii.k8s.iism.kit.edu/eyetracking/saccades'
    response = requests.get(request_url, params={'task_id': for_task_id})
    return response.json()


if __name__ == '__main__':

    if not os.path.exists('data/eye_tracking'):
        print("Splitting eyetracking file")
        split_eyetracking_file()

    # Get all csv files
    print("Loading files")
    eyetracking_files = glob.glob('data/eye_tracking/*.csv')
    eyetracking_filenames = [os.path.basename(file) for file in eyetracking_files]
    task_ids = []

    for index, eyetracking_file in enumerate(eyetracking_files):
        print(f"Sending request for file {index + 1}/{len(eyetracking_files)}")
        task_id = send_request(eyetracking_file)
        task_ids.append(task_id)

    for index, task_id in enumerate(task_ids):
        print(f"Getting data for task {index + 1}/{len(task_ids)}")
        task_data = {
            'fixations': get_fixation_data(task_id),
            'saccades': get_saccade_data(task_id),
        }
        if not os.path.exists('data/eye_tracking/results'):
            os.mkdir('data/eye_tracking/results')
        with open(f'data/eye_tracking/results/{eyetracking_filenames[index]}.json', 'w') as file:
            json.dump(task_data, file)
