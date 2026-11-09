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
    ; (pm (x y) pos)
    (not (and (<= 1 (car pos) max-x)
              (<= 1 (car (cdr pos)) max-y)
              (not (has-step? path (car path) pos)))))

  (defn good-path? (path)
    (and
      (= (car path) p-0)
      (= (length (distinct path)) points-count)))

  ; ((dir1 dir2 dir3 ...)
  ;  (dir4 dir5 dir6 ...)
  ; ...)
  (defn search (paths-stack dirs-stack) ; -> path or false
    (cond
      (nil? paths-stack) false
      (do
        (def path (car paths-stack) unstepped-directions (car dirs-stack))
        (cond
          (good-path? path) path
          (nil? unstepped-directions) (search (cdr paths-stack) (cdr dirs-stack))
          (do
            (def next-pos (zip-with + (car path) (car unstepped-directions)))
            (def next-dirs (cons (cdr unstepped-directions) (cdr dirs-stack)))
            (cond
              (bad-pos? path next-pos) (search paths-stack next-dirs)
              (search (cons (cons next-pos path) paths-stack) (cons all-directions next-dirs))))))))

  (search (list (list p-0)) (list all-directions)))
