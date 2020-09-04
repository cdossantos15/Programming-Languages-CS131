#lang racket

;TODO: lambda change, map the varibles
; FIX THIS TEST CASE: (expr-compare ''((blah (a) a) c) ''((lambda (b) b) d))


(define lam_sym (string->symbol "\u03BB"))

(define keywords '(if lambda lam_sym quote))

(define (is-lambda x) (or (equal? x 'lambda)(equal? x lam_sym)))

(define (expr-compare x y)
  (cond
    ;if the two items are equal:
    ((equal? x y) x)
    
    ;if the two items are bools
    ((and (boolean? x) (boolean? y) )
    (if x '% '(not %)))
    ;if x and y are both lambda types,
    ;Then return lam_sym
    ((or (equal? x lam_sym)(equal? y lam_sym)) lam_sym)

    ;if x and y start with a type of lambda
    ;check that they are both lists
    ;check that they are the same length
    ((and (list? x) (list? y) (is-lambda (car x)) (is-lambda (car y))
          (or
           (and
            (list? (car (cdr x)))
            (list? (car (cdr y)))
            (not (equal? (length (car (cdr x))) (length (car (cdr y))))))
          (and
           (or (list? (car (cdr x))) (list? (car (cdr y))))
           (or (not (list? (car (cdr x)))) (not (list? (car (cdr y))))
          )))
      )
      ;THEN
      (list 'if '% x y)
      )
    
    (;IF:  
     (or
      ;they are both lists
       (not (and (list? x) (list? y)))
      ;OR they are of equal lengths
       (not (equal? (length x) (length y)))
       ;OR they are quoted
       (and (equal? 'quote (car x)) (equal? 'quote (car y)))
      ;OR both keywords are the same (or the lambda case))
       (and
        ;Have to be not equal
        (and
            (not(equal? (car x) (car y)))
            (not (and (equal? (car x) lam_sym) (equal? (car y) 'lambda)))
            (not (and (equal? (car x) 'lambda) (equal? (car y) lam_sym)))

        ;one has to be keywords
        (or (member (car y) keywords) (member (car x) keywords))
       )))
     ;THEN
       (list 'if '% x y)
      )
     
  
    (else (cons (expr-compare (car x) (car y)) (expr-compare (cdr x) (cdr y))) )
   )
  )


;test call: (test-expr-compare test-expr-x test-expr-y)

(define (test-expr-compare x y)
  (and (equal? (eval x) (eval (list 'let '((% #t)) (expr-compare x y))))
       (equal? (eval y) (eval (list 'let '((% #f)) (expr-compare x y))))
))

(define test-expr-x (list 5 11 #t #f #t #f 'a '(a b c) '(quote (5 6)) '(cons c d) '(cons (cons a y) (cons b c))
                          '(cons a b) '(list) '(quote (a b)) '(quoth (a b)) '(if x y z) '(1 2 3)
                          '(lambda (c d) (+ c d) '(+ a b)
                          )))

(define test-expr-y (list 5 12 #t #f #f #t 'a '(a b c) '(quote (7 8)) '(cons c b) '(cons (cons a x) (cons a c))
                          '(list a b) '(list a) '(quote (a c)) '(quoth (a c)) '(if x z z) '(4 5 6)
                          '(lambda (c d) (- c d)) '(+ b c) 
                          ))
