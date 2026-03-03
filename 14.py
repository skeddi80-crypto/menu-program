c:\progs>git log
commit 65e46ad9c09b7a3cf29a9d6de33c003ddf2f4b87 (HEAD -> master)
Author: Vitalya <skeddi80@gmail.com>
Date:   Tue Mar 3 16:14:39 2026 +0700

    Initial commit: базовая программа для меню

c:\progs>git checkout -b color
Switched to a new branch 'color'

c:\progs>git status
On branch color
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   14.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        11.py
        111.py
        11123.py
        112.py
        113.py
        114.py
        115.py
        1212.py
        123.py
        13.py
        laba.py
        "\320\221\320\260\321\205\321\202\320\270\320\275_\320\276\321\202\321\207\321\221\321\202.docx"
        "\320\242\320\265\320\272\321\201\321\202\320\276\320\262\321\213\320\271 \320\264\320\276\320\272\321\203\320\274\320\265\320\275\321\202.txt"

no changes added to commit (use "git add" and/or "git commit -a")

c:\progs>git add 14.py

c:\progs>git commit -m "Добавлено поле color"
[color 96f0f23] Добавлено поле color
 1 file changed, 19 insertions(+), 16 deletions(-)

c:\progs>git checkout master
Switched to branch 'master'

c:\progs>git checkout -b menu
Switched to a new branch 'menu'

c:\progs>git add 14.py

c:\progs>git commit -m "Добавлен интерфейс (1-добавить, 2-показать)"
[menu 0dca224] Добавлен интерфейс (1-добавить, 2-показать)
 1 file changed, 48 insertions(+), 29 deletions(-)

c:\progs>git checkout master
Switched to branch 'master'

c:\progs>git merge menu
Updating 65e46ad..0dca224
Fast-forward
 14.py | 77 ++++++++++++++++++++++++++++++++++++++++++-------------------------
 1 file changed, 48 insertions(+), 29 deletions(-)

c:\progs>git merge color
Auto-merging 14.py
CONFLICT (content): Merge conflict in 14.py
Automatic merge failed; fix conflicts and then commit the result.

c:\progs>git add 14.py

c:\progs>c:\progs>git log --oneline --graph --all
"c:\progs" не является внутренней или внешней
командой, исполняемой программой или пакетным файлом.

c:\progs>git log --oneline --graph --all
* 0dca224 (HEAD -> master, menu) Добавлен интерфейс (1-добавить, 2-показать)
| * 96f0f23 (color) Добавлено поле color
|/
* 65e46ad Initial commit: базовая программа для меню

c:\progs>