;; Emacs init file: Sunit Joshi

;; Start the server
(require 'server)
(unless (server-running-p)
  (server-start))

;; UI Improvements
(setq inhibit-startup-screen t)  ; Disable splash screen
(when (fboundp 'menu-bar-mode) (menu-bar-mode -1))
(when (fboundp 'tool-bar-mode) (tool-bar-mode -1))
(when (fboundp 'scroll-bar-mode) (scroll-bar-mode -1))
(desktop-save-mode 1)
(xterm-mouse-mode 1)
(fido-vertical-mode t)
(electric-pair-mode 1)

(setq backup-directory-alist '(("." . "~/.emacs.d/backups")))
(setq desktop-path '("~/.emacs.d/backups"))
(desktop-save-mode 1)


;; Initialize packages (for Emacs 27+)
(require 'package)
(add-to-list 'package-archives '("melpa" . "https://melpa.org") t)
(package-initialize)

(use-package markdown-mode :ensure t)

(add-hook 'text-mode-hook #'visual-line-mode)                                                                             
(add-hook 'markdown-mode-hook #'visual-line-mode)

(load-theme 'dracula t)

;; Highlight color
(custom-set-faces                                                                                                         
 '(region ((t (:background "#44475a" :extend t)))))


;; Useful commands
;; CtrX-u: Undo, Alt-W: Copies marked txt
;; Ctr-X-Backspace: Backward kill sentence
;; CtrX-CtrW: File save as
;; Alt-Space: Deletes all spaces & tab around the cursorOB
;; Ctr-X o : Move to other buffer

;;Set backup folder
(setq backup-directory-alist '(("." . "~/.emacs.d/backups/")))
(setq auto-save-file-name-transforms
      `((".*" "~/.emacs.d/backups/" t)))

(defun move-line-up ()
  "Move the current line up."
  (interactive)
  (transpose-lines 1)
  (forward-line -2))

(defun move-line-down ()
  "Move the current line down."
  (interactive)
  (forward-line 1)
  (transpose-lines 1)
  (forward-line -1))

(global-set-key (kbd "M-<up>") 'move-line-up)
(global-set-key (kbd "M-<down>") 'move-line-down)
(global-set-key (kbd "M-w") 'kill-ring-save)

;; macOS terminals may send Option-W as this character instead of Meta-w.
(global-set-key (kbd "∑") 'kill-ring-save)
(global-set-key (kbd "C-c q") 'kill-emacs)
(global-set-key (kbd "<wheel-up>") 'scroll-down-line)
(global-set-key (kbd "<wheel-down>") 'scroll-up-line)

(when (eq system-type 'darwin)
  (setq interprogram-cut-function
        (lambda (text)
          (with-temp-buffer
            (insert text)
            (call-process-region (point-min) (point-max) "pbcopy"))))
  (setq interprogram-paste-function
        (lambda ()
          (let ((text (shell-command-to-string "pbpaste")))
            (when (> (length text) 0) text)))))

(global-set-key (kbd "C-_") 'undo)

(global-display-line-numbers-mode)

;; select current line
(defun select-current-line ()                                                                         
  "Select the entire current line."                                                                                       
  (interactive)
  (beginning-of-line)                                                                                                     
  (push-mark (line-end-position) t t))                                                                

(global-set-key (kbd "C-c l") 'select-current-line)


;; Comment region
(global-set-key (kbd "C-c ;") 'comment-or-uncomment-region)


;; format current buffer
(defun format-current-buffer ()                                                                                           
  "Re-indent the entire buffer."                                                                      
  (interactive)                                                                                                           
  (indent-region (point-min) (point-max)))

(global-set-key (kbd "C-c f") 'format-current-buffer)

;;format file hook
(add-hook 'emacs-lisp-mode-hook
	  (lambda ()
	    (add-hook 'before-save-hook 'indent-region-or-buffer nil t)))


(defun indent-region-or-buffer ()            
  "Indent the entire buffer."
  (indent-region (point-min) (point-max)))


;; Auto-revert buffers when files change on disk
(global-auto-revert-mode 1)
(setq global-auto-revert-non-file-buffers t)
(setq auto-revert-verbose nil)

;; Save on frame close and server kill                                                                                    
(unless noninteractive
  (add-hook 'kill-emacs-hook #'desktop-save-in-desktop-dir)
  (add-hook 'delete-frame-functions (lambda (_) (desktop-save-in-desktop-dir))))

;; Switch to last real buffer when emacsclient connects
(add-hook 'server-after-make-frame-hook                                                                                   
          (lambda ()                                                                                                      
            (let ((buf (cl-find-if (lambda (b)
                                     (not (string-prefix-p "*" (buffer-name b))))                                         
                                   (buffer-list))))                                                   
              (when buf (switch-to-buffer buf)))))
