; (def (symbol (1 1)) 0 (symbol (1 2)) 0 ...)
(defn defpos-codegen (all-positions)
  (cons def
    (reduce
      (lambda (acc p) (cons (symbol p) (cons 0 acc))) nil all-positions)))


(defn multiset (all-positions)
  (eval (defpos-codegen all-positions))
  (def distinct 0)

  (defn add (value)
    (def sym (symbol value))
    (cond (= 0 (eval sym)) (+= distinct 1) nil)
    (eval (list += sym 1)))

  (defn remove (value)
    (def sym (symbol value))
    (cond (<= (eval sym) 0) (error "cant remove nonexistent element from multiset") nil)
    (cond (= 1 (eval sym)) (-= distinct 1) nil)
    (eval (list -= sym 1)))

  (lambda (input) (eval input)))


(defn set (all-steps)
  (eval (defpos-codegen all-steps))

  (defn add (value)
    (def sym (symbol value))
    (eval (list set! sym 1)))

  (defn remove (value)
    (def sym (symbol value))
    (eval (list set! sym 0)))

  (defn contains? (value)
    (def sym (symbol value))
    (= 1 (eval sym)))

  (lambda (input) (eval input)))


(def concat
  (reduce (lambda (acc e) (append acc e)) nil))

(def concat-reverse
  (reduce (lambda (acc e) (append-reverse acc e)) nil))


(defn knight (max-x max-y x-0 y-0)
  (def points-count (* max-x max-y))
  (def p-0 (list x-0 y-0))
  (def all-directions '((2 1) (1 2) (-1 2) (-2 1) (-2 -1) (-1 -2) (1 -2) (2 -1)))

  (def all-positions
    (reduce
      (lambda (acc x)
        (append acc
          (map (lambda (y) (list x y)) (range 1 max-y))))
      nil
      (range 1 max-x)))

  (defn in-field? (pos)
    (and
      (<= 1 (car pos) max-x)
      (<= 1 (car (cdr pos)) max-y)))

  (def all-steps
    (concat-reverse
      (map-tco
        (lambda (p)
          (map-tco (lambda (next-pos) (list p next-pos))
            (filter in-field?
              (map-tco (lambda (dir) (zip-with + p dir)) all-directions))))
        all-positions)))

  (def path-set (multiset all-positions))
  (def step-set (set all-steps))

  ; (defn has-step? (path from to)
  ;   (cond
  ;     (nil? path) false
  ;     (nil? (cdr path)) false
  ;     (and (= to (car path)) (= from (car (cdr path)))) true
  ;     (has-step? (cdr path) from to)))
  (defn has-step? (path from to)
    ((step-set 'contains?) (list to from)))

  (defn bad-pos? (path pos)
    ; (pm (x y) pos)
    (not (and (<= 1 (car pos) max-x)
              (<= 1 (car (cdr pos)) max-y)
              (not (has-step? path (car path) pos)))))

  ; (defn good-path? (path)
  ;   (and
  ;     (= (car path) p-0)
  ;     (= (length (distinct path)) points-count)))

  (defn good-path? (path)
    (and
      (= (car path) p-0)
      (= (path-set 'distinct) points-count)))

  ; ((pos1 pos2 pos3 ...) (pos2 pos3 ...) (pos3 ...) ...)

  ; ((dir1 dir2 dir3 ...)
  ;  (dir4 dir5 dir6 ...)
  ; ...)
  (defn search (path dirs-stack) ; -> path or false
    (cond
      (nil? path) false
      (do
        (def unstepped-directions (car dirs-stack))
        (cond
          (good-path? path) path
          (nil? unstepped-directions)
            (do
              (cond (not (nil? (cdr path)))
                ((step-set 'remove) (list (car path) (car (cdr path))))
                nil)
              ((path-set 'remove) (car path))
              (search (cdr path) (cdr dirs-stack)))
          (do
            (def next-pos (zip-with + (car path) (car unstepped-directions)))
            (def next-dirs (cons (cdr unstepped-directions) (cdr dirs-stack)))
            (cond
              (bad-pos? path next-pos) (search path next-dirs)
              (do
                ((step-set 'add) (list next-pos (car path)))
                ((path-set 'add) next-pos)
                (search (cons next-pos path) (cons all-directions next-dirs)))))))))

  ((path-set 'add) p-0)
  (search (list p-0) (list all-directions))
  ; (print all-steps)
)
