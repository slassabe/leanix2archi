#!/usr/bin/env python
# coding: utf-8

'''
 Purpose :
   Dump LeanIx and convert output in various file format
   - Changelog
'''


def getBanner():
    return """
 _        ___   ____  ____   ____  __ __      ______   ___        ____  ____      __  __ __  ____
| T      /  _] /    T|    \ l    j|  T  T    |      T /   \      /    T|    \    /  ]|  T  Tl    j
| |     /  [_ Y  o  ||  _  Y |  T |  |  |    |      |Y     Y    Y  o  ||  D  )  /  / |  l  | |  T
| l___ Y    _]|     ||  |  | |  | l_   _j    l_j  l_j|  O  |    |     ||    /  /  /  |  _  | |  |
|     T|   [_ |  _  ||  |  | |  | |     |      |  |  |     |    |  _  ||    \ /   \_ |  |  | |  |
|     ||     T|  |  ||  |  | j  l |  |  |      |  |  l     !    |  |  ||  .  Y\     ||  |  | j  l
l_____jl_____jl__j__jl__j__j|____j|__j__|      l__j   \___/     l__j__jl__j\_j \____jl__j__j|____j
"""

def getNotes(ws, when):
    return f"""
Export du contenu LeanIX vers Archimate au format OEF (Open Exchange File)
# workspace : {ws}
# date : {when}

Version 1.0 (05/06/2020) :
========================
# Version opérationnelle

Version 2.0 (10/08/2020)
==========================
# Refactoring

Version 3.1 (19/08/2020) :
==========================
# Correction sur la suppression du lien consommateur d'une interface qui empèche le merge de modèle

Version 3.3 (27/08/2020) :
==========================
# Export du cycle de vie et des tags LeanIX sous forme de properties LeanIx
    - LEANIX.FIELDS.LIFECYCLE.{plan | phaseIn | active | phaseOut | endOfLife }
    - LEANIX.FIELDS.EXTERNAL_ID
    - LEANIX.TAGS.{ Hiérarchie projet }

Version 3.4 (09/09/2020) :
==========================
# Trace les interfaces mal formatées dans le fichier de warnings

Version 4.2 (03/11/2020) :
==========================
# Refactoring et industrialisation
# documentation

Version 4.3 (10/11/2020) :
==========================
# Résolution partielle du changement dans le temps du types d'interfaces
    c'est à dire un Flow qui devient une Interface par l'ajout de consommateurs
  Ce qui génère des erreurs lors du "Merge" dans Archi avec une version plus ancienne de modèle
  C'est une corrections partielle car le cas des Interfaces qui deviennent des Flows n'est pas traité pour l'instant

Version 4.5 (10/08/2021) :
==========================
# Il existe maintenant 2 fichiers d'extraction de LeanIX : mode light avec uniquement les éléments applicatifs et un mode full complet.

Version 5.0 (21/02/2023) :
==========================
# Rework important pour être packagée sous forme d'image docker
# Export par SFTP

May Archimate be with You :-)

"""
