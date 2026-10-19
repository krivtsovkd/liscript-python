# class List:
#     def __init__(self, car, cdr):
#         self.car = car
#         self.cdr = cdr


# def is_cons_list(val):
#     return val is List


# def cons(car, cdr):
#     return List(car, cdr)


# def car(list):
#     return list.car


# def cdr(list):
#     return list.cdr




# def is_cons_list(val):
#     return type(val) is tuple


# def cons(car, cdr):
#     return (car, cdr)


# def car(list):
#     return list[0]


# def cdr(list):
#     return list[1]


def is_cons_list(val):
    return callable(val)


def cons(car, cdr):
    return lambda f: f(car, cdr)


def fst(x, y):
    return x


def snd(x, y):
    return y


def car(list):
    return list(fst)


def cdr(list):
    return list(snd)


nil = cons(None, None)


def is_nil(lst):
    return lst == nil
