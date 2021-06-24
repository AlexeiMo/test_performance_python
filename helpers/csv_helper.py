import random
from pathlib import Path

import numpy as np
import pandas
from helpers.json_helper import read_json, write_json


def create_new_import_users_file(filename):
    filename = Path("data") / filename

    df = pandas.read_csv(f'{filename}.csv')

    for i in range(0, len(df.index)):
        username = ""
        email = ""
        for j in range(0, 20):
           username += str(random.randint(0, 9))
           email += str(random.randint(0, 9))

        email += "@gmail.com"

        df['username'].iloc[i] = username
        df['email'].iloc[i] = email

    username = ""
    email = ""
    for i in range(0, 20):
        username += str(random.randint(0, 9))
        email += str(random.randint(0, 9))

    email += "@gmail.com"

    df = df.rename(columns={"username": username, "email": email})

    for i in range(2, len(df.columns)):
        df = df.rename(columns={f"Unnamed: {i}": ""})

    df = df.replace(np.nan, '', regex=True)

    df.to_csv(f'{filename}_mod.csv', index=False, na_rep='NaN')


def create_new_import_requests_file(filename, request_id, status):
    filename = Path('data') / filename

    df = pandas.read_csv(f'{filename}.csv')

    for i in range(0, len(df.index)):

        df['Request ID'].iloc[i] = request_id
        df['Status'].iloc[i] = status

    df = df.rename(columns={"Request ID": request_id, "Status": status})

    df.to_csv(f'{filename}_mod.csv', index=False)


def change_tan(session, source_filename, tan_filename):
    file_to_open = Path("data") / source_filename

    data = read_json(file_to_open)

    df = pandas.read_csv(f'data\\{tan_filename}')

    tan_value = str(df["tan"].iloc[len(df.index) - 1])

    df = df.iloc[0:len(df.index) - 1]

    tan_filename = Path("data") / tan_filename

    df.to_csv(f'{tan_filename}', index=False)

    data["tanValue"] = tan_value

    write_json(file_to_open, data)

    session.headers.update(
        {"X-TAN": tan_value}
    )
