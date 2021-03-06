
from sample_players import DataPlayer


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
        depth_limit = 1
        while True:
            choice = self.alpha_beta_search(state, depth_limit=depth_limit)
            self.queue.put(choice)

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
        my_position = gameState.locs[0]
        opponent_position = gameState.locs[1]

        return len(gameState.liberties(my_position)) - len(gameState.liberties(opponent_position))

