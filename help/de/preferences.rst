Einstellungen
=============

.. only:: edition_se

    **Scan Typ:** Diese Option bestimmt nach welcher Eigenschaft die Dateien in einem Duplikate Scan verglichen werden. Wenn Sie **Dateiname** auswählen, wird dupeGuru jeden Dateinamen Wort für Wort vergleichen und, abhängig von den unteren Einstellungen, feststellen ob genügend Wörter übereinstimmen, um 2 Dateien als Duplikate zu betrachten. Wenn Sie **Inhalt** wählen, werden nur Dateien mit dem exakt gleichen Inhalt zusammenpassen.
    
    Der **Ordner** Scan Typ ist etwas speziell. Wird er ausgewählt, scannt dupeGuru nach doppelten Ordnern anstelle von Dateien. Um festzustellen ob 2 Ordner identisch sind, werden alle Datein im Ordner gescannt und wenn die Inhalte aller Dateien der Ordner übereinstimmen, werden die Ordner als Duplikate erkannt.
    
    **Filterempfindlichkeit:** Wenn Sie den **Dateiname** Scan Typ wählen, bestimmt diese Option wie ähnlich 2 Dateinamen für dupeGuru sein müssen, um Duplikate zu sein. Ist die Empfindlichkeit zum Beispiel 80, müssen 80% der Worte der 2 Dateinamen übereinstimmen. Um den Übereinstimmungsanteil herauszufinden, zählt dupeGuru zuerst die Gesamtzahl der Wörter **beider** Dateinamen, dann werden die gleichen Wörter gezählt (jedes Wort zählt als 2) und durch die Gesamtzahl der Wörter dividiert. Ist das Resultat größer oder gleich der Filterempfindlichkeit, haben wir ein Duplikat. Zum Beispiel, "a b c d" und "c d e" haben einen Übereinstimmungsanteil von 57 (4 gleiche Wörter, insgesamt 7 Wörter).

.. only:: edition_me

    **Scan Typ:** Diese Option bestimmt nach welcher Eigenschaft die Dateien in einem Duplikate Scan verglichen werden. Die Beschaffenheit des Duplikate Scans hängt hauptsächlich davon ab, was Sie für diese Option auswählen.

    * **Dateiname:** Der Dateiname jedes Stücks wird in einzelne Wörter zerlegt und verglichen, um den Übereinstimmungsanteil zu berechnen. Ist das Resultat größer oder gleich der **Filterempfindlichkeit** (siehe unten für mehr Details), wird dupeGuru die beiden Stücke als Duplikate erkennen.
    * **Dateiname - Felder:** Wie **Dateiname**, außer das, nachdem der Dateiname in Wörter geteilt wurde, diese Wörter in Felder gruppiert werden. Der Feldseparator ist " - ". Der endgültige Übereinstimmungsanteil ist der kleinste Übereinstimmungssatz zwischen den Feldern. Also, "Ein Künstler - Der Titel" und "Ein Künstler - Anderer Titel" hätte eine Übereinstimmung von 50 (Bei einem **Dateiname** Scan wäre es 75).
    * **Dateiname - Felder (keine Reihenfolge):** Wie **Dateiname - Felder**, außer das die Feldreihenfolge keine Rolle spielt. Also, "Ein Künstler - Der Titel" und "Der Titel - Ein Künstler" hätte eine Übereinstimmung von 100 anstelle von 0.
    * **Tags:** Diese Methode liest die Tags (Metadaten) jedes Stücks und vergleicht ihre Werte. Es wird, wie in **Dateiname - Felder**, die niedrigste Übereinstimmung als endgültiger Übereinstimmungsanteil betrachtet.
    * **Inhalt:** Diese Scanmethode nutzt den Inhalt des Stücks, um Duplikate zu erkennen. Damit 2 Stücke mit dieser Methode gleich sind, müssen sie **exakt den selben Inhalt** haben.
    * **Audioinhalt:** Das selbe wie Inhalt, aber nur der Audioinhalt wird verglichen (ohne Metadaten).

    **Filterempfindlichkeit:** Wenn Sie den **Dateiname** Scan Typ wählen, bestimmt diese Option wie ähnlich 2 Dateinamen für dupeGuru sein müssen, um Duplikate zu sein. Ist die Empfindlichkeit zum Beispiel 80, müssen 80% der Worte der 2 Dateinamen übereinstimmen. Um den Übereinstimmungsanteil herauszufinden, zählt dupeGuru zuerst die Gesamtzahl der Wörter **beider** Dateinamen, dann werden die gleichen Wörter gezählt (jedes Wort zählt als 2) und durch die Gesamtzahl der Wörter dividiert. Ist das Resultat größer oder gleich der Filterempfindlichkeit, haben wir ein Duplikat. Zum Beispiel, "a b c d" und "c d e" haben einen Übereinstimmungsanteil von 57% (4 gleiche Wörter, insgesamt 7 Wörter).

    **Tags zu scannen:** Bei der Nutzung des **Tags** Scan Typs, können Sie wählen welche Tags verglichen werden sollen.

.. only:: edition_se or edition_me

    **Wortgewichtung:** Wenn Sie den **Dateiname** Scan Type nutzen, ändert diese Option leicht die Berechnung der Übereinstimmung. Mit Wortgewichtung hat jedes Wort nicht mehr den Wert 1 in der Duplikatezählung und der Gesamtwortzahl, sondern einen Wert der sich aus der Gesamtzahl der Buchstaben des Wortes ergibt. Mit Wortgewichtung hätte "ab cde fghi" und "ab cde fghij" eine Übereinstimmung von 53% (Gesamt 19 Buchstaben, 10 gleiche Buchstaben (4 für "ab" und 6 für "cde")).

    **Ähnliche Wörter gleich** Wird diese Option angeschaltet, zählen ähnliche Wörter als Übereinstimmung. Zum Beispiel hätte mit dieser Option "The White Stripes" und "The White Stripe" eine Übereinstimmung von 100 anstelle von 0. **Warnung:** Nutzen Sie diese Option mit Vorsicht. Es ist wahrscheinlich, das sie eine hohe Anzahl an Falschpositiven erhalten. Wie auch immer, Sie werden Duplikate finden, die Sie sonst nie gefunden hätten. Der Suchdurchlauf wird außerdem mit dieser Option etwas länger dauern.

.. only:: edition_pe

    **Scan Typ:** Diese option bestimmt, welcher Scan Typ bei Ihren Bildern angewendet wird. Der **Inhalte** Scan Typ vergleicht den Inhalt der Bilder auf eine ungenaue Art und Weise (so werden nicht nur exakte Duplikate gefunden, sondern auch Ähnliche). Der **EXIF Zeitstempel** Scan Typ schaut auf die EXIF Metadaten der Bilder (wenn vorhanden) und erkennt Bilder die den Selben haben. Er ist viel schneller als der Inhalte Scan. **Warnung:** Veränderte Bilder behalten oft den selben EXIF Zeitstempel, also achten Sie auf Falschpositive bei der Nutzung dieses Scans.
    
    **Filterempfindlichkeit:** *Nur Inhalte Scan.* Je höher diese Einstellung, desto strenger ist der Filter (Mit anderen Worten, desto weniger Ergebnisse erhalten Sie). Die meisten Bilder der selben Qualität stimmen zu 100% überein, selbst wenn das Format anders ist (PNG und JPG zum Beispiel). Wie auch immer, wenn ein PNG mit einem JPG niederiger Qualität übereinstimmen soll, muss die Filterempfindlichkeit kleiner als 100 sein. Die Voreinstellung, 95, ist eine gute Wahl.

    **Bilder unterschiedlicher Abmessung gleich:** Wird diese Box gewählt, dürfen Bilder unterschiedlicher Abmessung in einer Duplikategruppe sein..

**Dateitypen dürfen gemischt werden:** Wird diese Box gewählt, dürfen Duplikategruppen Bilder mit unterschiedlichen Dateierweiterungen enthalten.

**Ignoriere Duplikate die mit derselben Datei verlinkt sind:** Ist diese Option aktiviert, wird dupeGuru überprüfen ob Duplikate auf den selben `inode <http://en.wikipedia.org/wiki/Inode>`_ verweisen. Wenn sie es tun, werden sie nicht als Duplikat erkannt. (Nur für OS X und Linux)

**Nutze reguläre Ausdrücke beim Filtern:** Ist diese Option aktiviert, wird die Filterfunktion Ihre Filteranfrage als **regulären Ausdruck** interpretieren. Sie zu erklären ist außerhalb des Aufgabenbereiches dieser Dokumentation. Ein guter Platz zum Starten ist `regular-expressions.info <http://www.regular-expressions.info>`_.

**Entferne leere Ordner nach dem Löschen oder Verschieben:** Ist diese Option aktiviert, werden Ordner gelöscht nachdem eine Datei gelöscht oder verschoben wurde und der Ordner leer ist.

**Copy and Move:** Determines how the Copy and Move operations (in the Action menu) will behave.

* **Zum Ziel:** Alle Dateien werden direkt in das ausgwählte Verzeichnis gesendet, ohne zu versuchen den Quellpfad wiederherzustellen
* **Relativen Pfad neu erstellen:** Der Pfad der Quelldatei wird im Zielverzeichnis wiederhergestellt bis zur Wurzelauswahl im Verzeichnis Panel. Zum Beispiel, wenn Sie ``/Users/foobar/SomeFolder`` zu ihrem Verzeichnis Panel hinzufügen und ``/Users/foobar/SomeFolder/SubFolder/SomeFile.ext`` zu dem Ziel ``/Users/foobar/MyDestination`` verschieben, wird das endgültige Ziel der Datei ``/Users/foobar/MyDestination/SubFolder`` sein (``SomeFolder`` wurde vom Pfad der Quelldatei im endgültigen Ziel abgetrennt.).
* **Absoluten Pfad neu erstellen:** Der Pfad der Quelldatei wird im Zielverzeichnis vollständig wiederhergestellt. Zum Beispiel, wenn Sie ``/Users/foobar/SomeFolder/SubFolder/SomeFile.ext`` zu dem Ziel ``/Users/foobar/MyDestination`` verschieben, wird das endgültige Ziel der Datei ``/Users/foobar/MyDestination/Users/foobar/SomeFolder/SubFolder`` sein.

Auf jeden Fall behandelt dupeGuru Namenskonflikte indem es dem Ziel-Dateinamen eine Nummer voranstellt, wenn der Dateiname bereits im Zielverzeichnis existiert.

**Eigener Befehl:** Diese Einstellung bestimmt den Befehl der durch "Führe eigenen Befehl aus" ausgeführt wird. Sie können jede externe Anwendung durch diese Aktion aufrufen. Dies ist zum Beispiel hilfreich, wenn Sie eine gute diff-Anwendung installiert haben.

Das Format des Befehls ist das Selbe wie in einer Befehlszeile, außer das 2 Platzhalter vorhanden sind: **%d** und **%r**. Diese Platzhalter werden durch den Pfad des markierten Duplikates (%d) und dem Pfad der Duplikatereferenz ersetzt (%r).
  
Wenn der Pfad Ihrer ausführbaren Datei Leerzeichen enthält, so schließen sie ihn bitte mit "" Zeichen ein. Sie sollten auch Platzhalter mit den Zitatzeichen einschließen, denn es ist möglich, das die Pfade der Duplikate und Referenzen ebenfalls Leerzeichen enthalten. Hier ist ein Beispiel eines eigenen Befehls::
  
    "C:\Program Files\SuperDiffProg\SuperDiffProg.exe" "%d" "%r"
