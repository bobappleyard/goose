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

(define error
  (call-with-current-continuation
   (lambda (k)
     (lambda msg
       (apply print msg)
       (k #f)))))

(define (analyze expr e ng)
  (match expr
    ((object . bindings)
     (apply new-type-obj (map (lambda (binding)
                                (cons (car binding) 
                                      (analyze (cdr binding) e ng)))
                              bindings)))
    ((lookup obj member)
     (print obj member)
     (let ((obj-type (analyze obj e ng))
           (member-type (new-type-var)))
       (unify obj-type (new-type-req member member-type))
       member-type))
    ((id name)
     (retrieve name e ng))
    ((if test then else)
     (let ((then-type (analyze then e ng))) 
       (unify (analyze test e ng) bool-type)
       (unify then-type
              (analyze else e ng))
       then-type))
    ((fun bind body)
     (let* ((bind-type (new-type-var))
            (e (cons (cons bind bind-type) e))
            (ng (cons bind-type ng)))
       (new-function-type bind-type (analyze body e ng))))
    ((call fun arg)
     (let ((res-type (new-type-var))
           (fun-type (analyze fun e ng))
           (arg-type (analyze arg e ng)))
       (unify fun-type (new-function-type arg-type res-type))
       res-type))
    ((let decl body)
     (let ((decl-env (analyze-decl decl e ng)))
       (analyze body decl-env ng)))))

(define (analyze-decl decl e ng)
  (match decl
    ((def bind def)
     (cons (cons bind (analyze def e ng)) e))
    ((seq first second)
     (analyze-decl second (analyze-decl first e ng) ng))
    ((rec decl)
     (analyze-rec-decl decl e ng))))

(define (analyze-rec-decl decl e ng)
  (define (bind decl)
    (match decl
      ((def bind def)
       (let* ((var (new-type-var)))
         (set! e (cons (cons bind var) e))
         (set! ng (cons var ng))
         ))
      ((seq first second)
       (bind first)
       (bind second))
      ((rec decl)
       (bind decl))))
  (define (analyze-rec decl)
    (match decl
      ((def bind def)
       (let ((bind-type (retrieve bind e ng))
             (def-type (analyze def e ng)))
         (unify bind-type def-type)))
      ((seq first second)
       (analyze-rec first e ng)
       (analyze-rec second e ng))
      ((rec decl)
       (analyze-rec decl e ng))))
  (bind decl)
  (analyze-rec decl)
  e)

(define (type-error a b)
  (error "type mismatch" a b))

(define (unify a b)
  (let ((a (prune a))
        (b (prune b)))
    (match a
      ((type-var v)
       (if (occurs-in-type? a b)
           (if (eqv? a b)
               a
               (type-error a b))
           (set-car! (cdr a) b)))
      ((type-obj . a-bindings)
       (match b
         ((type-obj . b-bindings)
          (unify-bindings a b #f)
          (unify-bindings b a #f))
         ((type-req . b-bindings)
          (unify-bindings a b #t)
          (unify-bindings b a #f))          
         (else
          (unify b a))))
      ((type-req . a-bindings)
       (match b
         ((type-var v)
          (unify b a))
         ((type-obj . b-bindings)
          (unify b a))
         ((type-req . b-bindings)
          (unify-bindings a b #t)
          (unify-bindings b a #t))
         (else 
          (type-error a b))))
      ((type-op a-name . a-args)
       (match b
         ((type-var v)
          (unify b a))
         ((type-op b-name . b-args)
          (if (and (eqv? a-name b-name)
                   (= (length a-args) (length b-args)))
              (begin
                (for-each unify a-args b-args)
                a)
              (type-error a b)))
         (else
          (type-error a b)))))))

(define (retrieve id e ng)
  (let ((t (assv id e)))
    (if t
        (fresh (cdr t) ng)
        (error "unbound id" id))))

(define (unify-bindings a b add-missing)
  (set-car! b (car a))
  (for-each (lambda (a-binding)
              (let* ((a-name (car a-binding))
                     (a-type (cdr a-binding))
                     (b-binding (assv a-name (cadr b))))
                (if b-binding
                    (let ((b-type (cdr b-binding)))
                      (unify a-type b-type))
                    (if add-missing
                        (set-car! (cdr b) (cons a-binding (cadr b)))
                        (type-error a b)))))
            (cadr a)))

(define (fresh t ng)
  (define e '())
  (define (fresh-var tv)
    (let ((t (assv tv e)))
      (if t
          (cdr t)
          (let ((res (new-type-var)))
            (set! e (cons (cons tv res) e))
            res))))
  (define (fresh-type t)
    (let ((t (prune t)))
      (match t
        ((type-var v)
         (if (memv t ng)
             t
             (fresh-var t)))
        ((type-op name . args)
         (apply new-type-op name (map fresh-type args))))))
  (fresh-type t))

(define (occurs-in-type? a b)
  (let ((b (prune b)))
    (match b
      ((type-var v)
       (eqv? a b))
      ((type-op name . args)
       (let next ((args args))
         (cond
           ((null? args) #f)
           ((occurs-in-type? a (car args)) #t)
           (else (next (cdr args))))))
      (else #f))))

(define (new-type-var)
  (list 'type-var #f))

(define (new-type-op name . args)
  (append (list 'type-op name) args))

(define (new-type-obj . bindings)
  (list 'type-obj bindings))

(define (new-type-req name type)
  (list 'type-req (list (cons name type))))

(define (new-function-type input output)
  (new-type-op 'fun input output))

(define (prune t)
  (case (car t)
    ((type-var)
     (if (cadr t)
         (begin
           (set-car! (cdr t) (prune (cadr t)))
           (cadr t))
         t))
    (else
     t)))

(define bool-type (new-type-op 'bool))
(define int-type (new-type-op 'int))

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
      (call (fun x (lookup (id x) b)) (object (a . (id 0))))
      ))
  (let ((env `((true . ,bool-type) 
               (false . ,bool-type) 
               (0 . ,int-type)
               (succ . ,(new-type-op 'fun int-type int-type))
               (pred . ,(new-type-op 'fun int-type int-type))
               (zero? . ,(new-type-op 'fun int-type bool-type)))))
    (for-each (lambda (prog)
                (print prog "::" (analyze prog env '())))
              progs)))

