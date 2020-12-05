<p align="center">
  <img src="https://raw.githubusercontent.com/ArnaudLhutereau/vuln_monitoring/main/ressources/logo.png" alt="Logo Vuln Monitoring"/>
</p>

### Qu'est-ce que c'est?

Vuln Monitoring est un script de surveillance des dernières vulnérabilités publiées sur Internet. Il parcourt des fils d'actualités et détecte si des logiciels utilisés par l'entreprise sont impactés.
Il vous notifie par mail dès qu'une vulnérabilitée est détectée.

<p align="center">
  <img src="https://raw.githubusercontent.com/ArnaudLhutereau/vuln_monitoring/main/ressources/preview.png" alt="Preview email notif"/>
</p>

### Pré-requis

- Un compte mail pour l'envoi de notifications (SMTP)
- Python, pip et quelques librairies
- 1 compte Twitter développeur avec une clé API


### Installation

1. Cloner le repertoire Git.

2. Installer les librairies nécéssaire au bon fonctionnement :
> pip install -r requirements.txt

3. Changer les variables d'environnements *(serveur SMTP, identifiants, clé API...)* dans le fichier *script.py*.

### Configuration

Vous pouvez configurer l'outil en personnalisant :
- Les applications surveillés : il suffit d'ajouter une nouvelle ligne dans le fichier *"application.txt"*.
- Le template de notification : il faut modifier le code HTML utilisé dans la fonction *sendEmailAlert()*. Le template par défaut est dans le dossier *ressources*.


### Déploiement

Par défaut, le script est configuré pour parcourir les fils d'actualités toutes les heures.

Il faut configurer un CRON sur l'environnement de déploiement afin d'automatiser l'éxécution du script.


> 0 * * * * python /path/to/script.py >/dev/null 2>&1


### Liste des connecteurs

- CVEnew sur Twitter (API)
- CERT-FR (flux RSS)



### Ajout d'un nouveau connecteur

Si vous souhaitez surveiller un nouveau fil d'actualité de vulnérabilité, vous pouvez créer une nouvelle
fonction et l'appeler dans la fonction main() de la façon suivante :

> alert_feed.append(**monNouveauConnecteur**(application_list))

Le paramètre application_list est un tableau contenant tous les noms des applications surveillées (exemple : *['nginx','windows 10']*).

La variable de retour alert_feed contient l'ensemble des vulnérabilités remontées durant l'execution.
Il s'agit d'un tableau qui contient des dictionnaires avec 3 champs :
- app_name : *Nom de l'application vulnérable remontée*
- description : *Description de la vulnérabilité*
- url : *Lien vers plus de détails*

### Changelog

- 05/12/2020 : Publication du script
