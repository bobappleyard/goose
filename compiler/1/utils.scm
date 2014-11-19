(define (print . msg)
  (for-each (lambda (m)
              (display m)
              (display " "))
            msg)
  (newline))

(define-syntax match
  (syntax-rules (else)
    ((_ ls ((head . tail) body ...) ... (else e-body ...))
     (let ((tmp ls))
       (case (car tmp)
         ((head) (apply (lambda tail body ...) (cdr tmp))) ...
         (else e-body ...))))
    ((_ ls ((head . tail) body ...) ...)
     (let ((tmp ls))
       (match tmp
         ((head . tail) body ...) ... 
         (else (error "couldn't match" tmp)))))))

(define (fold f i l)
  (if (null? l)
      i
      (fold f (f (car l) i) (cdr l))))

(define (filter f l)
  (reverse (fold (lambda (x acc)
                   (if (f x) 
                       (cons x acc)
                       acc))
                 '()
                 l)))

(define handler 
  (call-with-current-continuation
   (lambda (k)
     (lambda (msg)
       (apply print msg)
       (k #f)))))

(define error
  (lambda msg
    (handler msg)))

(define (with-error-handler f g)
  (call-with-current-continuation
   (lambda (k)
     (let ((old-handler handler))
       (dynamic-wind
        (lambda () (set! handler (lambda (msg) (k (g msg)))))
        f
        (lambda () (set! handler old-handler)))))))

