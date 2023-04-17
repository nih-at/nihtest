class CompareArrays:
    def __init__(self, expected, got):
        self.expected = expected
        self.got = got
        self.diff = []
        # keep copies of v/w from previous iterations for retracing our steps and getting the actual diff
        self.path_lengths = []
        # x dimension of G
        self.N = len(self.got)
        # y dimension of G
        self.M = len(self.expected)
        # upper limit on the number of differences this algorithm accepts
        # before giving up. If set to M+N like here it will never give up
        # and always find a path.
        self.max_size = self.M + self.N

    def get_diff(self):
        if self.expected == self.got:
            return []

        # Algorithm from
        # Eugene W. Myers - A O(ND) Difference algorithm and Its Variations

        # The graph G consists of nodes [x, y] where x is the index into
        # the array of lines "expected" and y is the index into the array
        # of lines "got". G(x,y) always has outgoing edges to G(x+1, y)
        # and G(x, y+1) with weight 1. Such an edge corresponds to
        # accepting the line expected[x] (or got[y] resp.) as different
        # and printing it. Additionally, an edge G(x, y) -> G(x+1, y+1)
        # with weight 0 exists if expected[x] is equal to got[y]. Going
        # along such an edge corresponds to finding a matching line in
        # expected and got.

        # The problem of finding the smallest diff corresponds to finding a
        # directed path from G(0, 0) to G(N, M) with minimal weight.

        # did we find a path from G(0, 0) to G(N, M)?
        done = False
        # v[k] = highest x coordinate we can reach after d non-diagonal
        # steps, where y = x - k
        # v is updated in-place in each iteration
        # The array v in the paper is [-max_size ... +max_size]; w is v rebased by max_size, i.e. v[k] = w[max_size + k]
        w = [999999999] * (2 * self.max_size + 1)

        # Initialize v[1] for first step of algorithm
        w[self.max_size + 1] = 0

        # loop over all possible differences, stop on the lowest one where we reach G(N, M)
        for d in range(0, self.max_size + 1):
            # update v_d[k] using v_{d-1}[k] - can be done in-place, so only v[k] is used here
            for k in range(-d, d + 1, 2):
                if k == -d or (k != d and w[self.max_size + k - 1] < w[self.max_size + k + 1]):
                    # step down, x does not increase
                    x = w[self.max_size + k + 1]
                else:
                    # step right, x increases
                    x = w[self.max_size + k - 1] + 1
                y = x - k
                # follow free edges (diagonal steps) as far as possible
                while x < self.N and y < self.M and self.got[x] == self.expected[y]:
                    # both lines are equal, so weight of path doesn't increase
                    x += 1
                    y += 1
                w[self.max_size + k] = x
                # did we reach G(N, M)? if yes, stop
                if x >= self.N and y >= self.M:
                    done = True
                    break

            # save v_d[k] for generating diff
            dest = []
            for i in w:
                dest.append(i)
            self.path_lengths.append(dest)
            if done:
                break

        if done:
            self.output(d, self.N, self.M)
        return self.diff

    def output(self, d, x, y):
        if d == 0:
            for i in range(0, x):
                self.diff.append(" " + self.expected[i])
            return

        lines = []
        wdprev = self.path_lengths[d - 1]
        k = x - y

        # walking backwards we cannot follow all diagonals completely,
        # going forward we might have entered in the middle of one
        while True:
            change = False
            # did we step right in the previous iteration?
            if x == wdprev[self.max_size + k - 1] + 1:
                self.output(d - 1, x - 1, y)
                self.diff.append("+" + self.got[x - 1])
                for line in reversed(lines):
                    self.diff.append(" " + line)
                return

            # did we step down in the previous iteration?
            if x == wdprev[self.max_size + k + 1]:
                self.output(d - 1, x, y - 1)
                self.diff.append("-" + self.expected[y - 1])
                for line in reversed(lines):
                    self.diff.append(" " + line)
                return

            # no match, so try going up diagonally one step and trying again
            if x > 0 and y > 0 and self.got[x - 1] == self.expected[y - 1]:
                # unchanged lines, for context
                lines.append(self.got[x - 1])
                x -= 1
                y -= 1
                change = True

            if not change:
                break

        raise RuntimeError("internal error creating diff")
