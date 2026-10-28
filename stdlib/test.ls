(defn test (expected test-val) (cond (= expected test-val) nil (error (++ "Test failed: " expected " != " test-val))))

(def fib (fix (lambda (self n)
  (cond
    (<= n 1) n
    (+ (self self (- n 1)) (self self (- n 2)))))))

(test 1.5 (+ 1 0.5))
(test 1 (/ 3 2))
(test 1.5 (/ 3 2.0))
(test 1.5 (/ 3.0 2))
(test 1.0 (- 1 0.0))

(test true (not false))
(test false (not true))

(test 2 (inc 1))

(test '(1 2 3) (range 1 3))
(test '(7 8 9 10) (range 7 10))
(test nil (range 100 1))

(test '(1 2) (take 2 (range 1 10)))
(test nil (take 1 nil))
(test '("vasya" "petya" 1) (take 3 '("vasya" "petya" 1 2 3)))
(test (range 5 9) (take 100 (range 5 9)))

(test '(3 4 5) (drop 2 (range 1 5)))
(test nil (drop 1 nil))
(test nil (drop 100 (range 1 10)))

(test 3 (n-times 3 inc 0))

; cant test that it errors in bad cases 💥
(test 1 (list-ref 1 (range 0 5)))

(test '(2 3 4) (map (lambda (n) (+ n 1)) (range 1 3)))
(test '(1 1 2 3 5 8 13 21 34 55) (map fib (range 1 10)))
(test '(true false true) (map not '(false true false)))

; (test true (contains? 4 (range 1 10)))
; (test false (contains? 10 (range 100 200)))
; (test false (contains? "vasya" nil))
; (test true (contains? "vasya" '("vasya" "petya" "vatya" "petya")))

; (test '(1 2 3) (init 3 (lambda (n) (+ n 1))))
; (test nil (init 0 (lambda (n) n)))
; (test '(0 1 1 2 3 5 8 13 21 34) (init 10 fib))

(test nil (intersperse 0 nil))
(test '(1) (intersperse 0 '(1)))
(test '(1 0 2 0 3) (intersperse 0 (range 1 3)))

(test '(1 1 1) (repeat 3 1))
(test nil (repeat 0 0))

(test '(2 4) (filter (lambda (n) (= 0 (% n 2))) (range 1 5)))
(test nil (filter (lambda (n) (< n 0)) (range 100 200)))
(test '("vasya" "vasya") (filter (lambda (s) (= "vasya" s)) '("vasya" "petya" "petya" "vasya")))

(test 55 (reduce + 0 (range 1 10)))
(test 0 (reduce * 0 nil))
; warning: will break if and is replaced with a macro
(test true (reduce and true
  (map (lambda (n) (= 0 (% n 2))) (map (lambda (n) (* n 2)) (range 1 10)))))

(test "petyavasya" (foldr ++ "" '("vasya" "petya")))

(test '(3 2 1) (reverse (range 1 3)))
(test nil (reverse nil))

(test 0 (length nil))
(test 3 (length (range 1 3)))
(test 2 (length (list "vasya" "petya")))

(test '(1 2 3) (append nil '(1 2 3)))
(test '(1 2 3) (append '(1 2 3) nil))
(test '(1 2 3 4 5 6) (append '(1 2 3) '(4 5 6)))

(test true (all (lambda (a) false) nil))
(test true (all (lambda (n) (= 0 (% n 2))) '(2 4 6)))
(test false (all (lambda (n) (= 0 (% n 2))) (range 1 5)))

(test false (any (lambda (a) true) nil))
(test false (any (lambda (n) (= 0 (% n 2))) '(1 3 5)))
(test true (any (lambda (n) (= 0 (% n 2))) (range 1 5)))

(test '(2 3 (4 5 6) 7) (deep-map inc '(1 2 (3 4 5) 6)))

; begin pattern matching tests

(def v '(1 "vasya" 3 (5 true 6) "petya" 8))

; failing matches
(test false (pm (_) v))
(test false (pm (2 _ _ _ _ _) v))
(test false (pm (_ _ _ (5 false 6) "petya" _) v))
(test false (pm (a b _ _ "vasya" c) v))
(test false (pm (2 & _) v))

; succeeding matches
(test true (pm (1 "vasya" 3 (5 true 6) "petya" 8) v))
(test true (pm (_ "vasya" 3 (5 _ 6) _ _) v))
(test true (pm (_ "vasya" 3 _ "petya" _) v))
(test true (pm (_ "vasya" 3 (5 & _) & _) v))

; succeeding matches with destructuring
(test true
  (do
    (pm (a b _ d _ 8) v)
    (and (= a 1) (= b "vasya") (= d '(5 true 6)))))

(test true
  (do
    (pm (x & xs) v)
    (and (= x (car v)) (= xs (cdr v)))))

(test true
  (do
    (pm (1 a 3 (b & c) "petya" d & e) v)
    (and (= a "vasya") (= b 5) (= c '(true 6)) (= d 8) (= e nil))))

; end pattern matching tests

"Tests finished"
