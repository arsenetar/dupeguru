Sélection de dossiers
=====================

La première fenêtre qui apparaît lorsque dupeGuru démarre est la fenêtre de sélection de dossiers à scanner. Elle détermine la liste des dossiers qui seront scannés lorsque vous cliquerez sur **Scan**.

Pour ajouter un dossier, cliquez sur le bouton **+**. Si vous avez ajouté des dossiers dans le passé, un menu vous permettra de rapidement choisir un de ceux ci. Autrement, il vous sera demandé d'indiquer le dossier à ajouter. 

Vous pouvez aussi utiliser le drag & drop pour ajouter des dossiers à la liste.

Pour retirer un dossier, sélectionnez le et cliquez sur **-**. Si le dossier sélectionné est un sous-dossier, son type changera pour **exclus** (voyez plus bas) au lieu d'être retiré.

Types de dossiers
-----------------

Tout dossier ajouté à la liste est d'un type parmis ces trois:

* **Normal:** Les doublons trouvés dans ce dossier peuvent être effacés.
* **Reference:** Les doublons trouvés dans ce dossier ne peuvent **pas** être effacés. Les fichiers provenant de ce dossier ne peuvent qu'être en position "Référence" dans le groupes de doublons.
* **Excluded:** Les fichiers provenant de ce dossier ne sont pas scannés.

Le type par défaut pour un dossier est, bien entendu, **Normal**. Vous pouvez utiliser le type **Référence** pour les dossiers desquels vous ne voulez pas effacer de fichiers.

Le type d'un dossier s'applique à ses sous-dossiers, excepté si un sous-dossier a un autre type explicitement défini.

.. only:: edition_pe

    Bibliothèques iPhoto et Aperture
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    
    dupeGuru PE supporte iPhoto et Aperture, ce qui veut dire qu'il sait comment lire le contenu de
    ces bibliothèques et comment communiquer avec ces applications pour correctement supprimer des
    photos de celles-ci. Pour utiliser cette fonctionnalité, vous devez ajouter iPhoto et/ou
    Aperture avec les boutons spéciaux "Ajouter librairie iPhoto" et "Ajouter librairie Aperture",
    qui apparaissent quand on clique sur le petit "+". Les dossiers ajoutés seront alors
    correctement interprétés par dupeGuru.
    
    Quand une photo est supprimée d'iPhoto, elle est envoyée dans la corbeille d'iPhoto.

    Quand une photo est supprimée d'Aperture, il n'est malheureusement pas possible de l'envoyer
    dans sa corbeille. Ce que dupeGuru fait à la place, c'est de créer un projet "dupeGuru Trash"
    et d'envoyer les photos dans ce projet. Vous pouvez alors supprimer toutes les photos de ce
    projet manuellement.

.. only:: edition_me

    Bibliothèques iTunes
    ^^^^^^^^^^^^^^^^^^^^
    
    dupeGuru ME supporte iTunes, ce qui veut dire qu'il sait comment lire le contenu de sa
    bibliothèque et comment communiquer avec iTunes pour correctement supprimer des chansons de sa
    bibliothèque. Pour utiliser cette fonctionnalité, vous devez ajouter iTunes avec le bouton
    spécial "Ajouter librairie iTunes", qui apparait quand on clique sur le petit "+". Le dossier
    ajouté sera alors correctement interprété par dupeGuru.
    
    Quand une chanson est supprimée d'iTunes, elle est envoyée à la corebeille du système, comme un
    fichier normal. La différence ici, c'est qu'après la suppression, iTunes est correctement mis au
    fait de cette suppression et retire sa référence à cette chanson de sa bibliothèque.
