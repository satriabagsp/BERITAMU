from sentistrength_id.sentistrength_id import sentistrength

# Fungsi Sentiment Bahasa Indonesia
def sentiment(kalimat):
    # config
    config = dict()
    config["negation"] = True
    config["booster"] = True
    config["ungkapan"] = True
    config["consecutive"] = True
    config["repeated"] = True
    config["emoticon"] = True
    config["question"] = True
    config["exclamation"] = True
    config["punctuation"] = True
    senti = sentistrength(config)

    sentimen = senti.main(kalimat)
    return(sentimen['kelas'])