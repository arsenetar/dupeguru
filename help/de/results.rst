Ergebnisse
==========

Sobald dupeGuru den Duplikatescan beendet hat, werden die Ergebnisse in Form einer Duplikate-Gruppenliste gezeigt.

Über Duplikatgruppen
--------------------

Eine Duplikatgruppe ist eine Gruppe von übereinstimmenden Dateien. Jede Gruppe hat eine **Referenzdatei** und ein oder mehrere **Duplikate**. Die Referenzdatei ist die 1. Datei der Gruppe. Die Auswahlbox ist deaktiviert. Darunter befinden sich die eingerückten Duplikate.

Sie können Duplikate markieren, aber niemals die Referenzdatei der Gruppe. Das ist eine Sicherheitsmaßnahme, die dupeGuru davon abhält nicht nur die Duplikate zu löschen, sondern auch die Referenzdatei. Sie wollen sicher nicht das das passiert, oder?

Welche Dateien Referenz oder Duplikate sind hängt zuerst von ihrem Ordnerzustand ab. Eine Datei von einem Referenzordner ist immer Referenz einer Duplikatgruppe. Sind alle Dateien aus normalen Ordnern, bestimmt die Größe welche Datei die Referenz einer Gruppe sein wird. DupeGuru nimmt an, das Sie immer die größte Datei behalten wollen. Also übernimmt die größte Datei die Referenzposition.

Sie können die Referenzdatei manuell verändern. Um das zu tun, wählen Sie das Duplikat aus, das zur Referenz befördert werden soll und drücken auf **Aktionen-->Mache Ausgewählte zur Referenz**.

Ergebnisse beurteilen
---------------------

Obwohl Sie einfach auf **Markieren-->Alles markieren** gehen und dann **Aktionen-->Verschiebe Markierte in den Mülleimer** ausführen können, um schnell alle Duplikate zu löschen, ist es sinnvoll erst alle Duplikate zu betrachten, bevor man sie löscht.

Um die Überprüfung zu erleichtern, können Sie das **Detail Panel** öffnen. Dieses Panel zeigt alle Details der gerade ausgewählten Datei sowie deren Referenz Details. Das ist sehr praktisch um schnell zu bestimmen, ob ein Duplikat wirklich ein Duplikat ist. Sie können außerdem auf die Datei doppelt klicken, um sie mit der verknüpften Anwendung zu öffnen.

Wenn Sie mehr Falschpositive als echte Duplikate haben (die Filterempfindlichkeit sehr niedrig ist), ist es der beste Weg die echten Duplikate zu markieren und mit **Aktionen-->Verschiebe Markierte in den Mülleimer** zu entfernen. Haben Sie mehr echte Duplikate als Falschpositive, können Sie stattdessen alle unechten Duplikate markieren und **Entferne Markierte aus den Ergebnissen** nutzen.

Markierung und Auswahl
----------------------

Ein **markiertes** Duplikat ist ein Duplikat, dessen kleine Box ein Häkchen hat. Ein **ausgewähltes** Duplikat ist hervorgehoben. Mehrfachauswahl wird in dupeGuru über den normalen Weg erreicht (Shift/Command/Steuerung Klick). Sie können die Markierung aller Duplikate umschalten, indem sie **Leertaste** drücken.

.. todo:: Add "Non-numerical delta" information.

Nur Duplikate anzeigen
----------------------

Wird dieser Modus aktiviert, so werden ausschließlich Duplikate ohne ihre respektive Referenzdatei gezeigt. Sie können diese Liste auswählen, markieren und sortieren, ganz wie im normalen Modus.

Die dupeGuru Ergebnisse werden, im normalen Modus, nach der **Referenzdatei** der Duplikatgruppen sortiert. Das bedeutet zum Beispiel, um alle Duplikate mit der "exe" Erweiterung zu markieren, können Sie nicht einfach die Ergebnisse nach "Typ" ordnen um alle exe Duplikate zu erhalten, denn eine Gruppe kann aus mehreren Typen (Dateiarten) bestehen. Hier kommt der Nur-Duplikate Modus ins Spiel. Um alle "exe" Duplikate zu markieren, müssen Sie nur:

* Nur Duplikate anzeigen aktivieren
* Die "Typ" Spalte über das "Spalten" Menü hinzufügen
* Auf "Typ" klicken, um die Liste zu sortieren
* Das erste Duplikat mit dem "exe" Typ lokalisieren.
* Es auswählen.
* Die Liste herunterscrollen und das letzte Duplikat mit dem "exe" Typ finden.
* Die Shift Taste halten und es auswählen.
* Leertaste drücken, um alle ausgewählten Duplikate zu markieren.

Deltawerte
----------

Wenn Sie diesen Schalter aktivieren, zeigen einige Spalten den Wert relativ zur Duplikate-Referenz anstelle des absoluten Wertes an. Diese Deltawerte werden zusätzlich in einer anderen Farbe dargestellt, um sie leichter zu entdecken. Zum Beispiel, ein Duplikat ist 1,2 MB groß und die Referenz 1,4 MB, dann zeigt die Größe-Spalte -0,2 MB.

Nur Duplikate anzeigen und Deltawerte
-------------------------------------

Der Nur-Duplikate Modus enthüllt seine wahre Macht nur, wenn der Deltawerte Schalter aktiviert wurde. Wenn Sie ihn anschalten, werden relative Werte anstelle Absoluter gezeigt. Wenn Sie also, zum Beispiel, alle Duplikate die mehr als 300 KB von der Referenz verschieden sind aus der Ergebnisliste entfernen möchten, so sortieren Sie die Duplikate nach der Größe, wählen alle Duplikate mit weniger als -300 in der Größe-Spalte, löschen sie und tun das selbe für Duplikate mit mehr als +300 auf der Unterseite der Liste.

Sie können dies außerdem nutzen, um die Referenzpriorität der Duplikateliste zu ändern. Wenn sie einen neuen Scan durchführen ist die größte Datei jeder Gruppe die Referenzdatei, solange keine Referenzordner existieren. Wollen Sie beispielsweise die Referenz nach der letztes Änderungszeit bestimmen, können Sie das Nur-Duplikate Ergebnis nach Änderungszeit in **absteigender** Reihenfolge sortieren, alle Duplikate mit einem Änderungszeit-Deltawert größergleich 0 auswählen und auf **Mache Ausgewählte zur Referenz** klicken. Der Grund warum die Sortierung absteigend erfolgen muss ist, wenn 2 Dateien der selben Duplikatgruppe ausgewählt werden und Sie **Mache Ausgewählte zur Referenz** klicken, dann wird nur der Erste der Liste wirklich als Referenz gesetzt. Da Sie nur die zuletzt geänderte Datei als Referenz haben möchten, stellt die vorangegangene Sortierung sicher, das der erste Eintrag der Liste auch der zuletzt Geänderte ist.

Filtern
-------

DupeGuru unterstützt das Filtern nach dem Scandurchlauf. Damit können Sie ihre Ergebnisse einschränken und diverse Aktionen auf einer Teilmenge ausführen. Beispielsweise ist es möglich alle Duplikate, deren Dateiname "copy" enthält mithilfe dieser Filterfunktion zu markieren.

**Windows/Linux:** Um diese Filterfunktion zu nutzen, klicken Sie Aktionen --> Filter anwenden, geben den Filter ein und drücken OK. Um zurück zu den ungefilterten Ergebnissen zu gelangen, gehen Sie auf Aktionen --> Filter entfernen.

**Mac OS X:** Um diese Filterfunktion zu nutzen, geben Sie ihren Filter im "Filter" Suchfeld in der Symbolleiste ein. Um zurück zu den ungefilterten Ergebnissen zu gelangen, leeren Sie das Feld oder drücken auf "X".

Im Einfach-Modus (Voreinstellung) wird jede Zeichenkette die Sie eingeben auch zum Filtern genutzt, mit Ausnahme einer Wildcard: **\***. Wenn Sie "[*]" als Filter nutzen, wird alles gefunden was die eckigen Klammern [] enthält, was auch immer zwischen diesen Klammern stehen mag.

Für fortgeschrittenes Filtern, können Sie "Nutze reguläre Ausdrücke beim Filtern" aktivieren. Diese Funktion erlaubt es Ihnen **reguläre Ausdrücke** zu verwenden. Ein regulärer Ausdruck ist ein Filterkriterium für Text. Das zu erklären sprengt den Rahmen dieses Dokuments. Ein guter Platz für eine Einführung ist `regular-expressions.info <http://www.regular-expressions.info>`_.

Filter ignorieren, im Einfach- und RegExp-Modus, die Groß- und Kleinschreibung.

Damit der Filter etwas findet, muss Ihr regulärer Ausdruck nicht auf den gesamten Dateinamen passen. Der Name muss nur eine Zeichenkette enthalten die auf den Ausdruck zutrifft.

Sie bemerken vielleicht, das nicht alle Duplikate in Ihren gefilterten Ergebnissen auf den Filter passen. Das liegt daran, sobald ein Duplikat einer Gruppe vom Filter gefunden wird, bleiben die restlichen Duplikate der Gruppe mit in der Liste, damit Sie einen besseren Überblick über den Kontext der Duplikate erhalten. Nicht passende Duplikate bleiben allerdings im "Referenz-Modus". Dadurch können Sie sicher sein Aktionen wie "Alles Markieren" anzuwenden und nur gefilterte Duplikate zu markieren.

Aktionen Menü
-------------

* **Ignorier-Liste leeren:** Entfernt alle ignorierten Treffer die Sie hinzugefügt haben. Um wirksam zu sein, muss ein neuer Scan für die gerade gelöschte Ignorier-Liste gestartet werden.
* **Exportiere als XHTML:** Nimmt die aktuellen Ergebnisse und erstellt aus ihnen eine XHTML Datei. Die Spalten die sichtbar werden, wenn sie auf diesen Knopf drücken, werden die Spalten in der XHTML Datei sein. Die Datei wird automatisch mit dem Standardbrowser geöffnet.
* **Verschiebe Markierte in den Mülleimer:** Verschiebt alle markierten Duplikate in den Mülleimer.
* **Lösche Markierte und ersetze mit Hardlinks:** Verschiebt alle Markierten in den Mülleimer. Danach werden die gelöschten Dateien jedoch mit Hardlinks zur Referenzdatei ersetzt `hard link <http://en.wikipedia.org/wiki/Hard_link>`_ . (Nur OS X und Linux)
* **Verschiebe Markierte nach...:** Fragt nach einem Ziel und verschiebt alle Markierten zum Ziel. Der Quelldateipfad wird vielleicht am Ziel neu erstellt, abhängig von der "Kopieren und Verschieben" Einstellung.
* **Kopiere Markierte nach...:** Fragt nach einem Ziel und kopiert alle Markierten zum Ziel. Der Quelldateipfad wird vielleicht am Ziel neu erstellt, abhängig von der "Kopieren und Verschieben" Einstellung.
* **Entferne Markierte aus den Ergebnissen:** Entfernt alle markierte Duplikate aus den Ergebnissen. Die wirklichen Dateien werden nicht angerührt und bleiben wo sie sind.
* **Entferne Ausgewählte aus den Ergebnissen:** Entfernt alle ausgewählten Duplikate aus den Ergebnissen. Beachten Sie das ausgewählte Referenzen ignoriert werden, nur Duplikate können entfernt werden.
* **Mache Ausgewählte zur Referenz:** Ernenne alle ausgewählten Duplikate zur Referenz. Ist ein Duplikat Teil einer Gruppe, die eine Referenzdatei aus einem Referenzordner hat (blaue Farbe), wird keine Aktion für dieses Duplikat durchgeführt. Ist mehr als ein Duplikat aus der selben Gruppe ausgewählt, wird nur das Erste jeder Gruppe befördert.
* **Füge Ausgewählte der Ignorier-Liste hinzu:** Dies entfernt zuerst alle ausgewählten Duplikate aus den Ergebnissen und fügt danach das aktuelle Duplikat und die Referenz der Ignorier-Liste hinzu. Diese Treffer werden bei zukünftigen Scans nicht mehr angezeigt. Das Duplikat selbst kann wieder auftauchen, es wird dann jedoch zur einer anderen Referenz gehören. Die Ignorier-Liste kann mit dem Ignorier-Liste leeren Kommando gelöscht werden.
* **Öffne Ausgewählte mit Standardanwendung:** Öffnet die Datei mit der Anwendung die mit dem Dateityp verknüpft ist.
* **Zeige Ausgewählte:** Öffnet den Ordner der die ausgewählte Datei enthält.
* **Eigenen Befehl ausführen:** Ruft die in den Einstellungen definierte externe Anwendung auf und nutzt die aktuelle Auswahl als Argumente für den Aufruf.
* **Ausgewählte umbenennen:** Fragt nach einem neuen Namen und benennt die ausgewählte Datei um.

.. todo:: Add Move and iPhoto/iTunes warning
.. todo:: Add "Deletion Options" section.