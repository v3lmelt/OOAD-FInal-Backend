from typing import List

import pandas as pd
from sqlmodel import SQLModel

from Model.orderModel import OrderModel


# 将SQLModel转换成pandas的dataframe
def sqlmodel_to_df(objects: List[SQLModel], set_index: bool = True) -> pd.DataFrame:
    """Converts SQLModel objects into a Pandas DataFrame.
    Usage
    ----------
    df = sqlmodel_to_df(list_of_sqlmodels)
    Parameters
    ----------
    :param objects: List[SQLModel]: List of SQLModel objects to be converted.
    :param set_index: bool: Sets the first column, usually the primary key, to dataframe index."""

    records = [obj.dict() for obj in objects]
    columns = list(objects[0].schema()["properties"].keys())
    df = pd.DataFrame.from_records(records, columns=columns)
    return df.set_index(columns[0]) if set_index else df


def df_to_sqlmodel(df: pd.DataFrame) -> List[SQLModel]:
    """Convert a pandas DataFrame into a a list of SQLModel objects."""
    objs = [OrderModel(**row) for row in df.to_dict('records')]
    return objs
