; (+ 1 2 3)
; (+ (+ 1 2 3) (+ 1.0 (++ "vas" "ya")) (/ 1 2))
; (+ (+ 1 2 3) (+ 1.0 ; comment
; ; comment
; "vasya part 2") (/ 1 2))
;
; (typeof "petya" "vasya")
;
; (cons 1 (+ 1 2 3))
;
; (cons ())
;
; (car
;   (cdr ; comment
;     (cdr
;       (cons 1
;         (cons 2 () ))))) ; comment 2
;
; (print (quote (1 2 3)) "vasya" 123)
;
; (cond
;   false 1
;   (> 2 1) 2)
;
; (cond
;   false 1
;   (> 2 1) 2
;   3)
;
; (cond
;   (< 3 2 1) (+ 1 "vasya")
;   (+ 1 2) "petya"
;   (+ 2 3) "name 3"
;   ()
; )
;
; (do (print "enter your age")
;   (print (cond
;    (>= (eval (read)) 18) "you are above 18"
;    "you are not above 18"
; )))

(def n (read "Enter num"))
(def orign n)
(def acc 1)
;(def fact '(
;  cond (= n 0) 1
;  (do (set! acc (* acc n)) (set! n (- n 1)) (eval fact))
;))
(def fact '(
  cond (> n 1) (do (set! acc (* acc n)) (set! n (- n 1)) (eval fact))
  1
))

(do (eval fact) (++ orign "! = " acc))
