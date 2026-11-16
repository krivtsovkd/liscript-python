; ; (def (symbol (1 1)) 0 (symbol (1 2)) 0 ...)
; (defn defpos-codegen (all-positions)
;   (cons def
;     (reduce
;       (lambda (acc p) (cons (symbol p) (cons 0 acc))) nil all-positions)))


; (defn multiset (all-positions)
;   (eval (defpos-codegen all-positions))
;   (def distinct 0)

;   (defn add (value)
;     (def sym (symbol value))
;     (cond (= 0 (eval sym)) (+= distinct 1) nil)
;     (eval (list += sym 1)))

;   (defn remove (value)
;     (def sym (symbol value))
;     (cond (<= (eval sym) 0) (error "cant remove nonexistent element from multiset") nil)
;     (cond (= 1 (eval sym)) (-= distinct 1) nil)
;     (eval (list -= sym 1)))

;   (lambda (input) (eval input)))


; (defn set (all-steps)
;   (eval (defpos-codegen all-steps))

;   (defn add (value)
;     (def sym (symbol value))
;     (eval (list set! sym 1)))

;   (defn remove (value)
;     (def sym (symbol value))
;     (eval (list set! sym 0)))

;   (defn contains? (value)
;     (def sym (symbol value))
;     (= 1 (eval sym)))

;   (lambda (input) (eval input)))


; (def concat
;   (reduce (lambda (acc e) (append acc e)) nil))

; (def concat-reverse
;   (reduce (lambda (acc e) (append-reverse acc e)) nil))


(defn multiset (max-x max-y)
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


(defn set (max-x max-y all-directions)
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


(defn knight (max-x max-y x-0 y-0)
  (def points-count (* max-x max-y))
  (def p-0 (list x-0 y-0))
  (def all-directions '((2 1) (1 2) (-1 2) (-2 1) (-2 -1) (-1 -2) (1 -2) (2 -1)))

  (def path-set (multiset max-x max-y))
  (def step-set (set max-x max-y all-directions))

  (defn has-step? (path from to)
    ((step-set 'contains?) from to))

  (defn bad-pos? (path pos)
    (not (and (<= 1 (car pos) max-x)
              (<= 1 (car (cdr pos)) max-y)
              (not (has-step? path (car path) pos)))))

  (defn good-path? (path)
    (and
      (= (car path) p-0)
      (= (path-set 'distinct-count) points-count)))

  ; ((pos1 pos2 pos3 ...) (pos2 pos3 ...) (pos3 ...) ...)

  ; ((dir1 dir2 dir3 ...)
  ;  (dir4 dir5 dir6 ...)
  ; ...)
  ; (defn search (path dirs-stack) ; -> path or false
  ;   (cond
  ;     (nil? path) false
  ;     (do
  ;       (def unstepped-directions (car dirs-stack))
  ;       (cond
  ;         (good-path? path) path
  ;         (nil? unstepped-directions)
  ;           (do
  ;             (cond (not (nil? (cdr path)))
  ;               ((step-set 'remove) (car (cdr path)) (car path)))
  ;             ((path-set 'remove) (car path))
  ;             (search (cdr path) (cdr dirs-stack)))
  ;         (do
  ;           (def next-pos (zip-with + (car path) (car unstepped-directions)))
  ;           (def next-dirs (cons (cdr unstepped-directions) (cdr dirs-stack)))
  ;           (cond
  ;             (bad-pos? path next-pos) (search path next-dirs)
  ;             (do
  ;               ((step-set 'add) (car path) next-pos)
  ;               ((path-set 'add) next-pos)
  ;               (search (cons next-pos path) (cons all-directions next-dirs)))))))))


  ((path-set 'add) p-0)
  (def path (list p-0) dirs-stack (list all-directions) result nil)

  (while (not (nil? path))
    (def unstepped-directions (car dirs-stack))
    (cond
      (good-path? path) (set! result path path nil)
      (nil? unstepped-directions)
        (do
          (when (not (nil? (cdr path)))
            ((step-set 'remove) (car (cdr path)) (car path)))
          ((path-set 'remove) (car path))
          (set! path (cdr path) dirs-stack (cdr dirs-stack)))
      (do
        (def next-pos (zip-with + (car path) (car unstepped-directions)))
        (def next-dirs (cons (cdr unstepped-directions) (cdr dirs-stack)))
        (cond
          (bad-pos? path next-pos) (set! dirs-stack next-dirs)
          (do
            ((step-set 'add) (car path) next-pos)
            ((path-set 'add) next-pos)
            (set!
              path (cons next-pos path)
              dirs-stack (cons all-directions next-dirs)))))))

  result)
