from io import TextIOWrapper
import json
import numpy as np

def _collapse_duplicate_rows(data):
    change_points = np.where(~np.all(data[:-1] == data[1:], axis=1))[0] + 1

    group_starts = np.concatenate(([0], change_points))
    group_ends = np.concatenate((change_points, [len(data)]))

    unique = data[group_starts]
    counts = group_ends - group_starts #type:ignore

    return counts, unique

def _collapse_duplicate_values(data):
    change_points = np.where(data[:-1] != data[1:])[0] + 1

    group_starts = np.concatenate(([0], change_points))
    group_ends = np.concatenate((change_points, [len(data)]))

    unique_values = data[group_starts]
    counts = group_ends - group_starts # type:ignore

    return counts, unique_values

def _serialize_value(val) -> str:
    count, value = val

    if count == 1:
        return str(value)

    return f'{count}x{value}'

def _serialize_row(row) -> str:
    return ','.join(_serialize_value(val) for val in row)

def serialize(file: TextIOWrapper, lights, metadata: dict):
    color_table, color_indices = np.unique(lights, return_inverse=True)
    color_indices = np.reshape(color_indices, lights.shape)

    metadata['colors'] = color_table.tolist()

    counts, unique_rows = _collapse_duplicate_rows(color_indices)

    data = zip(counts, [list(zip(*_collapse_duplicate_values(row))) for row in unique_rows])

    file.write(json.dumps(metadata) + '\n')

    for count, row in data:
        if count == 1:
            file.write(_serialize_row(row) + '\n')
        else:
            file.write(f'{count}r[{_serialize_row(row)}]\n')
