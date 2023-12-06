import os

import pandas as pd


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


if __name__ == '__main__':
    split_eyetracking_file()
