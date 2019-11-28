# Hochschulfachersystematik

Dieses Repository beinhaltet eine SKOS-Version der Destatis-Systematik der Fächergruppen, Studienbereiche und Studienfächer (http://bartoc.org/node/18919) sowie den Code zur Generierung der SKOS-Version aus einer innerhalb der Virtuellen Hochschule Bayern (vhb) genutzten XML-Version.

Um aus der Quelldatei die Turtle-codierte SKOS Version zu generieren, `$ npm i && node xml2nt > fachgebiete.ttl` ausführen.
