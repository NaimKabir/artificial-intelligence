
import itertools

WIDTH = 11
PADDED_WIDTH = WIDTH + 2 # Adjusting for our soft bitmap border
HEIGHT = 9

HORZ_MIDPOINT = (WIDTH // 2) + 1
VERT_MIDPOINT = (HEIGHT // 2) + 1

# Set up lambdas to detect what part of the board a location is in

is_upper_left = lambda start: start // PADDED_WIDTH >= VERT_MIDPOINT and start % PADDED_WIDTH >= HORZ_MIDPOINT
is_upper_right = lambda start: start // PADDED_WIDTH >= VERT_MIDPOINT and start % PADDED_WIDTH < HORZ_MIDPOINT
is_bottom_left = lambda start: start // PADDED_WIDTH < VERT_MIDPOINT and start % PADDED_WIDTH >= HORZ_MIDPOINT

# Functions for flipping locs around center axes
flip_horz = lambda loc: (loc // PADDED_WIDTH)*PADDED_WIDTH + WIDTH - (loc % PADDED_WIDTH) - 1
flip_vert = lambda loc: (HEIGHT - (loc // PADDED_WIDTH) - 1)*PADDED_WIDTH + (loc % PADDED_WIDTH)
rotate_180 = lambda loc: flip_horz(flip_vert(loc))

# Define set of starting points used to populate the opening book in OpeningBook.ipynb

def xy2ind(x, y):
    """
    Return a bitboard index for an x,y pair, where the (0,0) coordinate is bottom-right
    and values increase to the left and upward.
    """
    return PADDED_WIDTH * y + x


# Calculate the minimum set of positions we need to capture data
# that is generalizable via symmetry
STARTING_SET = [xy2ind(x, y) for x, y in itertools.product(range(6), range(5))]

def transform(path):
    """
    Transform any arbitrary path to a path with a starting position
    in the bottom right quadrant, so we can look up win/loss ratios in the 
    book we generated in OpeningBook.
    """
    start = path[0]

    if start in STARTING_SET:
        return path

    # If the starting position is in the upper-left quadrant, or the upper half of 
    # the vertical centerline, we can rotatate 180 degrees in either direction.
    if is_upper_left(start):
        return tuple(rotate_180(loc) for loc in path)
        
    # If the starting position is in the bottom left quadrant or the left half of
    # the horizontal centerline, we can flip all positions on the vertical axis
    if is_bottom_left(start):
        return tuple(flip_horz(loc) for loc in path)
    
    # If the starting position is on the top-right quadrant we can flip all positions
    # on the horizontal axis
    if is_upper_right(start):
        return tuple(flip_vert(loc) for loc in path)

