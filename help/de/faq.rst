Häufig gestellte Fragen
==========================

.. topic:: What is |appname|?

    .. only:: edition_se

        DupeGuru ist ein Tool zum Auffinden von Duplikaten auf Ihrem Computer. Es kann entweder Dateinamen oder Inhalte scannen. Der Dateiname-Scan stellt einen lockeren Suchalgorithmus zur Verfügung, der sogar Duplikate findet, die nicht den exakten selben Namen haben.

    .. only:: edition_me

        dupeGuru Music Edition ist ein Tool zum Auffinden von Duplikaten in Ihrer Musiksammlung. Es kann seine Suche auf Dateinamen, Tags oder Inhalte basieren. Der Dateiname-Scan und Tag-Scan stellt einen lockeren Suchalgorithmus zur Verfügung, der sogar Dateinamen und Tags findet, die nicht den exakt selben Namen haben.

    .. only:: edition_pe

        dupeGuru Picture Edition (kurz PE) ist ein Tool zum Auffinden von doppelten Bildern auf Ihrem Computer. Es findet nicht nur exakte Übereinstimmungen, sondern auch Duplikate unterschiedlichen Dateityps (PNG, JPG, GIF etc..) und Qualität.

.. topic:: Was macht es besser ala andere Duplikatscanner?

    Die Scan-Engine ist extrem flexibel. Sie können sie modifizieren, um die Art von Ergebnissen zu bekommen die Sie möchten. Sie können mehr über die dupeGuru Modifikationen finden auf der :doc:`Einstellungen Seite <preferences>`.

.. topic:: Wie sicher ist dupeGuru?

    Sehr sicher. DupeGuru wurde entwickelt, um sicherzustellen keine Dateien zu löschen, die nicht gelöscht werden sollen. Erstens, es existiert ein Referenzordnersystem welches Ordner definiert, die auf **keinen** Fall angefasst werden sollen. Dann gibt es noch das Referenzgruppensystem, das sicherstellt das **immer** ein Mitglied einer Duplikatgruppe behalten wird.

.. topic:: Was sind die Demo-Einschränkungen von dupeGuru?

    Keine, |appname| ist `Fairware <http://open.hardcoded.net/about/>`_.

.. topic:: Die Markierungsbox einer Datei, die ich löschen möchte, ist deaktiviert. Was muss ich tun?

    Sie können die Referenz nicht markieren (die erste Datei einer Duplikatgruppe). Wie auch immer, Sie können ein Duplikat zur Referenz befördnern. Wenn eine Datei, die Sie markieren möchten, eine Referenz ist, muss ein Duplikat der Gruppe zur Referenz gemacht werden, indem man es auswählt und auf **Aktionen-->Mache Ausgewählte zur Referenz** gehen. Befindet sich die Referenzdatei in einem Referenzordner (Dateiname in blauen Buchstaben), kann sie nicht aus der Referenzposition entfernt werden.

.. topic:: ich habe einen Ordner aus dem ich wirklich nichts löschen möchte.

    Möchten Sie sicherstellen, das dupeGuru niemals Dateien aus einem bestimmten Ordner löscht, dann versetzen sie den Ordner in den **Referenzzustand**. Siehe :doc:`folders`.

.. topic:: Was bedeutet diese '(X verworfen)' Nachricht in der Statusbar?

    In einigen Fällen werden manche Treffer aus Sicherheitsgründen nicht in den Ergebnissen angezeigt. Lassen Sie mich ein Beispiel konstruieren. Wir haben 3 Datein: A, B und C. Wir scannen sie mit einer niedrigen Filterempfindlichkeit. Der Scanner findet heraus das A mit B und C übereinstimmt, aber B **nicht** mit C übereinstimmt. Hier hat dupeGuru ein Problem. Es kann keine Duplikatgruppe erstellen mit A, B und C, weil nicht alle Dateien der Gruppe zusammenpassen. Es könnte 2 Gruppen erstellen: eine A-B Gruppe und eine A-C Gruppe, aber es dies aus Sicherheitsbedenken nicht tun. Denken wir darüber nach: Wenn B nicht zu C passt, heißt das, das entweder B oder C keine echten Duplikate sind. Wären es 2 Gruppen (A-B und A-C), würden Sie damit enden sowohl B als auch C zu löschen. Und ist keine der Beiden ein Duplikat, möchten Sie das ganz sicher nicht tun, richtig? Also verwirft dupeGuru in diesem Fall den A-C Treffer (und fügt eine Notiz in der Statusbar hinzu). Folglich, wenn Sie B löschen und den Scan erneut durchführen, haben Sie einen A-C Treffer nächstes Mal in den Ergebnissen.

.. topic:: Ich möchte alle Dateien aus einem bestimmten Ordner markieren. Was kann ich tun?

    Aktiveren Sie den :doc:`Nur Duplikate <results>` Modus und klicken auf die Ordnerspalte, um die Duplikate nach Ordner zu sortieren. Es wird dann einfach sein, alle Duplikate aus dem selben Ordner auszuwählen und auf die Leertaste zu drücken, um sie alle zu markieren.

.. only:: edition_se or edition_pe

    .. topic:: Ich möchte alle Dateien löschen, deren Größe sich um mehr als 300 KB von ihrer Referenz unterscheidet. Was kann ich tun?

        * Aktivieren Sie den :doc:`Nur Duplikate <results>` Modus.
        * Aktivieren Sie den **Deltawerte** Modus.
        * Gehen Sie auf die "Größe" Spalte, um die Ergebnisse nach Größe zu sortieren.
        * Alle Duplikate unter -300 auswählen.
        * Klicken Sie auf **Entferne Ausgewählte von den Ergebnissen**.
        * Alle Duplikate über 300 auswählen
        * Klicken Sie auf **Entferne Ausgewählte von den Ergebnissen**.

    .. topic:: Ich möchte meine zuletzt geänderten Dateien zur Referenz machen. Was kann ich tun?

        * Aktivieren Sie den :doc:`Nur Duplikate <results>` Modus.
        * Aktivieren Sie den **Deltawerte** Modus.
        * Gehen Sie auf die "Modifikation" Spalte, um die Ergebnisse nach Änderungsdatum zu sortieren.
        * Klicken Sie erneut auf die "Modifikation" Spalte, um die Reihenfolge umzukehren.
        * Wählen Sie alle Duplikate über 0.
        * Klicken Sie auf **Mache Ausgewählte zur Referenz**.

    .. topic:: Ich möchte alle Duplikate mit dem Wort copy markieren. Wie mache ich das?

        * **Windows**: Klicken Sie auf **Aktionen --> Filter anwenden**, tippen "copy" und klicken auf OK.
        * **Mac OS X**: Geben Sie "copy" in das "Filter" Feld in der Werkzeugleiste ein.
        * Klicken Sie **Markieren --> Alle Markieren**.

.. only:: edition_me
    
    .. topic:: Ich möchte alle Stücke markieren, die mehr als 3 Sekunden von ihrer Referenz verschieden sind. Was kann ich tun?

        * Aktivieren Sie den :doc:`Nur Duplikate <results>` Modus.
        * Aktivieren Sie den **Deltawerte** Modus.
        * Klicken Sie auf die "Zeit" Spalte, um nach Zeit zu sortieren.
        * Wählen Sie alle Duplikate unter -00:03.
        * Klicken Sie auf **Entferne Ausgewählte von den Ergebnissen**.
        * Wählen Sie alle Duplikate über 00:03.
        * Klicken Sie auf **Entferne Ausgewählte von den Ergebnissen**.

    .. topic:: Ich möchte meine Stücke mit der höchsten Bitrate zur Referenz machen. Was kann ich tun?
    
        * Aktivieren Sie den :doc:`Nur Duplikate <results>` Modus.
        * Aktivieren Sie den **Deltawerte** Modus.
        * Klicken Sie auf die "Bitrate" Spalte, um nach Bitrate zu sortieren.
        * Klicken Sie erneut auf die "Bitrate" Spalte, um die Reihenfolge umzukehren.
        * Wählen Sie alle Duplikate über 0.
        * Klicken Sie auf **Mache Ausgewählte zur Referenz**.

    .. topic:: Ich möchte nicht das [live] und [remix] Versionen meiner Stücke als Duplikate erkannt werden. Was kann ich tun?
    
        Ist Ihre Vergleichsschwelle niedrig genug, werden möglicherweise die live und remix Versionen in der Ergebnisliste landen. Das kann nicht verhindert werden, aber es gibt die Möglichkeit die Ergebnisse nach dem Scan zu entfernen, mittels dem Filter. Möchten Sie jedes Stück mit irgendetwas in eckigen Klammern [] im Dateinamen entfernen, so:
    
        * **Windows**: Klicken Sie auf **Aktionen --> Filter anwenden**, geben "[*]" ein und klicken OK.
        * **Mac OS X**: Geben Sie "[*]" in das "Filter" Feld der Werkzeugleiste ein.
        * Klicken Sie auf **Markieren --> Alle Markieren**.
        * Klicken Sie auf **Entferne Ausgewählte von den Ergebnissen**.

.. topic:: Ich habe versucht, meine Duplikate in den Mülleimer zu verschieben, aber dupeGuru sagt es ist nicht möglich. Warum? Was kann ich tun?

    Meistens kann dupeGuru aufgrund von Dateirechten keine Dateien in den Mülleimer schicken. Sie brauchen **Schreib** Rechte für Dateien, die in den Mülleimer sollen. Wenn Sie nicht vertraut mit Kommandozeilenwerkzeugen sind, können dafür auch Dienstprogramme wie `BatChmod <http://macchampion.com/arbysoft/BatchMod>`_ verwendet werden, um die Dateirechte zu reparieren.

    Wenn dupeGuru sich nach dem Reparieren der Recht immer noch verweigert, könnte es helfen die Funktion "Verschiebe Markierte nach..." als Workaround zu verwenden. Anstelle die Dateien in den Mülleimer zu schieben, senden SIe sie in einen temporären Ordner, den Sie dann manuell löschen können.

    .. only:: edition_pe

        Wenn Sie versuchen *iPhoto* Bilder zu löschen, dann ist der Grund des Versagens ein Anderer. Das Löschen schlägt fehl, weil dupeGuru nicht mit iPhoto kommunizieren kann. Achten Sie darauf nicht mit iPhoto herumzuspielen, während dupeGuru arbeitet, damit das Löschen funktioniert. Außerdem scheint das Applescript System manchmal zu vergessen wo sich iPhoto befindet, um es zu starten. Es hilft in diesen Fällen, wenn Sie iPhoto starten **bevor** Duplikate in den Mülleimer verschoben werden.

    Wenn dies alles fehlschlägt, kontaktieren Sie `HS support <http://www.hardcoded.net/support>`_, wir werden das Problem lösen.

.. todo:: This FAQ qestion is outdated, see english version.
