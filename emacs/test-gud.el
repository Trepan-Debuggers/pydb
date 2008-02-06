;; -*- emacs-lisp -*-
;; This program has to be run from the directory it is currently in and
;; the pydb code has to be in the parent directory
(load-file "./elk-test.el")

(setq load-path (cons "." load-path))
(require 'pydb)
(setq load-path (cdr load-path))

(defun y-or-n-p (prompt)
  "Replacement of y-or-n-p() for pydb testing"
  (assert-nil "y-or-n-p should not have been called"))

(defun error (msg)
  "Replacement error() for pydb testing"
  (assert-nil "error should not have been called"))

;; -------------------------------------------------------------------

(deftest "test-pydb-find-file"
  ;; Set to cause a warning in find-file-no-select and 
  ;; check that it is ignored.
  (let ((large-file-warning-threshold 1)) 
    (gud-pydb-find-file "elk-test.el")))


;; -------------------------------------------------------------------
;; Build and run the test suite.
;;

(build-suite "pydb-gud-suite"
	     "test-pydb-find-file")

(run-elk-test "pydb-gud-suite"
              "test some pydb-gud code")
