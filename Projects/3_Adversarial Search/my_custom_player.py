from isolation.isolation import DebugState, _BLANK_BOARD
from sample_players import DataPlayer
from transform import transform
import random

MAX_BOOK_LEVEL = 5  # how far down the turn tree we'll maintain a book for

BASELINE = False
DEPTH_LIMIT = 3.5


class CustomPlayer(DataPlayer):

    """ Implement your own agent to play knight's Isolation

    The get_action() method is the only required method for this project.
    You can modify the interface for get_action by adding named parameters
    with default values, but the function MUST remain compatible with the
    default interface.

    **********************************************************************
    NOTES:
    - The test cases will NOT be run on a machine with GPU access, nor be
      suitable for using any other machine learning techniques.

    - You can pass state forward to your agent on the next turn by assigning
      any pickleable object to the self.context attribute.
    **********************************************************************
    """

    def get_action(self, state):
        """ Employ an adversarial search technique to choose an action
        available in the current state calls self.queue.put(ACTION) at least

        This method must call self.queue.put(ACTION) at least once, and may
        call it as many times as you want; the caller will be responsible
        for cutting off the function after the search time limit has expired.

        See RandomPlayer and GreedyPlayer in sample_players for more examples.

        **********************************************************************
        NOTE: 
        - The caller is responsible for cutting off search, so calling
          get_action() from your own code will create an infinite loop!
          Refer to (and use!) the Isolation.play() function to run games.
        **********************************************************************
        """
        # TODO: Replace the example implementation below with your own search
        #       method by combining techniques from lecture
        #
        # EXAMPLE: choose a random move without any search--this function MUST
        #          call self.queue.put(ACTION) at least once before time expires
        #          (the timer is automatically managed for you)

        if self.context is None:
            # Who started the game: if only one loc has been populated, the opponent did.
            # If two locs have been populated, then we started. If no locs have been populated, we started.
            board_check = int(state.locs[0] is not None) + int(state.locs[1] is not None)
            order = 0 if board_check in (0, 2) else 1

            self.context = {
                "current_path": {},
                "next_path": {},
                "order": order,
            }

            # In some runs both initial states are set, so we need to incorporate that into our path history.

            if state.locs[self.context["order"]] is not None:
                self.context["current_path"][state.ply_count - 2] = state.locs[self.context["order"]]

        # Update context

        opponent_idx = 1 - self.context["order"]
        if self.context.get("next_path", None) is not None:
            self.context["current_path"] = {**self.context["current_path"], **self.context["next_path"]}

        if state.locs[opponent_idx] is not None and MAX_BOOK_LEVEL - 1 not in self.context["current_path"].keys():
            # Update our current path with what the opponent did, so we can make
            # a judgment.
            self.context["current_path"][state.ply_count - 1] = state.locs[opponent_idx]

        depth_limit = 1

        while depth_limit < DEPTH_LIMIT:
            path = None
            if state.ply_count < MAX_BOOK_LEVEL:
                path = [self.context["current_path"][ix] for ix in range(state.ply_count)]

            # Decision-making
            if BASELINE and state.ply_count <= MAX_BOOK_LEVEL:
                # In the BASELINE case we just select a random move as opposed to relying on a Book
                # or Minimax search.
                choice = random.choice(state.actions())
                new_loc = int(choice) + state.locs[0] if state.locs[self.context["order"]] is not None else choice
                self.context["next_path"] = self.context["current_path"].copy()
                self.context["next_path"][state.ply_count] = new_loc
                self.queue.put(choice)
                return

            choice = self.alpha_beta_search(state, depth_limit=depth_limit, path=path)

            # Keep track of the choice we've just made to inform the next choice.
            # NOTE: Context must be updated before sending objects to the queue; the queue is what
            # passes context forward through turns.
            if MAX_BOOK_LEVEL - 1 not in self.context["next_path"].keys():
                new_loc = int(choice) + state.locs[0] if state.locs[self.context["order"]] is not None else choice
                self.context["next_path"] = self.context["current_path"].copy()
                self.context["next_path"][state.ply_count] = new_loc

            self.queue.put(choice)

            # Iteratively deepen
            depth_limit += 1

    def alpha_beta_search(self, gameState, depth_limit, path):
        """ Return the move along a branch of the game tree that
        has the best possible value.  A move is a pair of coordinates
        in (column, row) order corresponding to a legal move for
        the searching player.

        You can ignore the special case of calling this function
        from a terminal state.
        """
        alpha = float("-inf")
        beta = float("inf")
        best_score = float("-inf")
        best_move = None
        for a in gameState.actions():
            next_loc = a if gameState.locs[self.context["order"]] is None else int(a) + gameState.locs[self.context["order"]]
            next_path = path + [next_loc] if path is not None else None
            v = self.min_value(gameState.result(a), alpha, beta, depth_limit=depth_limit, depth=1, path=next_path)
            if v > best_score:
                best_score = v
                best_move = a
                alpha = v
        return best_move

    def min_value(self, gameState, alpha, beta, depth_limit, path, depth=0):
        """ Return the value for a win (+1) if the game is over,
        otherwise return the minimum value over all legal child
        nodes.
        """
        if gameState.terminal_test():
            return gameState.utility(0)

        if depth >= depth_limit:
            return self.evaluation(gameState, path)

        v = float("inf")
        for a in gameState.actions():
            next_loc = int(a) + gameState.locs[gameState.player()] if gameState.locs[gameState.player()] is not None else a
            next_path = path + [next_loc] if path is not None else None
            v = min(v, self.max_value(gameState.result(a), alpha, beta, depth_limit, next_path, depth + 1))
            if v <= alpha:
                return v
            beta = min(v, beta)
        return v

    def max_value(self, gameState, alpha, beta, depth_limit, path, depth=0):
        """ Return the value for a loss (-1) if the game is over,
        otherwise return the maximum value over all legal child
        nodes.
        """
        if gameState.terminal_test():
            return gameState.utility(0)

        if depth >= depth_limit:
            return self.evaluation(gameState, path)

        v = float("-inf")
        for a in gameState.actions():
            next_loc = int(a) + gameState.locs[gameState.player()] if gameState.locs[gameState.player()] is not None else a
            next_path = path + [next_loc] if path is not None else None
            v = max(v, self.min_value(gameState.result(a), alpha, beta, depth_limit, next_path, depth + 1))
            if v >= beta:
                return v
            alpha = max(v, alpha)
        return v

    def evaluation(self, gameState, path=None):
        """
        Use an extension of Warnsdorff's heuristic for finding a Knight's Tour on an arbitrary board:
        Minimize the "accessibility" of your position, and maximize the accessibility of your opponent's position.
        :param gameState: A gamestate resulting from an action.
        :return:
        """
        my_position = gameState.locs[self.context["order"]]
        opponent_position = gameState.locs[1 - self.context["order"]]

        if path is not None and len(path) <= MAX_BOOK_LEVEL and not BASELINE:
            # Win/loss ratios were only calculated for paths starting in the lower-right quadrant.
            # Transform other paths to map onto these.
            transformed_path = transform(tuple(path))

            # Look up win/loss ratio for this particular path.
            # Win-loss ratios were always calculated for the first player in the path;
            # If we are the second player in the path, invert the ratio.
            ratio = abs(self.context["order"] - self.data[transformed_path])
            return ratio


        return len(gameState.liberties(my_position)) - len(gameState.liberties(opponent_position))
