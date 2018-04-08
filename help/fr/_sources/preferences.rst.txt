Préférences
===========

.. only:: edition_se

    **Type de scan:** Cette option détermine quels aspects du fichier doit être comparé. Un scan par **Nom de fichier** compare les noms de fichiers mot-à-mot et, dépendant des autres préférences ci-dessous, déterminera si les noms se ressemblent assez pour être considérés comme doublons. Un scan par **Contenu** trouvera les doublons qui ont exactement le même contenu.
    
    Le scan **Dossiers** est spécial. Si vous le sélectionnez, dupeGuru cherchera des doublons de *dossiers* plutôt que des doublons de fichiers. Pour déterminer si deux dossiers sont des doublons, dupeGuru regarde le contenu de tous les fichiers dans les dossiers, et si **tous** sont les mêmes, les dossiers sont considérés comme des doublons.
    
    **Seuil du filtre:** Pour les scan de type **Nom de fichier**, cette option détermine le degré de similtude nécessaire afin de considérer deux noms comme doublons. Avec un seuil de 80, 80% des mots doivent être égaux. Pour déterminer ce pourcentage, dupeGuru compte le nombre de mots total des deux noms, puis compte le nombre de mots égaux, puis fait la division des deux. Un résultat égalisant ou dépassant le seuil sera considéré comme un doublon. Exemple: "a b c d" et "c d e" ont un pourcentage de 57 (4 mots égaux, 7 au total).

.. only:: edition_me

    **Type de scan:** Cette option détermine quels aspects du fichier doit être comparé. La nature de la comparaison varie grandement, dépendant de l'option choisie ici.

    * **Nom de fichier:** Le nom de fichier des chansons est comparé, mot-à-mot.
    * **Nom de fichier (Champs):** Les noms de fichiers sont séparés en plusieurs champs séparés par le caractère "-". Le pourcentage de comparaison final est le plus petit parmi les champs. Ce type de scan est utile pour comparer les noms de fichier au format "Artiste - Titre" pour lequel le nom de l'artist contient beaucoup de mots (et donc augmente faussement le pourcentage de comparaison).
    * **Nom de fichier (Champs sans ordre):** Comme **Nom de fichier (Champs)**, excepté que l'ordre des champs n'a pas d'importance. Par exemple, "Artiste - Titre" et "Titre - Artiste" auraient un pourcentage de 100% au lieu de 0%.
    * **Tags:** Méthode de loin la plus utile, elle lit les métadonnées des chansons et le compare mot-à-mot. Comme pour **Nom de fichier (Champs)**, le pourcentage final est le plus bas des champs comparés.
    * **Contenu:** Compare le contenu des chansons. Seul un contenu exactement pareil sera considéré comme un doublon.
    * **Contenu audio:** Comme **Contenu**, excepté que les métadonnée no sont pas comparées, seulement le contenu audio lui même. Encore une fois, le contenu doit être exactement le même.

    **Seuil du filtre:** Pour les scans basés sur le nom de fichier ou les tags, cette option détermine le degré de similtude nécessaire afin de considérer deux noms comme doublons. Avec un seuil de 80, 80% des mots doivent être égaux. Pour déterminer ce pourcentage, dupeGuru compte le nombre de mots total des deux noms, puis compte le nombre de mots égaux, puis fait la division des deux. Un résultat égalisant ou dépassant le seuil sera considéré comme un doublon. Exemple: "a b c d" et "c d e" ont un pourcentage de 57 (4 mots égaux, 7 au total).

    **Tags à scanner:** Pour les scans de type **Tags**, cette option détermine les tags qui seront comparés.

.. only:: edition_se or edition_me

    **Proportionalité des mots:** Pour les scans basés sur les mots, cette option change la méthode de calcul afin que les mots plus long pèsent plus dans la balance. Avec cette option, les mots ont une valeur égale à leur longeur. Par exemple, "ab cde fghi" et "ab cde fghij" ont un pourcentage de 53% (19 caractères au total, 10 caractères de mots égaux (4 pour "ab" et 6 pour "cde")).

    **Comparer les mots similaires:** Avec cette options, les mots similaires sont comptés comme égaux. Par exemple, "The White Stripes" et "The White Stripe" ont un pourcentage de 100% au lieu de 66%. **Attention:** Cette option a la potentialité de créer beaucoup de faux doublons. Soyez certains de manuellement vérifier vos résultats avant de les effacer.

.. only:: edition_pe

    **Type de scan:** Détermine le type de scan qui sera fait sur vos images. Le type **Contenu** compare le contenu des images de façon "fuzzy", rendant possible de trouver non seulement les doublons exactes, mais aussi les similaires. Le type **EXIF Timestamp** compare les métadonnées EXIF des images (si existantes) et détermine si le "timestamp" (moment de prise de la photo) est pareille. C'est beaucoup plus rapide que le scan par Contenu. **Attention:** Les photos modifiées gardent souvent le même timestamp, donc faites attention aux faux doublons si vous utilisez cette méthode.
    
    **Seuil du filtre:** *Scan par Contenu seulement.* Plus il est élevé, plus les images doivent être similaires pour être considérées comme des doublons. Le défaut de 95% permet quelques petites différence, comme par exemple une différence de qualité ou bien une légère modification des couleurs.

    **Comparer les images de tailles différentes:** Le nom dit tout. Sans cette option, les images de tailles différentes ne sont pas comparées.

**Comparer les fichiers de différents types:** Sans cette option, seulement les fichiers du même type seront comparés.

**Ignorer doublons avec hardlink vers le même fichier:** Avec cette option, dupeGuru vérifiera si les doublons pointent vers le même `inode <http://en.wikipedia.org/wiki/Inode>`_. Si oui, ils ne seront pas considérés comme doublons. (Seulement pour OS X et Linux)

**Utiliser les expressions régulières pour les filtres:** Avec cette option, les filtres appliqués aux résultats seront lus comme des `expressions régulières <http://www.regular-expressions.info>`_.

**Effacer les dossiers vides après un déplacement:** Avec cette option, les dossiers se retrouvant vides après avoir effacé ou déplacé des fichiers seront effacés aussi.

**Déplacements de fichiers:** Détermine comment les opérations de copie et de déplacement s'organiseront pour déterminer la destination finale des fichiers:

* **Directement à la destination:** Les fichiers sont envoyés directement dans le dossier cible, sans essayer de recréer leur ancienne hierarchie.
* **Re-créer chemins relatifs:** Le chemin du fichier relatif au dossier sélectionné dans la :doc:`sélection de dossier <folders>` sera re-créé. Par exemple, si vous ajoutez ``/Users/foobar/MonDossier`` lors de la sélection de dossier et que vous déplacez ``/Users/foobar/MonDossier/SousDossier/MonFichier.ext`` vers la destination ``/Users/foobar/MaDestination``, la destination finale du fichier sera ``/Users/foobar/MaDestination/SousDossier``.
* **Re-créer chemins absolus:** Le chemin du fichier est re-créé dans son entièreté. Par exemple, si vous déplacez ``/Users/foobar/MonDossier/SousDossier/MonFichier.ext`` vers la destination  ``/Users/foobar/MaDestination``, la destination finale du fichier sera ``/Users/foobar/MaDestination/Users/foobar/MonDossier/SousDossier``.

Dans tous les cas, dupeGuru résout les conflits de noms de fichier en ajoutant un numéro en face du nom.

**Commande personelle:** Cette option vous permet de définir une ligne de commande à appeler avec le fichier sélectionné (ainsi que sa référence) comme argument. Cette commande sera invoquée quand vous cliquerez sur **Invoquer commande personnalisée**. Cette command est utile si, par exemple, vous avez une application de comparaison visuelle de fichiers que vous aimez bien.

Le format de la ligne de commande est la même que celle que vous écrireriez manuellement, excepté pour les arguments, **%d** et **%r**. L'endroit où vous placez ces deux arguments sera remplacé par le chemin du fichier sélectionné (%d) et le chemin de son fichier référence dans le groupe (%r).

Si le chemin de votre executable contient un espace, vous devez le placer entre guillemets "". Vous devriez aussi placer vos arguments %d et %r entre guillemets parce qu'il est très possible d'avoir des chemins de fichier contenant des espaces. Voici un exemple de commande personnelle::  
  
    "C:\Program Files\SuperDiffProg\SuperDiffProg.exe" "%d" "%r"
