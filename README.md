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

## Opgave 4 – Python HTTP-klient med socket

Opgaven bad mig skrive et lille program i Python, der sender en HTTP GET-forespørgsel til `localhost:8000/index.html` og viser svaret til brugeren. Fra min TCP-klient i Netværks-lag kunne jeg genkende delen med `socket.socket` – det nye var, at jeg nu selv skulle forme en rigtig HTTP-request i stedet for bare at sende tekst.

Forskellen på at bruge `curl` og selv at skrive klienten er, at jeg nu selv bestemmer hver del af requesten. Det betyder også, at jeg kan sende forespørgsler, som et almindeligt værktøj eller en browser ikke ville sende.

Requesten skal slutte med en tom linje (`\r\n\r\n`), ellers bliver serveren ved med at vente på resten. Netop den mekanisme udnyttes i Slowloris-angreb, hvor man åbner mange forbindelser og aldrig afslutter dem, så serveren løber tør for pladser til rigtige brugere.

Jeg skulle `encode()` før afsendelse, fordi socket'en arbejder med bytes, og `decode()` svaret, fordi jeg ville have det som læsbar tekst. Huskereglen: encode når du sender, decode når du modtager. Svaret hentede jeg med `recv()` i en løkke, fordi et HTTP-svar kan komme i flere bidder – løkken samler dem, indtil serveren lukker forbindelsen.

**Hvorfor er det relevant for cybersikkerhed?**
Når man selv kan forme hver byte i en request, kan man teste en server med forespørgsler, en browser aldrig ville sende – forkerte headers, mærkelige stier eller ufuldstændige requests. Det er netop den slags kontrol, der bruges til at finde fejl og sårbarheder, og det hænger sammen med min pointe fra øvelse 4 om, at en server kan være for tilgivende.

## Opgave 5 – Python HTTP-server med socket

Opgaven bad mig skrive et lille program i Python, der svarer på en HTTP GET-forespørgsel. I modsætning til Opgave 4, hvor jeg sendte en request, skal serveren nu modtage en request og selv sende et svar tilbage. Jeg genbrugte `bind`, `listen`, `accept` og `recv` fra min TCP-server i Netværks-lag – det nye var at forme et korrekt HTTP-svar.

Et HTTP-svar skal indeholde en statuslinje (fx `HTTP/1.1 200 OK`), nogle headers der beskriver svaret, en tom linje, og til sidst selve body'en. Den tomme linje er afgørende: den fortæller klienten, hvor headerne slutter, og indholdet begynder.

Jeg brugte `len(body.encode())` til `Content-Length` og ikke bare tekstens længde, fordi værdien skal være antal bytes, ikke antal tegn. Jeg bandt serveren til `127.0.0.1` og ikke `0.0.0.0`, fordi den så kun kan nås lokalt – det minimerer angrebsfladen.

Undervejs fik jeg fejlen "Address already in use". Det viste sig at være min egen fejl: jeg havde byttet om på mine SSH-faner og havde stadig `python3 -m http.server` kørende på port 8000. Jeg fandt processen med `ss -tlnp | grep 8000` (kørt som root, fordi `ss` ikke er blandt de sudo-kommandoer, admin har adgang til efter Linux 101), stoppede den gamle server, og så kunne min egen binde til porten.

**Hvorfor er det relevant for cybersikkerhed?**
Når jeg selv bygger serveren, bestemmer jeg hele svaret, inklusive `Content-Length`, som klienten bare stoler på. Det gjorde det konkret for mig, hvordan en server kan lyve om sit svar, og hvorfor forkerte længder kan udnyttes til angreb som request smuggling. Min server er også bevidst "for tilgivende": den svarer ens på alle stier og alle requests, også ugyldige. En rigtig server bør skelne, og den slags for tillidsfulde servere er netop dem, der er lette at misbruge.

## Status

- Øvelse 1-4: Udført
- Opgave 1: Udført
- Opgave 2: Udført (Host-header-kravet blev dækket i forbindelse med Øvelse 4)
- Opgave 3: Udført
- Opgave 4: Udført (Python HTTP-klient med socket)
- Opgave 5: Udført (Python HTTP-server med socket)
- Opgave 6 (valgfri parøvelse): Ikke udført

## Filer i dette repo

- `index.html` – testsiden, som serveren leverer
- `ovelse4-ovelse5/http_klient.py` – HTTP-klient, der sender en GET-request
- `ovelse4-ovelse5/http_server.py` – HTTP-server, der svarer på GET-requests
