# -*- coding: utf-8 -*-
"""Add 'Ukens Dua' sections to the backside of each week file."""
import os

BASE = os.path.join(os.path.dirname(__file__), '..', 'uker')

CSS_BLOCK = """
/* Ukens dua */
.dua-section {
  margin-top: 3mm;
  padding: 2mm 3mm;
  border-top: .5pt solid #c8c0a8;
  background: #fdf8ed;
}
.dua-title {
  font-family: Arial, sans-serif;
  font-size: 8pt; font-weight: 900;
  color: #1a1a2e; background: #f7e636;
  padding: .3mm 2mm; display: inline-block;
  margin-bottom: 1.5mm;
}
.dua-trans {
  font-size: 7.5pt; font-style: italic;
  color: #3d2b1f; margin-bottom: 1.5mm;
  line-height: 1.4;
}
.dua-betyr {
  font-size: 7pt; color: #222;
  margin-bottom: 1mm; line-height: 1.4;
}
.dua-kilde {
  font-size: 5.5pt; color: #888;
  font-family: Arial, sans-serif;
}"""

CSS_ANCHOR = """.in-f {
  position: absolute; bottom: 2mm; right: 2mm;
  font-size: 5pt; color: #ddd;
  font-family: Arial, sans-serif;
}"""

# (week_start, title, transliteration, meaning_norwegian, source)
DUAS = [
    (7,
     "Morgonb&oslash;nn",
     "Allahumma bika asbahna, wa bika amsayna, wa bika nahya, wa bika namutu, wa ilaykan-nushur.",
     "&Aring; Allah, ved Deg v&aring;kner vi, ved Deg g&aring;r vi til hvile, ved Deg lever vi, ved Deg d&oslash;r vi, og til Deg er oppstandelsen.",
     "Sunan at-Tirmidhi, nr. 3391"),

    (9,
     "B&oslash;nn om nyttig kunnskap",
     "Allahumma inni as&rsquo;aluka &lsquo;ilman nafi&lsquo;an, wa rizqan tayyiban, wa &lsquo;amalan mutaqabbalan.",
     "&Aring; Allah, jeg ber Deg om nyttig kunnskap, god rizq (forsyning) og aksepterte handlinger.",
     "Sunan Ibn Majah, nr. 925"),

    (11,
     "B&oslash;nnen til Yunus (fred v&aelig;re med ham)",
     "La ilaha illa Anta, subhanaka, inni kuntu minadh-dhalimin.",
     "Det er ingen gud unntatt Deg, &aelig;re v&aelig;re Deg! Jeg har sannelig v&aelig;rt blant de urettferdige.",
     "Sunan at-Tirmidhi, nr. 3505 &mdash; Koran 21:87"),

    (13,
     "B&oslash;nn om standhaftighet",
     "Ya Muqallibal-qulub, thabbit qalbi &lsquo;ala dinik.",
     "&Aring; Du som vender hjertene, gjør mitt hjerte standhaftig p&aring; Din religion.",
     "Sunan at-Tirmidhi, nr. 2140"),

    (15,
     "B&oslash;nn om god karakter",
     "Allahumma inni a&lsquo;udhu bika min munkaratil-akhlaq, wal-a&lsquo;mal, wal-ahwa&rsquo;.",
     "&Aring; Allah, jeg s&oslash;ker tilflukt hos Deg fra d&aring;rlig karakter, onde handlinger og villfarende lyster.",
     "Sunan at-Tirmidhi, nr. 3591"),

    (17,
     "B&oslash;nn for foreldrene",
     "Rabbighfir li wa liwalidayya wa liman dakhala baytiya mu&rsquo;minan wa lil-mu&rsquo;minina wal-mu&rsquo;minat.",
     "Min Herre, tilgi meg og mine foreldre, og den som trer inn i mitt hus som troende, og de troende menn og kvinner.",
     "Koran 71:28"),

    (19,
     "Beskyttelse mot ilden",
     "Allahumma ajirni minan-nar.",
     "&Aring; Allah, beskytt meg mot ilden. (Sies syv ganger etter Fajr og Maghrib.)",
     "Sunan Abu Dawud, nr. 5079 &mdash; hasan"),

    (21,
     "B&oslash;nn om tilgivelse (Laylatul Qadr)",
     "Allahumma innaka &lsquo;afuwwun tuhibbul-&lsquo;afwa fa&rsquo;fu &lsquo;anni.",
     "&Aring; Allah, Du er Den som tilgir, Du elsker &aring; tilgi, s&aring; tilgi meg.",
     "Sunan at-Tirmidhi, nr. 3513"),

    (23,
     "B&oslash;nn etter &aring; ha spist",
     "Alhamdu lillahil-ladhi at&lsquo;amani hadha wa razaqanihi min ghayri hawlin minni wa la quwwah.",
     "All lovprisning tilh&oslash;rer Allah, som ga meg denne maten og fors&oslash;rget meg med den uten noen kraft eller styrke fra min side.",
     "Sunan at-Tirmidhi, nr. 3458"),

    (25,
     "B&oslash;nn n&aring;r man g&aring;r ut av hjemmet",
     "Bismillah, tawakkaltu &lsquo;alallah, wa la hawla wa la quwwata illa billah.",
     "I Allahs navn, jeg setter min lit til Allah, og det er ingen makt eller styrke unntatt ved Allah.",
     "Sunan Abu Dawud, nr. 5095"),

    (27,
     "B&oslash;nn f&oslash;r s&oslash;vnen",
     "Bismika Allahumma amutu wa ahya.",
     "I Ditt navn, &aring; Allah, d&oslash;r jeg og lever jeg.",
     "Sahih al-Bukhari, nr. 6324"),

    (29,
     "B&oslash;nn n&aring;r man v&aring;kner",
     "Alhamdu lillahil-ladhi ahyana ba&lsquo;da ma amatana wa ilayhin-nushur.",
     "All lovprisning tilh&oslash;rer Allah, som ga oss liv etter &aring; ha latt oss d&oslash;, og til Ham er oppstandelsen.",
     "Sahih al-Bukhari, nr. 6312"),

    (31,
     "B&oslash;nn i n&oslash;d",
     "La ilaha illallahul-&lsquo;Adhimul-Halim. La ilaha illallahu Rabbul-&lsquo;Arshil-&lsquo;Adhim. La ilaha illallahu Rabbus-samawati wal-ardi wa Rabbul-&lsquo;Arshil-Karim.",
     "Det er ingen gud unntatt Allah, Den Allmektige, Den Milde. Det er ingen gud unntatt Allah, Herren over Den mektige tronen. Det er ingen gud unntatt Allah, Herren over himlene og jorden og Herren over Den edle tronen.",
     "Sahih al-Bukhari, nr. 6346"),

    (33,
     "B&oslash;nn om Allahs tilflukt",
     "Allahumma inni a&lsquo;udhu bi ridaka min sakhatika, wa bi mu&lsquo;afatika min &lsquo;uqubatika, wa a&lsquo;udhu bika minka, la uhsi thana&rsquo;an &lsquo;alayka, Anta kama athnayta &lsquo;ala nafsik.",
     "&Aring; Allah, jeg s&oslash;ker tilflukt i Ditt beh&aring;g fra Din vrede, og i Din tilgivelse fra Din straff, og jeg s&oslash;ker tilflukt hos Deg fra Deg. Jeg kan ikke prise Deg nok; Du er slik Du har priset Deg selv.",
     "Sahih Muslim, nr. 486"),

    (35,
     "Reiseb&oslash;nn",
     "Subhanal-ladhi sakhkhara lana hadha wa ma kunna lahu muqrinin, wa inna ila Rabbina lamunqalibun.",
     "&AElig;re v&aelig;re Den som underla oss dette, for vi kunne ikke ha klart det selv. Og sannelig, til v&aring;r Herre skal vi vende tilbake.",
     "Sahih Muslim, nr. 1342 &mdash; Koran 43:13&ndash;14"),

    (37,
     "Istikhara-b&oslash;nn (veiledning i valg)",
     "Allahumma inni astakhiruka bi &lsquo;ilmika, wa astaqdiruka bi qudratika, wa as&rsquo;aluka min fadlikal-&lsquo;adhim. Fa innaka taqdiru wa la aqdir, wa ta&lsquo;lamu wa la a&lsquo;lam, wa Anta &lsquo;Allamul-ghuyub.",
     "&Aring; Allah, jeg s&oslash;ker Ditt r&aring;d gjennom Din kunnskap, og jeg s&oslash;ker Din styrke gjennom Din allmakt, og jeg ber Deg om Din store gunst. For Du er i stand til og jeg er ikke, Du vet og jeg vet ikke, og Du er Kjenneren av det skjulte.",
     "Sahih al-Bukhari, nr. 1166"),

    (39,
     "Beskyttelse av barn",
     "U&lsquo;idhukuma bi kalimatillahit-tammati min kulli shaytanin wa hammah, wa min kulli &lsquo;aynin lammah.",
     "Jeg s&oslash;ker beskyttelse for dere i Allahs fullkomne ord mot enhver djevel og hvert giftig vesen, og mot ethvert ondt &oslash;ye.",
     "Sahih al-Bukhari, nr. 3371"),

    (41,
     "B&oslash;nn etter adhan",
     "Allahumma Rabba hadhihid-da&lsquo;watit-tammati was-salatil-qa&rsquo;imah, ati Muhammadanil-wasilata wal-fadilah, wab&lsquo;athhu maqaman mahmudanil-ladhi wa&lsquo;adtah.",
     "&Aring; Allah, Herre over dette fullkomne kallet og den forestående b&oslash;nnen, gi Muhammad al-Wasilah (den h&oslash;yeste plassen i Paradiset) og fortrinn, og opph&oslash;y ham til den lovpriste stillingen Du har lovet ham.",
     "Sahih al-Bukhari, nr. 614"),

    (43,
     "B&oslash;nn etter wudu (rituell vask)",
     "Ashhadu an la ilaha illallahu wahdahu la sharika lah, wa ashhadu anna Muhammadan &lsquo;abduhu wa rasuluh. Allahummaj&lsquo;alni minat-tawwabin, waj&lsquo;alni minal-mutatahhirin.",
     "Jeg vitner om at det ikke finnes noen gud unntatt Allah alene, uten partner, og at Muhammad er Hans tjener og budbærer. &Aring; Allah, gj&oslash;r meg blant dem som angrer, og gj&oslash;r meg blant dem som renser seg.",
     "Sahih Muslim, nr. 234"),

    (45,
     "B&oslash;nn n&aring;r man g&aring;r inn i moskeen",
     "Allahumma iftah li abwaba rahmatik.",
     "&Aring; Allah, &aring;pne for meg portene til Din barmhjertighet.",
     "Sahih Muslim, nr. 713"),

    (47,
     "B&oslash;nn n&aring;r man g&aring;r ut av moskeen",
     "Allahumma inni as&rsquo;aluka min fadlik.",
     "&Aring; Allah, jeg ber Deg om Din gunst.",
     "Sahih Muslim, nr. 713"),

    (49,
     "B&oslash;nn ved avslutning av en samling (kaffaratul-majlis)",
     "Subhanaka Allahumma wa bihamdika, ashhadu an la ilaha illa Anta, astaghfiruka wa atubu ilayk.",
     "&AElig;re v&aelig;re Deg, &aring; Allah, og all ros tilh&oslash;rer Deg. Jeg vitner om at det ikke finnes noen gud unntatt Deg. Jeg ber om Din tilgivelse og vender meg til Deg i anger.",
     "Sunan at-Tirmidhi, nr. 3433"),

    (51,
     "B&oslash;nn om det beste i begge verdener",
     "Rabbana atina fid-dunya hasanatan wa fil-akhirati hasanatan wa qina &lsquo;adhaban-nar.",
     "V&aring;r Herre, gi oss godt i denne verden og godt i det hinsidige, og beskytt oss mot ildens straff.",
     "Sahih al-Bukhari, nr. 4522 &mdash; Koran 2:201"),
]

def make_dua_html(title, trans, meaning, source):
    return (
        '<div class="dua-section">'
        f'<div class="dua-title">Ukens Dua &mdash; {title}</div>'
        f'<div class="dua-trans">&laquo;{trans}&raquo;</div>'
        f'<div class="dua-betyr">&laquo;{meaning}&raquo;</div>'
        f'<div class="dua-kilde">{source}</div>'
        '</div>'
    )

def process_file(week_start, title, trans, meaning, source):
    s = f"{week_start:02d}"
    e = f"{week_start+1:02d}"
    fname = f"uke-{s}-{e}.html"
    fpath = os.path.join(BASE, fname)

    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1) Add CSS if not already present
    if 'dua-section' not in content:
        content = content.replace(CSS_ANCHOR, CSS_ANCHOR + CSS_BLOCK)

    # 2) Add dua HTML before the footer
    dua_html = make_dua_html(title, trans, meaning, source)
    footer_marker = f'<div class="in-f">&#9790; Uke {s}'
    if 'dua-section"><div' not in content.split(footer_marker)[0].split('class="pg inn"')[-1]:
        # Only second occurrence matters if marker present in front page too - but
        # the footer class in-f only appears once. Insert before it.
        content = content.replace(footer_marker, dua_html + footer_marker, 1)

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  {fname} OK")

def process_master():
    """Add duas to the combined kalender-2027.html file."""
    master = os.path.join(os.path.dirname(__file__), '..', 'kalender-2027.html')
    with open(master, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1) Add CSS if not already present
    if 'dua-section' not in content:
        content = content.replace(CSS_ANCHOR, CSS_ANCHOR + CSS_BLOCK)

    # 2) Insert each dua before its footer marker
    for week_start, title, trans, meaning, source in DUAS:
        s = f"{week_start:02d}"
        dua_html = make_dua_html(title, trans, meaning, source)
        footer_marker = f'<div class="in-f">&#9790; Uke {s}'
        if footer_marker in content and 'dua-section' not in content.split(footer_marker)[0].split('class="pg inn"')[-1]:
            content = content.replace(footer_marker, dua_html + footer_marker, 1)

    with open(master, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  kalender-2027.html OK")

if __name__ == '__main__':
    for week_start, title, trans, meaning, source in DUAS:
        process_file(week_start, title, trans, meaning, source)
    process_master()
    print("Done — all files updated.")
