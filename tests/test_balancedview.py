from app.api.balancedview_api import run
from pprint import pprint


texts = [

    """Everybody agrees that ObamaCare doesn’t work. Premiums & deductibles are far too high - Really bad HealthCare! Even the Dems want to replace it, but with Medicare for all, which would cause 180 million Americans to lose their beloved private health insurance. The Republicans are developing a really great HealthCare Plan with far lower premiums (cost) & deductibles than ObamaCare. In other words it will be far less expensive & much more usable than ObamaCare. Vote will be taken right after the
    Election when Republicans hold the Senate & win back the House. It will be truly great HealthCare that will work for America. Also, Republicans will always support Pre-Existing Conditions. The Republican Party will be known as the Party of Great HealtCare. Meantime, the USA is doing better than ever & is respected again!""",

    """
    The Democrats today killed a Bill that would have provided great relief to Farmers and yet more money to Puerto Rico despite the fact that Puerto Rico has already been scheduled to receive more hurricane relief funding than any “place” in history. The people of Puerto Rico are GREAT, but the politicians are incompetent or corrupt. Puerto Rico got far more money than Texas & Florida combined, yet their government can’t do anything right, the place is a mess - nothing works. FEMA & the Military
    worked emergency miracles, but politicians like the crazed and incompetent Mayor of San Juan have done such a poor job  of bringing the Island back to health. 91 Billion Dollars to Puerto Rico, and now the Dems want to give them more, taking dollars away from our Farmers and so many others. Disgraceful!""",

    """
    Mexico must use its very strong immigration laws to stop the many thousands of people trying to get into the USA. Our detention areas are maxed out & we will take no more illegals. Next step is to close the Border! This will also help us with stopping the Drug flow from Mexico!""",

    """
    In a letter to me sent by Kim Jong Un, he stated, very nicely, that he would like to meet and start negotiations as soon as the joint U.S./South Korea joint exercise are over. It was a long letter, much of it complaining about the ridiculous and expensive exercises. It was also a small apology for testing the short range missiles, and that this testing would stop when the exercises end. I look forward to seeing Kim Jong Un in the not too distant future! A nuclear free North Korea will lead to one of the most successful countries in the world!""",
    """Bazinga!""",
    """Ongeveer een week geleden, de vele dode vogels die spontaan dood neervielen in een park in Den Haag waarvan iedereen hoopte dat dit misschien een éénmalig incident zou zijn. Helaas….
    Blijkt nu dat er weer een groot aantal dode spreeuwen zijn gevonden:
    Een week na de laatste massale spreeuwensterfte in het Huijgenspark in Den Haag zijn er opnieuw tientallen dode spreeuwen gevonden. De Dierenambulance spreekt over zeker 150 nieuwe vogellijkjes. Daarmee komt het dodental op 297.
    Ook nu weer hetzelfde verhaal: niemand heeft enig idee wat de oorzaak kan zijn van deze plotselinge vogelsterfte. Totdat je gaat kijken wat er gebeurde vorige week toen die vogels dood neervielen.
    Op de hoek hoefkade staat op het dak van HS telecenter een nieuwe 5G mast , laag op het dak niet zichtbaar. Er werd een test gedaan, dit ivm met het station Hollands spoor om te kijken hoe groot het bereik was en of er geen nadelige apparatuur schade zou ontstaan op en rond het station
    Meteen erna vielen de vogels massaal dood uit de bomen. En de eenden die zwommen op het zieke / van maanenkade en pletterijkade schenen ook heel raar te reageren heb ik gehoord. Alsof ze ineens simultaan hun kop onderwater deden om aan de straling te ontsnappen en sommige wilde wegvliegen en storten neer op straat of in de gracht.
    Vrijwel op hetzelfde moment dat die dieren dood neervallen, wordt in de buurt van station Holland Spoor getest met een 5G zendmast.""",
    """Zaak-Epstein: Amerikaanse Justitie richt pijlen nu op Epsteins medewerkers
    De dood van Jeffrey Epstein, de van misbruik verdachte Amerikaanse miljardair die afgelopen weekend zelfmoord pleegde in zijn cel, betekent niet het einde van het onderzoek. Justitie belooft nu haar pijlen te richten op mogelijke medeplichtingen. Ook is een grondig onderzoek bevolen naar de zelfdoding van Epstein. Minister van Justitie William Barr zegt dat er "ernstige onregelmatigheden" zijn gebeurd in de gevangenis.""",
    """Crise à Hong Kong: l’aéroport annule tous les vols au départ
    Les militants affluaient mardi après-midi à l’aéroport quelques heures à peine après que la cheffe de l’exécutif hongkongais pro-Pékin, Carrie Lam a mis en garde que leurs manifestations poussaient la ville sur « un chemin sans retour ».
     Les autorités aéroportuaires de Hong Kong ont annulé tous les vols au départ de l’aéroport international ce mardi après que des manifestants pro-démocratie ont bloqué les terminaux pour la deuxième fois en deux jours, mais des vols continuaient d’atterrir et de décoller en fin d’après-midi.
    «Les opérations aux terminaux de l’aéroport international de Hong Kong ont été sérieusement perturbées en raison d’un rassemblement public», ont indiqué les autorités aéroportuaires dans un communiqué.
    Les contestataires ont obstrué les allées menant aux zones d’embarquement des deux terminaux, mais des dizaines de passagers sont néanmoins parvenus à passer.
    «Je soutiens votre cause (...) mais je dois aller voir ma famille», criait un homme entouré de manifestants vêtus de noir -la couleur emblématique du mouvement- qui l’empêchaient d’atteindre les contrôles de sécurité menant à la zone internationale.""",
    """Putins Wunderwaffe fällt ins Wasser
    Donald Trump stichelt, Russland trauert: Fünf Tage nach dem rätselhaften atomaren Unfall auf einem Testgelände am Weißen Meer kommen langsam neue Details ans Licht.
    Wer den Schaden hat, braucht für den Spott nicht zu sorgen. Fünf Tage nach der Explosion einer russischen Rakete auf einem Militärgelände am Weißen Meer hat US-Präsident Donald Trump den Vorfall auf Twitter kommentiert - in seiner typischen Mischung aus Stichelei und Auftrumpfen. "Die Vereinigten Staaten lernen viel aus der Explosion", schrieb er am Montag. Man habe nämlich eine "ähnliche, aber weiter fortgeschrittene Technik". Und dann lässt er einen Namen fallen: "Die russische 'Skyfall'-Explosion lässt Leute um die Luftqualität am Ort und weit darüber hinaus bangen. Nicht gut!"""
]

for text in texts:
    params = {"text": text}
    response = run(params)
    print("Graph:")
    if "error" in response["graph"]:
        print(response["graph"]["error"]["text"])
    else:
        print("{} nodes, {} edges".format(len(response["graph"]["nodes"]), len(response["graph"]["links"])))
    print("Articles:")
    if "error" in response["articles"]:
        print(response["articles"]["error"]["text"])
    else:
        print("; ".join([
            "{}: {}".format(orientation, str(len(articles))) for orientation, articles in response["articles"].items()]))

