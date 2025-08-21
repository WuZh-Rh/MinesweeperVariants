def Number(n: int | float):
    return {
        'type': 'template',
        'style': '',
        'value': {
            'name': 'number',
            'value': n
        }
    }

def MultiNumber(n: list[int | float]):
    return {
        'type': 'template',
        'style': '',
        'value': {
            'name': 'multiNumber',
            'value': n
        }
    }