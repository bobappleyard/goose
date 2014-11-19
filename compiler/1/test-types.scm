(load "utils.scm")
(load "types.scm")

(define (test)
  (define progs 
    '(
      (id 0)
      (if (id true) (id 0) (id 0))
      (fun x (id x))
      (call (fun x (id x)) (id 0))
      (let (def identity (fun x (id x)))
        (call (id identity) (id 0)))
      (let (rec (def add (fun a (fun b (if (call (id zero?) (id a)) 
                                           (id b)
                                           (call (call (id add) (call (id pred) (id a))) (call (id succ) (id b))))))))
        (id add))
      (object (a . (id 0)))
      (fun x (lookup (id x) a))
      (lookup (object (a . (id 0))) a)
      (lookup (object (a . (id 0))) b)
      (call (fun x (call (lookup (id x) b) (lookup (id x) a))) (object (a . (id 0)) (b . (fun x (id x)))))
      (let (def test (object (a . (fun x (id x))))) (if (call (lookup (id test) a) (id true))
                                                        (call (lookup (id test) a) (id 0))
                                                        (call (lookup (id test) a) (id 0))))
      (fun x (let (seq (def y (id x)) (seq (def a (call (id y) (id 0))) (def a (call (id y) (id false))))) (id y)))
      (call (fun test (if (call (lookup (id test) a) (id true))
                          (call (lookup (id test) a) (id 0))
                          (call (lookup (id test) a) (id 0)))) (object (a . (fun x (id x)))))
      (fun x (let (seq (def y (id x)) (seq (def a (lookup (id y) a)) (def b (lookup (id y) b)))) (id y)))
      (let (def get-c (fun x (lookup (id x) c)))
        (fun x
             (begin
               (call (id get-c) (id x))
               (lookup (id x) a)
               (lookup (id x) b)
               (id get-c))))
      ))
  (let ((env `((true . ,bool-type) 
               (false . ,bool-type) 
               (0 . ,int-type)
               (nil . ,null-type)
               (succ . ,(new-type-op 'fun int-type int-type))
               (pred . ,(new-type-op 'fun int-type int-type))
               (zero? . ,(new-type-op 'fun int-type bool-type)))))
    (for-each (lambda (prog)
                (with-error-handler 
                 (lambda () (print prog "::" (analyze prog env '())))
                 (lambda (msg) (apply print prog "failed with message:" msg))))
              progs)))

