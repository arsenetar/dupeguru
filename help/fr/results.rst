Résultats
==========

Quand dupeGuru a terminé de scanner, la fenêtre de résultat apparaît avec la liste de groupes de doublons trouvés.

À propos des groupes de doublons
---------------------------------

Un groupe de doublons est un groupe de fichier dans lequel tous les fichiers sont le doublon de tous les autres fichiers. Chaque groupe a son **fichier de référence** (le premier fichier du groupe). Ce fichier est celui qui n'est jamais effacé, et il est donc impossible de le marquer.

Les critères utilisés pour décider de quel fichier d'un groupe devient la référence sont multiples. Il y a d'abord les dossiers référence. Tout fichier provenant d'un dossier de type "Référence" ne peut être autre chose qu'une référence dans un groupe. Si il n'y a pas de fichiers provenant d'un dossier référence, alors le plus gros fichier est placé comme référence.

Bien entendu, dans certains cas, il est possible que dupeGuru ne choisisse pas le bon fichier. Dans ce cas, sélectionnez un doublon à placer en position de référence, puis cliquez sur l'action **Transformer sélectionnés en références**.

Vérifier les résultats
------------------------

Bien que vous pouvez tout simplement faire **Tout marquer** puis tous envoyer à la corbeille, il est recommandé de vérifier les résultats avant, surtout si votre seuil de filtre est bas.

Pour vous aider dans cette tâche, vous pouvez utiliser le panneau de détails. Ce panneau montre les détails du fichier sélectionné côte-à-côte avec sa référence. Vous pouvez aussi double-cliquer sur un fichier pour l'ouvrir avec son application associée.

Si vous avez plus de faux doublons que de vrais (si votre seuil de filtre est très bas), la meilleure façon de procéder, au lieu de retirer les faux doublons des résultat, serait de marquer seulement les vrais doublons.

Marquer et sélectionner
-----------------------

Dans le vocabulaire de dupeGuru, il y a une nette différence entre sélectionner et marquer. Les fichiers **sélectionnés** sont ceux qui sont surlignés dans la liste. On peut sélectionner plusieurs fichiers à la fois en tenant Shift, Control ou Command lorsqu'on clique sur un fichier.

Les fichiers **marqués** sont ceux avec la petite boite cochée. Il est possible de marquer les fichiers sélectionnés en appuyant sur **espace**.

Ne pas montrer les références
-------------------------------

Quand ce mode est activé, les groupes de doublons sont (momentanément) brisés et les doublons sont montrés individuellement, sans leurs références. On peut agir sur les fichiers sous ce mode de la même façon que sous le mode normal.

L'attrait principal de ce mode est le tri. En mode normal, les groupes ne peuvent pas être brisés, et donc les résultats sont triés en fonction de leur référence. Sous ce mode spécial, le tri est fait au niveau des fichiers individuels. Il est alors possible, par exemple, de facilement marquer tous les fichiers de type "exe":

* Activer le mode **Ne pas montrer les références**.
* Ajouter la colonne "Type" par le menu "Colonnes".
* Cliquez sur la colonne Type pour changer le tri.
* Trouvez le premier fichier avec un type "exe".
* Sélectionnez-le.
* Trouvez le dernier fichier avec un type "exe".
* Tenez Shift et sélectionnez-le.
* Appuyez sur espace pour marquer les fichiers sélectionnés.

Montrer les valeurs en tant que delta
-------------------------------------

Sous ce mode, certaines colonnes montreront leur valeurs relativement à la valeur de la référence du
groupe (de couleur orange, pour bien les différencier des autres valeurs). Par exemple, si un
fichier a une taille de 1.2 MB alors que la référence a une taille de 1.4 MB, la valeur affichée
sous ce mode sera -0.2 MB.

Les valeurs non numériques sont aussi affectées par le mode delta. Par contre, plutôt que montrer la
différence avec la valeur de référence (ce qui est impossible), elles indiquent si elles sont
pareilles en adoptant la couleur orange dans le cas ou la valeur est différent. Il est ainsi
possible de facilement identifier, par exemple, tous le doublons qui ont un nom de fichier différent
de leur référence.

Les deux modes ensemble
-----------------------

Quand on active ces deux modes ensemble, il est alors possible de faire de la sélection de ficher
assez avancée parce que le tri de fichier se fait alors en fonction des valeurs delta. Il devient
alors possible de, par exemple, sélectionner tous les fichiers qui ont une différence de plus de 300
KB par rapport à leur référence, ou d'autres trucs comme ça.

Même chose pour les valeurs non numériques: quand les deux modes sont activés, les règles de tri
pour les valeurs non-numériques change. On commence par grouper les doublon selon si leur valeur est
orange ou non, pour ensuite procéder aux règles de tri normales. Avec ce système, il est alors
facile de, par exemple, marquer toues les doublons qui ont un nom de fichier différent de leur
référence: il suffit de trier par nom de fichier.

Filtrer les résultats
---------------------

Il est possible de filtrer les résultats pour agir sur un sous-ensemble de ceux-ci, par exemple tous
les fichiers qui contiennent le mot "copie".

Pour filtrer les résultats, entrer le filtrer dans le champ de la barre d'outils, puis appuyer sur
Entrée. Pour annuler le filtre, appuyez sur le X dans le champ.

En mode simple (le mode par défaut), ce que vous tapez est ce qui est filtré. Il n'y a qu'un
caractère spécial: **\***. Ainsi, si vous entrez "[*]", le filtre cherchera pour tout nom contenant
les "[" et "]" avec quelquechose au milieu.

Pour un filtrage avancé, activez **Utiliser les expressions régulières pour les filtres** dans les
:doc:`preferences`. Votre filtre sera alors appliqué comme une `expression régulière`_.

Les filtres sont dans tous les cas insensibles aux majuscules et minuscules.

Les expression régulière pour s'appliquer à un fichier n'ont pas besoin de correspondre au nom
entier. Une correspondance partielle suffit.

Vous remarquerez peut-être que ce ne sont pas tous les fichiers de vos résultats filtrés qui
s'appliquent au filtre. C'est parce que les groupes ne sont pas brisés par les filtres afin de
permettre une meilleure mise en context. Par contre, ces fichier seront en mode "Lecture seule" et
ne pourront être marqués.

Actions
-------

Voici la liste des actions qu'il est possible d'appliquer aux résultats.

* **Vider la liste de fichiers ignorés:** Ré-initialise la liste des paires de doublons que vous avez ignorés dans le passé.
* **Exporter vers HTML:** Exporte les résultats vers un fichier HTML et l'ouvre dans votre browser.
* **Envoyer marqués à la corbeille:** Le nom le dit.
* **Déplacer marqués vers...:** Déplace les fichiers marqués vers une destination de votre choix. La destination finale du fichier dépend de l'option "Déplacements de fichiers" dans les :doc:`preferences`.
* **Copier marqués vers...:** Même chose que le déplacement, sauf que c'est une copie à la place.
* **Retirer marqués des résultats:** Retire les fichiers marqués des résultats. Ils ne seront donc ni effacés, ni déplacés.
* **Retirer sélectionnés des résultats:** Retire les fichiers sélectionnés des résultats. Notez que si il y a des fichiers références parmi la sélection, ceux-ci sont ignorés par l'action.
* **Transformer sélectionnés en références:** Prend les fichiers sélectionnés et les place à la position de référence de leur groupe respectif. Si l'action est impossible (si la référence provient d'un dossier référence), rien n'est fait.
* **Ajouter sélectionnés à la liste de fichiers ignorés:** Retire les fichiers sélctionnés des résultats, puis les place dans une liste afin que les prochains scans ignorent les paires de doublons qui composaient le groupe dans lequel ces fichiers étaient membres.
* **Ouvrir sélectionné avec l'application par défaut:** Ouvre le fichier sélectionné avec son application associée.
* **Ouvrir le dossier contenant le fichier sélectionné:** Le nom dit tout.
* **Invoquer commande personnalisée:** Invoque la commande personnalisé que vous avez définie dans les :doc:`preferences`.
* **Renommer sélectionné:** Renomme le fichier sélectionné après vous avoir demandé d'entrer un nouveau nom.

**Déplacer des fichiers dans iPhoto/iTunes:** Attention, quand vous déplacez des fichiers des
bibliothèques iPhoto ou iTunes, elles ne sont pas vraiment déplacées, mais copiée. Il n'y a pas
d'action de déplacement possible dans ces bibliothèques.

Options de suppression
----------------------

Ces options, présentées lors de l'action de suppression de doublons, déterminent comment celle-ci
s'exécute. La plupart du temps, ces options n'ont pas a être activées.

* **Remplacer les fichiers effacés par des liens:** les fichiers supprimés seront replacés par des
  liens (`symlink`_ ou `hardlink`_) vers leur fichiers de référence respectifs. Un symlink est un
  lien symbolique (qui devient caduque si l'original est supprimé) et un hardlink est un lien direct
  au contenu du fichier (même si l'original est supprimé, le lien reste valide).

  Sur OS X et Linux, cette fonction est supportée pleinement, mais sur Windows, c'est un peu
  compliqué. Windows XP ne le supporte pas, mais Vista oui. De plus, cette fonction ne peut être
  utilisée que si dupeGuru roule avec les privilèges administratifs. Ouaip, Windows c'est la joie.

* **Supprimer les fichiers directement:** Plutôt que d'envoyer les doublons à la corbeille,
  directement les supprimer. Utiliser cette option si vous avez de la difficulté à supprimer des
  fichiers (ce qui arrive quelquefois quand on travaille avec des partages réseau).

.. _expression régulière: http://www.regular-expressions.info
.. _hardlink: http://en.wikipedia.org/wiki/Hard_link
.. _symlink: http://en.wikipedia.org/wiki/Symbolic_link
