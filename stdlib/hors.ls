(defn knight (max-x max-y x-0 y-0)
  (def points-count (* max-x max-y))
  (def p-0 (list x-0 y-0))
  (def all-directions '((2 1) (1 2) (-1 2) (-2 1) (-2 -1) (-1 -2) (1 -2) (2 -1)))

  (defn has-step? (path from to)
    (cond
      (nil? path) false
      (nil? (cdr path)) false
      (and (= to (car path)) (= from (car (cdr path)))) true
      (has-step? (cdr path) from to)))

  (defn bad-pos? (path pos)
    (pm (x y) pos)
    (not (and (<= 1 x max-x)
              (<= 1 y max-y)
              (not (has-step? path (car path) pos)))))

  (defn good-path? (path)
    (and
      (= (car path) p-0)
      (= (length (distinct path)) points-count)))

  (defn search (path unstepped-directions) ; -> path or false
    (cond
      (good-path? path) path
      (nil? unstepped-directions) false
      (do
        (def next-pos (zip-with + (car path) (car unstepped-directions)))
        (cond
          (bad-pos? path next-pos) (search path (cdr unstepped-directions))
          (do
            (def out (search (cons next-pos path) all-directions))
            (cond (= out false) (search path (cdr unstepped-directions)) out))))))

  (search (list p-0) all-directions))
