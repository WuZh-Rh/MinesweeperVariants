def Number(n: int | float | str):
    return {
        'type': 'template',
        'style': '',
        'value': {
            'name': 'str',
            'value': n
        }
    }


def MultiNumber(n: list[int | float | str]):
    return {
        'type': 'template',
        'style': '',
        'value': {
            'name': 'multiStr',
            'value': n
        }
    }
