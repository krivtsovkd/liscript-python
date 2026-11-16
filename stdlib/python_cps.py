def fib_rec_naive(n):
    if (n <= 1):
        return n
    else:
        return fib_rec_naive(n - 1) + fib_rec_naive(n - 2)


def fib_dp_naive(n):
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]

    return dp[n]


def fib_dp_optimal(n):
    dp = [0, 1]
    for i in range(2, n + 1):
        dp = [dp[1], dp[0] + dp[1]]
    return dp[1]


noms = [1, 5, 10, 25, 50]


def cc_rec_naive(sum, nom_idx):
    if sum == 0:
        return 1
    if sum < 0:
        return 0
    if nom_idx < 0:
        return 0

    return cc_rec_naive(sum - noms[nom_idx], nom_idx) + cc_rec_naive(sum, nom_idx - 1)


def get_2d(arr, i, j):
    if i < 0 or j < 0 or i >= len(arr) or j >= len(arr[0]):
        return 0
    return arr[i][j]


# 1 0 0 0 0 ...
# 1 0 0 0 0 ...
# 1 0 0 0 0 ...
# 1 0 0 0 0 ...
# 1 0 0 0 0 ...
def cc_dp_naive(sum):
    dp = [[0 for i in range(sum+1)] for j in range(len(noms))]
    for i in range(len(noms)):
        dp[i][0] = 1

    # dp[i][j] = dp[i][j - noms[i]] + dp[i - 1][j]
    for j in range(1, sum + 1):
        for i in range(len(noms)):
            dp[i][j] = get_2d(dp, i, j - noms[i]) + get_2d(dp, i - 1, j)

    return dp[len(noms) - 1][sum]


row_len = max(noms)


def get_2d_cb(arr, i, j):
    if i < 0 or j < 0 or i >= len(arr):
        return 0
    return arr[i][j % row_len]


def cc_dp_optimal(sum):
    dp = [[0 for j in range(row_len)] for i in range(len(noms))]
    for i in range(len(noms)):
        dp[i][0] = 1

    # dp[i][j] = dp[i][j - noms[i]] + dp[i - 1][j]
    for j in range(1, sum + 1):
        for i in range(len(noms)):
            dp[i][j % row_len] = get_2d_cb(dp, i, j - noms[i]) + get_2d_cb(dp, i - 1, j)

    return dp[len(noms) - 1][sum % row_len]


fib_memo = [-1] * int(1e6)
def fib_rec_memo(n):
    if (n <= 1):
        return n
    elif fib_memo[n] != -1:
        return fib_memo[n]
    else:
        fib_memo[n] = fib_rec_memo(n - 1) + fib_rec_memo(n - 2)
        return fib_memo[n]


class Tr:
    def __init__(self, exp):
        self.exp = exp


def eval_tr(tr):
    while isinstance(tr, Tr):
        tr = tr.exp()

    return tr


def nrtshaei(n, v):
    fib_memo[n] = v
    return v


def fib_cps_memo(cont, n):
    if (n <= 1):
        return cont(n)
    elif fib_memo[n] != -1:
        return cont(fib_memo[n])
    else:
        return Tr(lambda: fib_cps_memo(lambda x: (Tr(lambda: fib_cps_memo(lambda y: cont(nrtshaei(n, x + y)), n - 2))), n - 1))


cc_memo = dict()
def cc_rec_memo(sum, nom_idx):
    if sum == 0:
        return 1
    if sum < 0:
        return 0
    if nom_idx < 0:
        return 0

    if (sum, nom_idx) in cc_memo:
        return cc_memo[(sum, nom_idx)]

    cc_memo[(sum, nom_idx)] = cc_rec_memo(sum - noms[nom_idx], nom_idx) + cc_rec_memo(sum, nom_idx - 1)
    return cc_memo[(sum, nom_idx)]


def nrtshaei2(n, v):
    cc_memo[n] = v
    return v


def cc_cps_memo(cont, sum, nom_idx):
    if sum == 0:
        return cont(1)
    if sum < 0:
        return cont(0)
    if nom_idx < 0:
        return cont(0)

    if (sum, nom_idx) in cc_memo:
        return cont(cc_memo[(sum, nom_idx)])

    return Tr(lambda: cc_cps_memo(lambda x: Tr(lambda: cc_cps_memo(lambda y: cont(nrtshaei2((sum, nom_idx), x + y)), sum, nom_idx - 1)), sum - noms[nom_idx], nom_idx))


def inc(cont, a):
    return cont(a + 1)


def timesten(cont, a):
    return cont(10 * a)


def sum(cont, n):
    if n <= 0:
        return cont(0)
    return sum(lambda x: cont(n + x), n - 1)


def id(a):
    return a


# inc(id, 0)

# timesten(lambda x: inc(id, x), 1)

# inc(id, timesten(id, 1))

def lambda_gen(f, n):
    return lambda x: f(n + x)


def sum2(n):
    cont = id
    for i in range(n, 0, -1):
        cont = lambda_gen(cont, i)

    return cont(0)
