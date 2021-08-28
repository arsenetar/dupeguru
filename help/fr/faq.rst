Foire aux questions
===================

.. contents::

Qu'est-ce que dupeGuru?
------------------------

.. only:: edition_se

    dupeGuru est un outil pour trouver des doublons parmi vos fichiers. Il peut comparer soit les
    noms de fichiers, soit le contenu. Le comparateur de nom de fichier peut trouver des doublons
    même si les noms ne sont pas exactement pareils.

.. only:: edition_me

    dupeGuru Music Editon est un outil pour trouver des doublons parmi vos chansons. Il peut
    comparer les noms de fichiers, les tags ou bien le contenu. Les comparaisons de nom de fichier
    ou de tags peuvent trouver des doublons même si les noms de sont pas exactement pareils.

.. only:: edition_pe

    dupeGuru Picture Edition est un outil pour trouver des doublons parmi vos images. Non seulement
    il permet de trouver les doublons exactes, mais il est aussi capable de trouver les images ayant
    de légères différences, étant de format différent ou bien ayant une qualité différente.

En quoi est-il mieux que les autres applications?
-------------------------------------------------

dupeGuru est hautement configurable. Vous pouvez changer les options de comparaison afin de trouver
exactement le type de doublons recherché. Plus de détails sur la
:doc:`page de préférences <preferences>`.

dupeGuru est-il sécuritaire?
----------------------------

Oui. dupeGuru a été conçu afin d'être certain que vous conserviez toujours au moins une copie des
doublons que vous trouvez. Il est aussi possible de configurer dupeGuru afin de déterminer certains
dossier à partir desquels aucun fichier ne sera effacé.

Quelles sont les limitation démo de dupeGuru?
---------------------------------------------

En mode de démonstration, les actions sont limitées à 10 doublons par session. En mode `Fairware`_,
il n'y a pas de limitation.

Je ne peux pas marquer le doublons que je veux effacer, pourquoi?
-----------------------------------------------------------------

Tour groupe de doublons contient au moins un fichier dit "référence" et ce fichier ne peut pas être
effacé. Par contre, ce que vous pouvez faire c'est de le remplacer par un autre fichier du groupe.
Pour ce faire, sélectionnez un fichier du groupe et cliquez sur l'action **Transformer sélectionnés
en références**.
    
Notez que si le fichier référence du groupe vient d'un dossier qui a été défini comme dossier
référence, ce fichier ne peut pas être déplacé de sa position de référence du groupe.

J'ai un dossier duquel je ne veut jamais effacer de fichier.
------------------------------------------------------------

Si vous faites un scan avec un dossier qui ne doit servir que de référence pour effacer des doublons
dans un autre dossier, changez le type de dossier à "Référence" dans la fenêtre de
:doc:`sélection de dossiers <folders>`.

Que veut dire '(X hors-groupe)' dans la barre de statut?
--------------------------------------------------------

Lors de certaines comparaisons, il est impossible de correctement grouper les paires de doublons et
certaines paires doivent être retirées des résultats pour être certain de ne pas effacer de faux
doublons. Example: Nous avons 3 fichiers, A, B et C. Nous les comparons en utilisant un petit seuil
de filtre. La comparaison détermine que A est un double de B, A est un double C, mais que B n'est
**pas** un double de C. dupeGuru a ici un problème. Il ne peut pas créer un groupe avec A, B et C.
Il décide donc de jeter C hors du groupe. C'est de là que vient la notice '(X hors-groupe)'.
    
Cette notice veut dire que si jamais vous effacez tout les doubles contenus dans vos résultats et
que vous faites un nouveau scan, vous pourriez avoir de nouveaux résultats.

Je veux marquer tous les fichiers provenant d'un certain dossier. Quoi faire?
-----------------------------------------------------------------------------

Activez l'option :doc:`Ne pas montrer les références <results>` et cliquez sur la colonne Dossier
afin de trier par dossier. Il sera alors facile de sélectionner tous les fichiers de ce dossier
(avec Shift+selection) puis ensuite d'appuyer sur Espace pour marquer les fichiers sélectionnés.

.. only:: edition_se or edition_pe

    Je veux enlever tous les doublons qui ont une différence de plus de 300KB avec leur référence.
    ----------------------------------------------------------------------------------------------

    * Activez l'option :doc:`Ne pas montrer les références <results>`.
    * Activez l'option **Montrer les valeurs en tant que delta**.
    * Cliquez sur la colonne Taille pour changer le tri.
    * Sélectionnez tous les fichiers en dessous de -300.
    * Cliquez sur l'action **Retirer sélectionnés des résultats**.
    * Sélectionnez tous les fichiers au dessus de 300.
    * Cliquez sur l'action **Retirer sélectionnés des résultats**.

    Je veux que le fichier avec la plus grande date de dernière modification soit la référence.
    -------------------------------------------------------------------------------------------

    * Activez l'option :doc:`Ne pas montrer les références <results>`.
    * Activez l'option **Montrer les valeurs en tant que delta**.
    * Cliquez sur la colonne Modification (deux fois, afin d'avoir un ordre descendant) pour changer le tri.
    * Sélectionnez tous les fichiers au dessus de 0.
    * Cliquez sur l'action **Transformer sélectionnés en références**.

    Je veux marquer tous les fichiers contenant le mot "copie".
    -----------------------------------------------------------

    * Entrez le mot "copie" dans le champ "Filtre" dans la fenêtre de résultats puis appuyez sur
      Entrée.
    * Cliquez sur **Tout Marquer** dans le menu Marquer.

.. only:: edition_me

    Je veux enlever les doublons qui ont une différence de plus de 3 secondes avec leur référence.
    ----------------------------------------------------------------------------------------------

    * Activez l'option :doc:`Ne pas montrer les références <results>`.
    * Activez l'option **Montrer les valeurs en tant que delta**.
    * Cliquez sur la colonne Temps pour changer le tri.
    * Sélectionnez tous les fichiers en dessous de -00:03.
    * Cliquez sur l'action **Retirer sélectionnés des résultats**.
    * Sélectionnez tous les fichiers au dessus de 00:03.
    * Cliquez sur l'action **Retirer sélectionnés des résultats**.

    Je veux que mes chansons aux bitrate le plus élevé soient mes références.
    -------------------------------------------------------------------------

    * Activez l'option :doc:`Ne pas montrer les références <results>`.
    * Activez l'option **Montrer les valeurs en tant que delta**.
    * Cliquez sur la colonne Bitrate (deux fois, afin d'avoir un ordre descendant) pour changer le tri.
    * Sélectionnez tous les fichiers au dessus de 0.
    * Cliquez sur l'action **Transformer sélectionnés en références**.

    Je veux enlever les chansons contenant "[live]" ou "[remix]" de mes résultat.
    -----------------------------------------------------------------------------

    Si votre seuil de filtre est assez bas, il se pourrait que vos chansons live ou vos remix soient
    détectés comme des doublons. Vous n'y pouvez rien, mais ce que vous pouvez faire est d'enlever
    ces fichiers de vous résultats après le scan. Si, par exemple, vous voulez enlever tous les
    doublons contenant quelque mot que ce soit entre des caractères "[]", faites:

    * Entrez "[*]" dans le champ "Filtre" dans la fenêtre de résultats puis appuyez sur Entrée.
    * Cliquez sur **Tout Marquer** dans le menu Marquer.
    * Cliquez sur l'action **Retirer marqués des résultats**.

J'essaie d'envoyer mes doublons à la corbeille, mais dupeGuru me dit que je ne peux pas. Pourquoi?
--------------------------------------------------------------------------------------------------

La plupart du temps, la raison pour laquelle dupeGuru ne peut pas envoyer des fichiers à la
corbeille est un problème de permissions. Vous devez avoir une permission d'écrire dans les fichiers
que vous voulez effacer. Si vous n'êtes pas familiers avec la ligne de commande, vous pouvez
utiliser des outils comme `BatChmod`_ pour modifier vos permissions.

Si malgré cela vous ne pouvez toujours pas envoyer vos fichiers à la corbeille, essayez l'option
"Supprimer les fichiers directement" qui vous est offerte lorsque vous procédez à l'effacement des
doublons. Cette option fera en sorte de supprimer directement les fichiers sans les faire passer par
la corbeille. Dans certains cas, ça règle le problème.

.. only:: edition_pe

    Si vous essayez d'effacer des photos dans iPhoto, alors la raison du problème est différente.
    L'opération rate parce que dupeGuru ne peut pas communiquer avec iPhoto. Il faut garder à
    l'esprit qu'il ne faut pas toucher à iPhoto pendant l'opération parce que ça peut déranger la
    communication entre dupeGuru et iPhoto. Aussi, quelque fois, dupeGuru ne peut pas trouver
    l'application iPhoto. Il faut mieux alors démarrer iPhoto avant l'opération.

Dans le pire des cas, `contactez le support HS`_, on trouvera bien.

Où sont les fichiers de configuration de dupeGuru?
--------------------------------------------------

Si, pour une raison ou une autre, vous voulez effacer ou modifier les fichiers générés par dupeGuru,
voici où ils sont:

* Linux: ``~/.local/share/data/Hardcoded Software/dupeGuru``
* Mac OS X: ``~/Library/Application Support/dupeGuru``
* Windows: ``\Users\<username>\AppData\Local\Hardcoded Software\dupeGuru``

Les fichiers de préférences sont ailleurs:

* Linux: ``~/.config/Hardcoded Software/dupeGuru.conf``
* Mac OS X: Dans le système ``defaults`` sous ``com.hardcoded-software.dupeguru``
* Windows: Dans le Registre, sous ``HKEY_CURRENT_USER\Software\Hardcoded Software\dupeGuru``

Pour la Music Edition et Picture Edition, remplacer "dupeGuru" par "dupeGuru Music Edition" et
"dupeGuru Picture Edition", respectivement.

.. _Fairware: http://open.hardcoded.net/about/
.. _BatChmod: http://www.lagentesoft.com/batchmod/index.html
.. _contactez le support HS: http://www.hardcoded.net/support
