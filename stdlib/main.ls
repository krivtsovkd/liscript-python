; (defn fact-l (n)
;   (cond
;     (<= n 1) n
;     (* n (fact-l (- n 1)))))

; (defmacro fact-m (n)
;   (cond
;     (<= n 1) n
;     (* n (fact-m (- n 1)))))

; (def a 10)

; (print (fact-l a) (fact-m a))

; (defn inc-l (n) (+ n 1))
; (defmacro inc-m (n) (+ n 1))
