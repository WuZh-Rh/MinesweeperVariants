

from minesweepervariants.server.model import Model


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

    def generate_board(self):
        from minesweepervariants.impl.summon.game import GameSession

        if self.host is None:
            return super().generate_board()

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
        new_game.answer_board = host_game.answer_board.clone()
        new_game.board = host_game.board.clone()

        self.game = new_game
        self.board = new_game.board.clone()

        self.reset()

        return {"reason": "", "success": True}, 200
