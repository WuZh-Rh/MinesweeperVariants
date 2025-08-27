from typing import Literal


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

def StrWithArrow(n: str, arrow: Literal['up', 'down', 'left', 'right', 'up_down', 'left_right']):
    return {
        'type': 'template',
        'style': '',
        'value': {
            'name': 'strWithArrow',
            'value': {
                'text': n,
                'arrow': arrow
            }
        }
    }