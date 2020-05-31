from isolation.isolation import DebugState, _BLANK_BOARD
from sample_players import DataPlayer
from transform import transform

MAX_BOOK_LEVEL = 5  # how far down the turn tree we'll maintain a book for


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

            print(DebugState.from_state(state))

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

        depth_limit = 1

        while depth_limit < 2:
            opponent_idx = 1 - self.context["order"]

            if self.context.get("next_path", None) is not None:
                self.context["current_path"] = {**self.context["current_path"], **self.context["next_path"]}
            if state.locs[opponent_idx] is not None and MAX_BOOK_LEVEL - 1 not in self.context["current_path"].keys():
                # Update our current path with what the opponent did, so we can make
                # a judgment.
                self.context["current_path"][state.ply_count - 1] = state.locs[opponent_idx]

            # Decision-making
            print(self.context)
            choice = self.alpha_beta_search(state, depth_limit=depth_limit)

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

    def alpha_beta_search(self, gameState, depth_limit):
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
        print("loc: ", gameState.locs[self.context["order"]])
        print("actions: ", gameState.actions())
        for a in gameState.actions():
            v = self.min_value(gameState.result(a), alpha, beta, depth_limit=depth_limit, depth=1)
            if v > best_score:
                best_score = v
                best_move = a
                alpha = v
        return best_move

    # TODO: modify the function signature to accept an alpha and beta parameter
    def min_value(self, gameState, alpha, beta, depth_limit, depth=0):
        """ Return the value for a win (+1) if the game is over,
        otherwise return the minimum value over all legal child
        nodes.
        """
        if gameState.terminal_test():
            return gameState.utility(0)

        if depth >= depth_limit:
            return self.evaluation(gameState)

        v = float("inf")
        for a in gameState.actions():
            v = min(v, self.max_value(gameState.result(a), alpha, beta, depth_limit, depth + 1))
            if v <= alpha:
                return v
            beta = min(v, beta)
        return v

    # TODO: modify the function signature to accept an alpha and beta parameter
    def max_value(self, gameState, alpha, beta, depth_limit, depth=0):
        """ Return the value for a loss (-1) if the game is over,
        otherwise return the maximum value over all legal child
        nodes.
        """
        if gameState.terminal_test():
            return gameState.utility(0)

        if depth >= depth_limit:
            return self.evaluation(gameState)

        v = float("-inf")
        for a in gameState.actions():
            v = max(v, self.min_value(gameState.result(a), alpha, beta, depth_limit, depth + 1))
            if v >= beta:
                return v
            alpha = max(v, alpha)
        return v

    def evaluation(self, gameState):
        """
        Use an extension of Warnsdorff's heuristic for finding a Knight's Tour on an arbitrary board:
        Minimize the "accessibility" of your position, and maximize the accessibility of your opponent's position.
        :param gameState: A gamestate resulting from an action.
        :return:
        """
        my_position = gameState.locs[self.context["order"]]
        opponent_position = gameState.locs[1 - self.context["order"]]

        if gameState.ply_count < MAX_BOOK_LEVEL:
            print(gameState.ply_count)
            first = min(self.context["current_path"].keys()) if len(self.context["current_path"]) > 0 else 0
            path = [self.context["current_path"][ix] for ix in range(first, gameState.ply_count - 1)]
            path = tuple(path + [my_position])

            # Win/loss ratios were only calculated for paths starting in the lower-right quadrant.
            # Transform other paths to map onto these.
            transformed_path = transform(path)

            # Look up win/loss ratio for this particular path.
            # Win-loss ratios were always calculated for the first player in the path;
            # If we are the second player in the path, invert the ratio.
            ratio = abs(self.context["order"] - self.data[transformed_path])

            return ratio


        return len(gameState.liberties(opponent_position)) - 2 * len(gameState.liberties(my_position))
