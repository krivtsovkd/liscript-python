(def error panic)
(def nil '())
(def nil? (lambda (l) (= l nil)))
(def list (lambda () rest-args))
(def list? (lambda (l) (= "list" (typeof l))))

(def benchmark (dambda (label f)
  (do
    (def benchmark-start-time (current-time))
    (eval f)
    (def time-taken-s (- (current-time) benchmark-start-time))
    (def time-taken-real (cond (>= time-taken-s 1.0) time-taken-s (* time-taken-s 1000.0)))
    (def time-taken-unit (cond (>= time-taken-s 1.0) "s" "ms"))
    (print "Benchmark" label "took" time-taken-real time-taken-unit))))


(def defracro (racro (name args body) (def name (racro args body))))

; (defmacro defn (name args)
;   (list def name
;     (list lambda args
;       (cond
;         (nil? rest-args) nil
;         (nil? (cdr rest-args)) (car rest-args)
;         (cons do rest-args)))))

; (defmacro += (name n) (list set! name (list + name n)))

; (defmacro or-impl (z)
;   (cond
;     (nil? z) false
;     (list cond (car z) true (list 'or-impl (cdr z)))))

; (defmacro or () (list 'or-impl rest-args))

; (defmacro or ()
;   (cond
;     (nil? rest-args) false
;     (nil? (cdr rest-args)) (car rest-args)
;     (list cond (car rest-args) true (cons 'or (cdr rest-args)))))

; (defmacro prepend-1-m (a l) (cons a l))
; (defmacro prepend-2-m (a b l) (cons a (cons b l)))

; (defmacro or-impl ()
;   (cond
;     (nil? rest-args) '(false)
;     (nil? (cdr rest-args)) rest-args
;     (list 'prepend-2-m (car rest-args) true (cons 'or-impl (cdr rest-args)))))

; (defmacro or ()
;   (cond
;     (nil? rest-args) false
;     (nil? (cdr rest-args)) (car rest-args)
;     (list 'prepend-1-m cond (cons 'or-impl rest-args))))

(def defn-codegen (lambda (name args body)
  (list def name
    (list lambda args
      (cond
        (nil? body) nil
        (nil? (cdr body)) (car body)
        (cons do body))))))
(defracro defn (name args) (eval (defn-codegen 'name 'args 'rest-args)))

(defn intersperse (e l)
  (cond
    (nil? l) nil
    (nil? (cdr l)) l
    (cons (car l) (cons e (intersperse e (cdr l))))))

; (defmacro or ()
;   (cond
;     (nil? rest-args) false
;     (nil? (cdr rest-args)) (car rest-args)
;     (cons cond (intersperse true rest-args))))

(defn not (b) (= false b))
(defracro or () (eval (cons cond (intersperse true 'rest-args))))

(defn and-codegen (l)
  (cond
    (nil? l) true
    (list cond (car l) (and-codegen (cdr l)) false)))
(defracro and () (eval (and-codegen 'rest-args)))

(defn t (a) (print "t: " a) a)

(defn fix (func) (func func))

(def fix-recursive-body (fix (lambda (self name body start?) (do
  (cond
    (nil? body) nil
    (list? (car body))
      (cons (self self name (car body) true) (self self name (cdr body) false))
    (and start? (= name (car body)))
      (cons name (cons name (self self name (cdr body) false)))
    (cons (car body) (self self name (cdr body) false)))))))

(def defnrec-codegen (lambda (name args body)
  (list def name
    (list fix
      (list lambda args
        (cond
          (nil? body) nil
          (nil? (cdr body)) (car body)
          (cons do body)))))))
(defracro defnrec (name args) (eval (defnrec-codegen 'name (cons 'name 'args) (fix-recursive-body 'name 'rest-args true))))

(defn append (a b)
  (cond
    (nil? a) b
    (cons (car a) (append (cdr a) b))))

; (defn min (a b) (cond (< a b) a b))
; (defn max (a b) (cond (> a b) a b))

(defn inc (a) (+ a 1))

(defnrec n-times (n f x)
  (cond
    (<= n 0) x
    (n-times (- n 1) f (f x))))

(defnrec list-ref (i l)
  (cond
    (< i 0) (error "Index < 0")
    (nil? l) (error "Index out of bounds")
    (= i 0) (car l)
    (list-ref (- i 1) (cdr l))))

(defnrec range (from to) (cond (> from to) nil (cons from (range (+ 1 from) to))))

(defnrec take (n l)
  (cond
    (<= n 0) nil
    (nil? l) nil
    (cons (car l) (take (- n 1) (cdr l)))))

(defnrec drop (n l)
  (cond
    (<= n 0) l
    (nil? l) nil
    (drop (- n 1) (cdr l))))

(defnrec contains? (elem l)
  (cond
    (nil? l) false
    (= elem (car l)) true
    (contains? elem (cdr l))))

(defnrec iter (f l)
  (cond
    (nil? l) nil
    (do (f (car l)) (iter f (cdr l)))))

(defnrec map (f l)
  (cond
    (nil? l) nil
    (cons (f (car l)) (map f (cdr l)))))

(defn init (length func) (map func (range 0 (- length 1))))
(defn repeat (len e)
  (cond
    (<= len 0) nil
    (cons e (repeat (- len 1) e))))

(defnrec filter (f l)
  (cond
    (nil? l) nil
    (do
      (def rest (filter f (cdr l)))
      (cond
        (f (car l)) (cons (car l) rest)
        rest))))

(defnrec reduce (f acc l)
  (cond
    (nil? l) acc
    (reduce f (f acc (car l)) (cdr l))))
(def foldl reduce)

(defnrec foldr (f a l)
  (cond
    (nil? l) a
    (f (foldr f a (cdr l)) (car l))))

(def length (reduce (lambda (acc e) (+ 1 acc)) 0))
(def reverse (reduce (lambda (acc x) (cons x acc)) nil))

(defn all (f l)
  (cond
    (nil? l) true
    (f (car l)) (all f (cdr l))
    false))

(defn any (f l)
  (cond
    (nil? l) false
    (f (car l)) true
    (any f (cdr l))))

(defnrec merge (a b)
  (cond
    (nil? a) b
    (nil? b) a
    (< (car a) (car b)) (cons (car a) (merge (cdr a) b))
    (cons (car b) (merge a (cdr b)))))

(defnrec merge-sort (l)
  (cond
    (nil? l) nil
    (nil? (cdr l)) l
    (do
      (def
        half-len (/ (length l) 2)
        lh (take l half-len)
        rh (drop l half-len))
      (merge (merge-sort lh) (merge-sort rh)))))
