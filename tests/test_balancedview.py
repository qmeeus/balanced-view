from app.api.balancedview_api import run
from pprint import pprint


texts = ["""
    Everybody agrees that ObamaCare doesn’t work. Premiums & deductibles are far too high - Really bad HealthCare! Even the Dems want to replace it, but with Medicare for all, which would cause 180 million Americans to lose their beloved private health insurance. The Republicans are developing a really great HealthCare Plan with far lower premiums (cost) & deductibles than ObamaCare. In other words it will be far less expensive & much more usable than ObamaCare. Vote will be taken right after the
    Election when Republicans hold the Senate & win back the House. It will be truly great HealthCare that will work for America. Also, Republicans will always support Pre-Existing Conditions. The Republican Party will be known as the Party of Great HealtCare. Meantime, the USA is doing better than ever & is respected again!""",

    """
    The Democrats today killed a Bill that would have provided great relief to Farmers and yet more money to Puerto Rico despite the fact that Puerto Rico has already been scheduled to receive more hurricane relief funding than any “place” in history. The people of Puerto Rico are GREAT, but the politicians are incompetent or corrupt. Puerto Rico got far more money than Texas & Florida combined, yet their government can’t do anything right, the place is a mess - nothing works. FEMA & the Military
    worked emergency miracles, but politicians like the crazed and incompetent Mayor of San Juan have done such a poor job  of bringing the Island back to health. 91 Billion Dollars to Puerto Rico, and now the Dems want to give them more, taking dollars away from our Farmers and so many others. Disgraceful!""",

    """
    Mexico must use its very strong immigration laws to stop the many thousands of people trying to get into the USA. Our detention areas are maxed out & we will take no more illegals. Next step is to close the Border! This will also help us with stopping the Drug flow from Mexico!""",

    """
    In a letter to me sent by Kim Jong Un, he stated, very nicely, that he would like to meet and start negotiations as soon as the joint U.S./South Korea joint exercise are over. It was a long letter, much of it complaining about the ridiculous and expensive exercises. It was also a small apology for testing the short range missiles, and that this testing would stop when the exercises end. I look forward to seeing Kim Jong Un in the not too distant future! A nuclear free North Korea will lead to one of the most successful countries in the world!""",
    """Bazinga!"""
]

for text in texts:
    params = {"text": text, "language": "en"}
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

