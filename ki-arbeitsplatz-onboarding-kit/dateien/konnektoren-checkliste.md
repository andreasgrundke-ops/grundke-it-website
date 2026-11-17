# Konnektoren — Checkliste und Nachweis

Auszufüllen beim Einrichten. Zweck: jederzeit belegen können, was verbunden ist, warum, und wer es
freigegeben hat. Diese Liste zu haben, bevor die IT danach fragt, macht den Unterschied.

**Person:** [Name] · **Konto:** [Mailadresse] · **Plan:** [Pro / Max / Team] · **Stand:** [Datum]

---

## Verbundene Konnektoren

| Konnektor | Zweck | Zugriffsart | Freigabe durch | Datum | Nächste Prüfung |
|---|---|---|---|---|---|
| Lokaler Ordner `[Pfad]` | Dateiarbeit im Arbeitsordner | lesen + schreiben | — (Privatgerät) | | |
| Browser (Chrome) | Recherche, Formulare | je Website | — | | |
| | | | | | |
| | | | | | |

## Nicht verbunden — bewusst

| Konnektor | Warum nicht | Wiedervorlage |
|---|---|---|
| Microsoft 365 | Administratorzustimmung im Tenant nicht erteilt | [Datum] |
| Power BI / Fabric | Vorabversion, Freigabe der Plattformadministration erforderlich | [Datum] |
| | | |

---

## Prüffragen je Konnektor

Vor dem Verbinden zu beantworten. Wer eine Frage nicht beantworten kann, verbindet noch nicht.

1. **Wozu genau** brauche ich ihn? Eine konkrete Aufgabe, nicht „könnte nützlich sein".
2. **Welche Daten** werden dadurch erreichbar?
3. **Lesend oder schreibend?** Wenn schreibend: was kann im schlimmsten Fall passieren?
4. **Wer hat freigegeben?** Bei allem mit Arbeitsbezug: Name und Datum.
5. **Wie nehme ich ihn wieder weg**, wenn er nicht gebraucht wird?

## Regeln

- **Sparsam.** Jeder Konnektor erweitert, was bei einem Fehler betroffen ist.
- **Eng.** Ordnerfreigaben auf den Arbeitsordner, Browserfreigaben je Website.
- **Befristet.** Was drei Monate ungenutzt bleibt, wird getrennt.
- **Aus vertrauenswürdiger Quelle.** Ein eigener Konnektor ist fremder Code mit Zugriff auf die eigene
  Sitzung — er gehört geprüft wie jede andere Software.

## Halbjährliche Durchsicht

- [ ] Wird jeder Konnektor noch benutzt?
- [ ] Stimmen die Berechtigungen noch, oder sind sie gewachsen?
- [ ] Sind Freigaben noch gültig?
- [ ] Gibt es neue Konnektoren, die etwas Selbstgebautes ersetzen?
- [ ] Ist die Liste hier aktuell?

Datum der letzten Durchsicht: ____________

---

*CI 2026.01 · Grundke IT-Service · [grundke-it.de](https://grundke-it.de) · Arbeitsbuch v1.1.1*
