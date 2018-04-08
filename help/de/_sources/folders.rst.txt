Ordnerauswahl
================

Das erste Fenster das Sie sehen, wenn dupeGuru gestartet wird, ist das Ordnerauswahl Fenster. Dieses Fenster enthält die Liste der Ordner die durchsucht werden, wenn Sie **Scan** wählen.

Das Fenster ist leicht zu bedienen. Wollen Sie einen Ordner hinzufügen, klicken Sie auf den **+** Knopf. Haben Sie bereits vorher Ordner hinzugefügt, erscheint ein Popup-Menü mit einer Liste der zuletzt hinzugefügten Ordner. Sie können einen davon auswählen, indem Sie darauf klicken. Wenn Sie auf den ersten Eintrag der Liste klicken, **Neuen Ordner hinzufügen...**, werden Sie nach einem Ordner zum Hinzufügen gefragt. Nutzen Sie dupeGuru zum ersten Mal, erscheint kein Menü und Sie werden direkt nach einem Ordner gefragt. Ein alternativer Weg zum Hinzufügen der Ordner ist, sie auf die Liste zu ziehen.

Um einen Ordner zu entfernen, wählen Sie ihn aus und klicken auf **-**. Wenn Sie einen Unterordner auswählen, wird der ausgewählte Ordner in den **Ausgeschlossen** Zustand versetzt (siehe unten), anstatt entfernt zu werden.

Ordnerzustände
--------------

Jeder Ordner kann in einem von 3 Zuständen sein:

* **Normal:** Duplikate in diesem Ordner können gelöscht werden.
* **Referenz:** Duplikate in diesem Ordner können **nicht** gelöscht werden. Dateien dieses Ordners können sich nur in der **Referenz** Position einer Duplikatgruppe befinden. Ist mehr als eine Datei des Referenzordners in derselben Duplikatgruppe, so wird nur Eine behalten. Die Anderen werden aus der Gruppe entfernt.
* **Ausgeschlossen:** Dateien in diesem Verzeichnis sind nicht im Scan eingeschlossen.

Der Standardzustand eines Ordners ist natürlich **Normal**. Sie können den **Referenz** Zustand für Ordner nutzen, in denen auf keinen Fall eine Datei gelöscht werden soll. 

Wenn sie einen Zustand für ein Verzeichnis setzen, erben alle Unterordner automatisch diesen Zustand, es sei denn Sie ändern den Zustand der Unterordner explizit.

.. todo:: Add iPhoto/Aperture/iTunes libraries notes
