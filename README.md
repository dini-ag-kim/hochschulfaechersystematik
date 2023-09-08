# Hochschulfächersystematik

Diese Hochschulfächersystematik basiert auf der Destatis-Systematik der Fächergruppen, Studienbereiche und Studienfächer (http://bartoc.org/node/18919) und wird gepflegt von der [OER-Metadatengruppe der DINI-AG KIM](https://wiki.dnb.de/display/DINIAGKIM/OER-Metadatengruppe). Die Systematik ist Bestandteil der Spezifikationen [LOM for Higher Education OER Repositories](https://w3id.org/kim/hs-oer-lom-profil/latest/) und [LRMI-Profil (Entwurf)](https://github.com/dini-ag-kim/lrmi-profile).

## Maintainer

[Michael Menzel](https://github.com/mic-men) und [Adrian Pohl](https://github.com/acka47)

## Status

Veröffentlicht

## Entwicklung und Publikation

In der Entwicklung des Vokabulars nutzen wir die [StöberSpecs](https://w3id.org/kim/stoeberspecs/)-Wekzeuge und -Prozesse. Das Vokabular wird in diesem [GitHub Repo](https://github.com/dini-ag-kim/hochschulfaechersystematik) in der Datei [hochschulfaechersystematik.ttl](https://github.com/dini-ag-kim/hochschulfaechersystematik/blob/master/hochschulfaechersystematik.ttl) versioniert und gepflegt. Als Beschreibungssprache wird das [Simple Knowledge Organization System (SKOS)](https://www.w3.org/2004/02/skos/) in [Turtle](https://www.w3.org/TR/turtle/)-Syntax verwendet. Die offizielle Publikation erfolgt unter der URI [https://w3id.org/kim/hochschulfaechersystematik/scheme](https://w3id.org/kim/hochschulfaechersystematik/scheme) mit [SkoHub-Vocabs](https://github.com/hbz/skohub-vocabs), einer grafischen Präsentation des Vokabulars mit weitergehenden Möglichkeiten wie einer Suchfunktion.

Die erste Turtle-codierte SKOS-Version wurde aus einer XML-Version der [Virtuellen Hochschule Bayern (vhb)](https://www.vhb.org/) geniert (mit `$ npm i && node xml2nt > hochschulfaechersystematik.ttl`). Diese erste Turtle-Version wurde und wird schrittweise nach Bedarf angepasst.

## Mitarbeit und Kontakt

Mitarbeit und Kontakt findet am besten statt über [Issues](https://github.com/dini-ag-kim/hochschulfaechersystematik/issues) oder die [Mailingliste der OER-Metadatengruppe](http://lists.dnb.de/mailman/listinfo/dini-ag-kim-oer).
