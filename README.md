# Introduktion til HTTP

Denne README fungerer som en logbog over min forståelse og mine refleksioner, mens jeg arbejder mig igennem opgaven "Introduktion til HTTP". Jeg bruger min Ubuntu-server (samme VM som i Linux 101-opgaven) til at køre en simpel HTTP-server og teste den med `curl` og `netcat`.

## Opsætning

Jeg oprettede en simpel `index.html`-side og startede en Python-webserver i samme mappe med:

```bash
python3 -m http.server
```

Serveren lytter på `0.0.0.0:8000`, hvilket betyder, at den tager imod forbindelser på alle netværksinterfaces på maskinen, ikke kun på localhost.

Det er i sig selv en sikkerhedsovervejelse: når serveren er bundet til `0.0.0.0`, kan den nås fra andre maskiner på netværket, mens den med `127.0.0.1` kun ville være tilgængelig lokalt. Til en testserver er det fint, men i praksis vil man binde til mindst muligt – samme princip som jeg mødte i Netværks-lag-opgaven.

## Øvelse 1 – Åbn siden i en browser

Jeg hentede siden med `curl` og kunne se, at serveren svarer med HTML-indholdet fra `index.html`, samtidig med at serverens log viser requesten (IP, metode, sti og statuskode). Her lærte jeg, at hver gang en klient henter en side, logger serveren det som en separat request – det er sådan, man som administrator kan se, hvem der har tilgået hvad.

**Hvorfor er det relevant for cybersikkerhed?**
At kunne se og forstå serverens logs er grundlaget for at kunne opdage unormal eller mistænkelig trafik senere. Hvis man ikke forstår, hvad en "normal" request ser ud som, kan man heller ikke genkende en unormal.

## Øvelse 2 – Hent siden med cURL

Jeg brugte `curl -i` til at se både headers og body i svaret. Det gjorde det tydeligt, at et HTTP-svar altid består af en statuslinje, en række headers og til sidst selve indholdet (body), adskilt af en tom linje.

**Hvorfor er det relevant for cybersikkerhed?**
Headers afslører ofte mere, end man regner med – fx server-software og version. At kunne læse dem er første skridt til at vurdere, om en server lækker information, den ikke burde.

## Øvelse 3 – cURL med verbose output

Med `curl -v` kunne jeg se hele kommunikationen, inklusive at klienten først prøvede at oprette forbindelse via IPv6 (`::1`), fordi `localhost` kan slå op til både IPv6 og IPv4. Det forsøg faldt igennem, og `curl` faldt tilbage til IPv4 (`127.0.0.1`), hvor serveren lyttede. Det gav mig en bedre forståelse af, at en klient kan prøve flere veje, før den finder en, der virker, og at det er helt normalt at se "mislykkede" forsøg i en verbose-log, uden at det nødvendigvis er et problem.

**Hvorfor er det relevant for cybersikkerhed?**
`curl -v` viser præcis, hvad der sendes og modtages på ledningen. Den evne til at se den rå trafik er grundlæggende, når man skal fejlfinde eller analysere, om en forbindelse opfører sig, som den skal.

## Øvelse 4 – Hent siden med Netcat

Her skulle jeg selv skrive en rå HTTP-request med `netcat`. Første forsøg uden en `Host`-header gav stadig et svar fra testserveren, men jeg lærte, at `Host`-headeren egentlig er et krav i HTTP/1.1 (jf. RFC 9112) – test-serveren var bare tilgivende og svarede alligevel. Det viste mig, at man ikke altid kan stole på, at en server fejler "korrekt" bare fordi en klient ikke følger spec'en 100 %.

**Hvorfor er det relevant for cybersikkerhed?**
Det er et godt eksempel på, at en implementation kan afvige fra specifikationen uden at det er synligt i hverdagen – men den slags afvigelser kan udnyttes, hvis en server er mere tillidsfuld end den bør være.

## Opgave 1 – Hvordan bestemmes det, hvilken side der leveres?

Jeg lærte at adskille tre dele af en request, som hver har sin egen rolle:

- **IP-adressen** finder selve serveren (svarer til en vej og husnummer).
- **`Host`-headeren** bestemmer, hvilken "beboer"/hjemmeside der spørges efter på den adresse – relevant når flere domæner deler samme IP.
- **Stien (path)** bestemmer, hvilken specifik side/ressource hos den beboer, der skal leveres.

I vores tilfælde med kun én side på serveren er `Host` og path trivielle (localhost:8000 og `/`), men princippet bliver vigtigt, så snart en server skal hoste flere sider eller domæner.

**Hvorfor er det relevant for cybersikkerhed?**
Fordi flere domæner kan dele samme IP, er det `Host`-headeren, der afgør, hvilken side man rammer. Det gør headeren til et angrebspunkt – fx Host-header-manipulation, hvor en forkert eller forfalsket Host kan narre en server til at opføre sig anderledes end tiltænkt.

## Opgave 3 – Hvor meget data sender serveren egentlig?

Jeg undersøgte svarets størrelse på to måder:

- `curl -s | wc -c` talte kun body'en: **380 bytes**.
- `curl -s -i | wc -c` talte headers + body: **566 bytes**.

I browserens DevTools (Network-fanen) kunne jeg se det samme skel: en "resource size" (selve indholdet, ca. 0,4 kB) og en "transferred" størrelse (hele svaret inkl. headers, ca. 0,6 kB). Det gav mig en konkret forståelse af, at `Content-Length`-headeren kun beskriver body'en – ikke hele HTTP-svaret.

**Hvorfor er det relevant for cybersikkerhed?**
`Content-Length` er en værdi, serveren selv påstår er korrekt – en klient (eller en mellemliggende proxy) er nødt til at stole på den. Hvis denne værdi er forkert eller manipuleret, kan det bruges til angreb som request/response smuggling, hvor to parter er uenige om, hvor et HTTP-svar egentlig slutter.

## Status

- Øvelse 1-4: Udført
- Opgave 1: Udført
- Opgave 2: Udført (Host-header-kravet blev dækket i forbindelse med Øvelse 4)
- Opgave 3: Udført
- Opgave 4-5 (Python-programmer): Ikke påbegyndt endnu
- Opgave 6 (valgfri parøvelse): Ikke udført

## Filer i dette repo

- `index.html` – testsiden, som serveren leverer
- `ovelse4-ovelse5/` – mappe til de to kommende Python-programmer (HTTP-klient og HTTP-server med `socket`)
