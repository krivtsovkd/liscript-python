(def fact (lambda (n) (
  cond (= 0 n) 1
  (* n (fact (- n 1)))
)))

(print (fact 5))

(def list (lambda () rest-args))

(def fib (lambda (n) (
  cond (< n 2) n
  (+ (fib (- n 1)) (fib (- n 2)))
)))
