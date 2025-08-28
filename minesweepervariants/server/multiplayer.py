

from flask import Request
from .model import Model


class MPModel(Model):
    def __init__(self, host: Model | None = None, token: str = '',  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.players: list[Model] = []
        self.token = token
        self.host = host
        print(f"MPModel initialized with token: {self.token}, host: {self.host}")
        if host is not None:
            if hasattr(host, "add_player") and callable(getattr(host, "add_player")):
                getattr(host, "add_player")(self)


    def add_player(self, player: Model):
        self.players.append(player)

    def remove_player(self, player: Model):
        self.players.remove(player)

    def generate_board(self, args, json):
        from minesweepervariants.impl.summon.game import GameSession

        if self.host is None:
            result = super().generate_board(args, json)
            return result

        try:
            host_game = self.host.get_game()
        except Exception as e:
            return {"reason": f"主机未准备好: {e}", "success": False}, 200

        try:
            _ = host_game.board
            _ = host_game.answer_board
        except Exception as e:
            return {"reason": f"主机棋盘未准备好: {e}", "success": False}, 200


        summon_arg = getattr(self.host, "summon", None) or getattr(host_game, "summon", None)
        if summon_arg is None:
            return {"reason": "主机的 Summon 未初始化", "success": False}, 500

        new_game = GameSession(
            summon=summon_arg,
            mode=host_game.mode,
            drop_r=host_game.drop_r,
            ultimate_mode=host_game.ultimate_mode,
        )
        new_game.flag_tag = host_game.flag_tag
        new_game.clue_tag = host_game.clue_tag
        new_game.answer_board = host_game.answer_board.clone()
        new_game.board = host_game.origin_board.clone()

        self.rules = self.host.rules
        self.game = new_game
        self.board = new_game.board

        self.reset(args, json)

        return {"reason": "", "success": True}, 200
