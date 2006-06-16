;; Copyright (C) 2006 Free Software Foundation, Inc.
;; This file is (not yet) part of GNU Emacs.

;; GNU Emacs is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation; either version 2, or (at your option)
;; any later version.

;; GNU Emacs is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with GNU Emacs; see the file COPYING.  If not, write to the
;; Free Software Foundation, Inc., 59 Temple Place - Suite 330,
;; Boston, MA 02111-1307, USA.
;; ======================================================================
;; pydb (Python extended debugger) functions

(require 'gud)

(defvar gud-pydb-history nil
  "History of argument lists passed to pydb.")

(defconst gud-pydb-marker-regexp
  "^(\\([-a-zA-Z0-9_/.]*\\):\\([0-9]+\\)):[ \t]?"
  "Regular expression used to find a file location given by pydb.

The debugger outputs program-location lines that look like this:
   (/usr/bin/zonetab2pot.py:15): makePOT")

(defconst gud-pydb-marker-regexp-file-group 1
  "Group position in gud-pydb-marker-regexp that matches the file name.")

(defconst gud-pydb-marker-regexp-line-group 2
  "Group position in gud-pydb-marker-regexp that matches the line number.")

(defun gud-pydb-massage-args (file args)
  args)

;; There's no guarantee that Emacs will hand the filter the entire
;; marker at once; it could be broken up across several strings.  We
;; might even receive a big chunk with several markers in it.  If we
;; receive a chunk of text which looks like it might contain the
;; beginning of a marker, we save it here between calls to the
;; filter.
(defun gud-pydb-marker-filter (string)
  (setq gud-marker-acc (concat gud-marker-acc string))
  (let ((output ""))

    ;; Process all the complete markers in this chunk.
    ;; Format of line looks like this:
    ;;   (/etc/init.d/ntp.init:16):
    ;; but we also allow DOS drive letters
    ;;   (d:/etc/init.d/ntp.init:16):
    (while (string-match gud-pydb-marker-regexp gud-marker-acc)
      (setq

       ;; Extract the frame position from the marker.
       gud-last-frame
       (cons (substring gud-marker-acc 
			(match-beginning gud-pydb-marker-regexp-file-group) 
			(match-end gud-pydb-marker-regexp-file-group))
	     (string-to-int 
	      (substring gud-marker-acc
			 (match-beginning gud-pydb-marker-regexp-line-group)
			 (match-end gud-pydb-marker-regexp-line-group))))

       ;; Append any text before the marker to the output we're going
       ;; to return - we don't include the marker in this text.
       output (concat output
		      (substring gud-marker-acc 0 (match-beginning 0)))

       ;; Set the accumulator to the remaining text.
       gud-marker-acc (substring gud-marker-acc (match-end 0))))

    ;; Does the remaining text look like it might end with the
    ;; beginning of another marker?  If it does, then keep it in
    ;; gud-marker-acc until we receive the rest of it.  Since we
    ;; know the full marker regexp above failed, it's pretty simple to
    ;; test for marker starts.
    (if (string-match "\032.*\\'" gud-marker-acc)
	(progn
	  ;; Everything before the potential marker start can be output.
	  (setq output (concat output (substring gud-marker-acc
						 0 (match-beginning 0))))

	  ;; Everything after, we save, to combine with later input.
	  (setq gud-marker-acc
		(substring gud-marker-acc (match-beginning 0))))

      (setq output (concat output gud-marker-acc)
	    gud-marker-acc ""))

    output))

(defun gud-pydb-find-file (f)
  (find-file-noselect f))

(defcustom gud-pydb-command-name "pydb"
  "File name for executing the Python debugger.
This should be an executable on your path, or an absolute file name."
  :type 'string
  :group 'gud)

;;;###autoload
(defun pydb (command-line)
  "Run pydb on program FILE in buffer `*gud-FILE*'.
The directory containing FILE becomes the initial working directory
and source-file directory for your debugger."
  (interactive
   (list (gud-query-cmdline 'pydb)))

  (gud-common-init command-line 'gud-pydb-massage-args
		   'gud-pydb-marker-filter 'gud-pydb-find-file)
  (set (make-local-variable 'gud-minor-mode) 'pydb)

  (gud-def gud-args   "info args" "a"
	   "Show arguments of current stack.")
  (gud-def gud-break  "break %f:%l""\C-b"
	   "Set breakpoint at current line.")
  (gud-def gud-cont   "continue"   "\C-r" 
	   "Continue with display.")
  (gud-def gud-down   "down %p"     ">"
	   "Down N stack frames (numeric arg).")
  (gud-def gud-finish "finish"      "f\C-f"
	   "Finish executing current function.")
  (gud-def gud-next   "next %p"     "\C-n"
	   "Step one line (skip functions).")
  (gud-def gud-print  "p %e"        "\C-p"
	   "Evaluate bash expression at point.")
  (gud-def gud-remove "clear %f:%l" "\C-d"
	   "Remove breakpoint at current line")
  (gud-def gud-run    "run"       "R"
	   "Restart the Python script.")
  (gud-def gud-statement "eval %e" "\C-e"
	   "Execute Python statement at point.")
  (gud-def gud-step   "step %p"       "\C-s"
	   "Step one source line with display.")
  (gud-def gud-tbreak "tbreak %f:%l"  "\C-t"
	   "Set temporary breakpoint at current line.")
  (gud-def gud-up     "up %p"
	   "<" "Up N stack frames (numeric arg).")
  (gud-def gud-where   "where"
	   "T" "Show stack trace.")
  (local-set-key "\C-i" 'gud-gdb-complete-command)
  (setq comint-prompt-regexp "^(+Pydb)+ *")
  (setq paragraph-start comint-prompt-regexp)

  ;; Update GUD menu bar
  (define-key gud-menu-map [args]      '("Show arguments of current stack" . 
					 gud-args))
  (define-key gud-menu-map [down]      '("Down Stack" . gud-down))
  (define-key gud-menu-map [eval]      '("Execute Python statement at point" 
					 . gud-statement))
  (define-key gud-menu-map [finish]    '("Finish Function" . gud-finish))
  (define-key gud-menu-map [run]       '("Restart the Python Script" . 
					 gud-run))
  (define-key gud-menu-map [stepi]     'undefined)
  (define-key gud-menu-map [tbreak]    '("Temporary break" . gud-tbreak))
  (define-key gud-menu-map [up]        '("Up Stack" . gud-up))
  (define-key gud-menu-map [where]     '("Show stack trace" . gud-where))

  (local-set-key [menu-bar debug finish] '("Finish Function" . gud-finish))
  (local-set-key [menu-bar debug up] '("Up Stack" . gud-up))
  (local-set-key [menu-bar debug down] '("Down Stack" . gud-down))

  (setq comint-prompt-regexp "^(+Pydb)+ *")
  (setq paragraph-start comint-prompt-regexp)

  (run-hooks 'pydb-mode-hook))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; pydbtrack --- tracking pydb debugger in an Emacs shell window
;;; Modified from  python-mode in particular the part:
;; pdbtrack support contributed by Ken Manheimer, April 2001.

;;; Code:

(require 'comint)
(require 'custom)
(require 'cl)
(require 'compile)
(require 'shell)

(defgroup pydbtrack nil
  "Pydb file tracking by watching the prompt."
  :prefix "pydb-pydbtrack-"
  :group 'shell)


;; user definable variables
;; vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

(defcustom pydb-pydbtrack-do-tracking-p t
  "*Controls whether the pydbtrack feature is enabled or not.
When non-nil, pydbtrack is enabled in all comint-based buffers,
e.g. shell buffers and the *Python* buffer.  When using pydb to debug a
Python program, pydbtrack notices the pydb prompt and displays the
source file and line that the program is stopped at, much the same way
as gud-mode does for debugging C programs with gdb."
  :type 'boolean
  :group 'pydb)
(make-variable-buffer-local 'pydb-pydbtrack-do-tracking-p)

(defcustom pydb-pydbtrack-minor-mode-string " PYDB"
  "*String to use in the minor mode list when pydbtrack is enabled."
  :type 'string
  :group 'pydb)

(defcustom pydb-temp-directory
  (let ((ok '(lambda (x)
	       (and x
		    (setq x (expand-file-name x)) ; always true
		    (file-directory-p x)
		    (file-writable-p x)
		    x))))
    (or (funcall ok (getenv "TMPDIR"))
	(funcall ok "/usr/tmp")
	(funcall ok "/tmp")
	(funcall ok "/var/tmp")
	(funcall ok  ".")
	(error
	 "Couldn't find a usable temp directory -- set `pydb-temp-directory'")))
  "*Directory used for temporary files created by a *Python* process.
By default, the first directory from this list that exists and that you
can write into: the value (if any) of the environment variable TMPDIR,
/usr/tmp, /tmp, /var/tmp, or the current directory."
  :type 'string
  :group 'pydb)


;; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
;; NO USER DEFINABLE VARIABLES BEYOND THIS POINT

;; have to bind pydb-file-queue before installing the kill-emacs-hook
(defvar pydb-file-queue nil
  "Queue of Makefile temp files awaiting execution.
Currently-active file is at the head of the list.")

(defvar pydb-pydbtrack-is-tracking-p t)


;; Constants

(defconst pydb-position-re 
  "\\(^\\|\n\\)(\\([^:]+\\):\\([0-9]*\\)).*\n"
  "Regular expression for a pydb position")

(defconst pydb-marker-regexp-file-group 2
  "Group position in pydb-postiion-re that matches the file name.")

(defconst pydb-marker-regexp-line-group 3
  "Group position in pydb-position-re that matches the line number.")



(defconst pydb-traceback-line-re
  "^#[0-9]+[ \t]+\\((\\([a-zA-Z-.]+\\) at (\\(\\([a-zA-Z]:\\)?[^:\n]*\\):\\([0-9]*\\)).*\n"
  "Regular expression that describes tracebacks.")

;; pydbtrack contants
(defconst pydb-pydbtrack-stack-entry-regexp
      "^(\\([-a-zA-Z0-9_/.]*\\):\\([0-9]+\\)):[ \t]?\\(.*\n\\)"
  "Regular expression pydbtrack uses to find a stack trace entry.")

(defconst pydb-pydbtrack-input-prompt "\n(+Pydb)+ *"
  "Regular expression pydbtrack uses to recognize a pydb prompt.")

(defconst pydb-pydbtrack-track-range 10000
  "Max number of characters from end of buffer to search for stack entry.")


;; Utilities
(defmacro pydb-safe (&rest body)
  "Safely execute BODY, return nil if an error occurred."
  (` (condition-case nil
	 (progn (,@ body))
       (error nil))))


;;;###autoload

(defun pydb-pydbtrack-overlay-arrow (activation)
  "Activate or de arrow at beginning-of-line in current buffer."
  ;; This was derived/simplified from edebug-overlay-arrow
  (cond (activation
	 (setq overlay-arrow-position (make-marker))
	 (setq pos (point))
	 (setq overlay-arrow-string "=>")
	 (set-marker overlay-arrow-position (point) (current-buffer))
	 (setq pydb-pydbtrack-is-tracking-p t))
	(pydb-pydbtrack-is-tracking-p
	 (setq overlay-arrow-position nil)
	 (setq pydb-pydbtrack-tracking-p nil))
	))

(defun pydb-pydbtrack-track-stack-file (text)
  "Show the file indicated by the pydb stack entry line, in a separate window.
Activity is disabled if the buffer-local variable
`pydb-pydbtrack-do-tracking-p' is nil.

We depend on the pydb input prompt matching `pydb-pydbtrack-input-prompt'
at the beginning of the line.
" 
  ;; Instead of trying to piece things together from partial text
  ;; (which can be almost useless depending on Emacs version), we
  ;; monitor to the point where we have the next pydb prompt, and then
  ;; check all text from comint-last-input-end to process-mark.
  ;;
  ;; Also, we're very conservative about clearing the overlay arrow,
  ;; to minimize residue.  This means, for instance, that executing
  ;; other pydb commands wipe out the highlight.  You can always do a
  ;; 'where' (aka 'w') command to reveal the overlay arrow.
  (let* ((origbuf (current-buffer))
	 (currproc (get-buffer-process origbuf)))

    (if (not (and currproc pydb-pydbtrack-do-tracking-p))
        (pydb-pydbtrack-overlay-arrow nil)

      (let* ((procmark (process-mark currproc))
             (block (buffer-substring (max comint-last-input-end
                                           (- procmark
                                              pydb-pydbtrack-track-range))
                                      procmark))
             target target_fname target_lineno)

        (if (not (string-match (concat pydb-pydbtrack-input-prompt "$") block))
            (pydb-pydbtrack-overlay-arrow nil)

          (setq target (pydb-pydbtrack-get-source-buffer block))

          (if (stringp target)
              (message "pydbtrack: %s" target)

            (setq target_lineno (car target))
            (setq target_buffer (cadr target))
            (setq target_fname (buffer-file-name target_buffer))
            (switch-to-buffer-other-window target_buffer)
            (goto-line target_lineno)
            (message "pydbtrack: line %s, file %s" target_lineno target_fname)
            (pydb-pydbtrack-overlay-arrow t)
            (pop-to-buffer origbuf t)

            )))))
  )

(defun pydb-pydbtrack-get-source-buffer (block)
  "Return line number and buffer of code indicated by block's traceback text.

We look first to visit the file indicated in the trace.

Failing that, we look for the most recently visited python-mode buffer
with the same name or having 
having the named function.

If we're unable find the source code we return a string describing the
problem as best as we can determine."

  (if (not (string-match pydb-position-re block))

      "line number cue not found"

    (let* ((filename (match-string pydb-marker-regexp-file-group block))
           (lineno (string-to-int 
		    (match-string pydb-marker-regexp-line-group block)))
           funcbuffer)

      (cond ((file-exists-p filename)
             (list lineno (find-file-noselect filename)))

            ((= (elt filename 0) ?\<)
             (format "(Non-file source: '%s')" filename))

            (t (format "Not found: %s" filename)))
      )
    )
  )


;;; Subprocess commands



;; pydbtrack functions
(defun pydb-pydbtrack-toggle-stack-tracking (arg)
  (interactive "P")
  (if (not (get-buffer-process (current-buffer)))
      (error "No process associated with buffer '%s'" (current-buffer)))
  ;; missing or 0 is toggle, >0 turn on, <0 turn off
  (if (or (not arg)
	  (zerop (setq arg (prefix-numeric-value arg))))
      (setq pydb-pydbtrack-do-tracking-p (not pydb-pydbtrack-do-tracking-p))
    (setq pydb-pydbtrack-do-tracking-p (> arg 0)))
  (message "%sabled pydb's pydbtrack"
           (if pydb-pydbtrack-do-tracking-p "En" "Dis")))

(defun turn-on-pydbtrack ()
  (interactive)
  (pydb-pydbtrack-toggle-stack-tracking 1)
  (setq pydb-pydbtrack-is-tracking-p t)
  (add-hook 'comint-output-filter-functions 'pydb-pydbtrack-track-stack-file))
  ; remove other py-pdbtrack if which gets in the way
  (remove-hook 'comint-output-filter-functions 'py-pdbtrack-track-stack-file))


(defun turn-off-pydbtrack ()
  (interactive)
  (pydb-pydbtrack-toggle-stack-tracking 0)
  (setq pydb-pydbtrack-is-tracking-p nil)
  (remove-hook 'comint-output-filter-functions 
	       'pydb-pydbtrack-track-stack-file) )

;; Add a designator to the minor mode strings if we are tracking
(or (assq 'pydb-pydbtrack-minor-mode-string minor-mode-alist)
    (push '(pydb-pydbtrack-is-tracking-p
	    pydb-pydbtrack-minor-mode-string)
	  minor-mode-alist)) 
;; pydbtrack


