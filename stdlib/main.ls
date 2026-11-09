; (defn sum0 (n) (cond (= n 0) 0 (+ n (sum0 (- n 1)))))

; (def x 0)
; (defn sum1 (acc n)
;   (cond
;     (= n 0) acc
;     (do
;       (set! x (+ x 1))
;       (sum1 (+ acc n) (- n 1)))))



; (def k 0)
; (while-core (< k 10) (print k) (+= k 1))
; (print k)












; want:
; (do (def while-lambda (lambda () (cond condition (do body (while-lambda)) nil))) (while-lambda))
; (fix (lambda (f) (cond condition (do body (f f)) nil)))

; (defn while-codegen (condition body)
;   (list fix
;       (list lambda '(f)
;         (list cond condition
;           (list do
;             (cond
;               (nil? body) nil
;               (nil? (cdr body)) (car body)
;               (cons do body))
;           '(f f))
;         nil))))
; (defracro while (condition) (eval (while-codegen 'condition 'rest-args)))






; (while-core (< k 10) (print k) (+= k 1))

; (def k 0)
; (while (< k 10000) (print k) (+= k 1))

; (while (< k 5)
;   (print "------")
;   (+= k 1)
;   (def a 0)
;   (while (< a 5)
;     (+= a 1)
;     (print a k)))

(def i 0 sum 0)
(while (< i 5)
  (def j 0)
  (while (< j 5) (+= sum j) (+= j 1))
  (+= i 1))

sum
