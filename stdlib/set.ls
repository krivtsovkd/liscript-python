(def max-x 8 max-y 8)
(def all-directions '((2 1) (1 2) (-1 2) (-2 1) (-2 -1) (-1 -2) (1 -2) (2 -1)))

(defn multiset ()
  (def init-codegen nil)
  (def x 1)
  (while (<= x max-x)
    (def y 1)
    (while (<= y max-y)
      (def sym (symbol (++ "p-" x "-" y)))
      (set! init-codegen (cons 0 init-codegen))
      (set! init-codegen (cons sym init-codegen))
      (+= y 1))
    (+= x 1))
  (eval (cons def init-codegen))

  (def total-count 0)
  (def distinct-count 0)

  (defn add (pos)
    (def sym (symbol (++ "p-" (car pos) "-" (car (cdr pos)))))
    (def val (eval sym))

    (+= total-count 1)
    (cond (= val 0) (+= distinct-count 1))
    (eval (list set! sym (+ val 1))))

  (defn remove (pos)
    (def sym (symbol (++ "p-" (car pos) "-" (car (cdr pos)))))
    (def val (eval sym))

    (when (> val 0)
      (-= total-count 1)
      (cond (= val 1) (-= distinct-count 1))
      (eval (list set! sym (- val 1)))))


  (lambda (input) (eval input)))

(defn set ()
  (def init-codegen nil)
  (def x 1)
  (while (<= x max-x)
    (def y 1)
    (while (<= y max-y)
      (def l all-directions)
      (while (not (nil? l))
        (pm ((dx dy) & _) l)
        (def x1 (+ x dx) y1 (+ y dy))

        (when (and (<= 1 x1 max-x) (<= 1 y1 max-y))
          (def sym (symbol (++ "s-" x "-" y "-" x1 "-" y1)))
          (set! init-codegen (cons false init-codegen))
          (set! init-codegen (cons sym init-codegen)))
        (set! l (cdr l)))
      (+= y 1))
    (+= x 1))
  (eval (cons def init-codegen))

  (def count 0)

  (defn add (from to)
    (pm ((from-x from-y) (to-x to-y)) (list from to))
    (def sym (symbol (++ "s-" from-x "-" from-y "-" to-x "-" to-y)))
    (def val (eval sym))

    (when (not val)
      (+= count 1)
      (eval (list set! sym true))))

  (defn remove (from to)
    (pm ((from-x from-y) (to-x to-y)) (list from to))
    (def sym (symbol (++ "s-" from-x "-" from-y "-" to-x "-" to-y)))
    (def val (eval sym))

    (when val
      (-= count 1)
      (eval (list set! sym false))))

  (defn contains? (from to)
    (pm ((from-x from-y) (to-x to-y)) (list from to))
    (def sym (symbol (++ "s-" from-x "-" from-y "-" to-x "-" to-y)))
    (eval sym))

  (lambda (input) (eval input)))
