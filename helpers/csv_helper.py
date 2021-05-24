import random

import numpy as np
import pandas


def create_new_import_users_file(filename):
    df = pandas.read_csv(f'data\\{filename}.csv')

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

    df.to_csv(f'data\\{filename}_mod.csv', index=False, na_rep='NaN')
