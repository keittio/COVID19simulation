text = open("Parameterfile.txt","w")
for aaa in range(6):
    sep = (aaa + 1) * 5
    ali = 0
    for bbb in range(1):
        #ali = (bbb + 1) * 10
        ali = 30
        coh = 0
        for ccc in range(1):
            #coh = (ccc + 1) * 17
            coh = 50
            prob = 0
            for ddd in range(3):
                if ddd == 0:
                    prob = 66 #マスクなし→マスクあり
                elif ddd == 1:
                    prob = 33 #マスクなし→マスクあり
                elif ddd == 2:
                    prob = 16 #マスクあり→マスクなし
                rad = 0
                for eee in range(3):
                    if eee == 0:
                        rad = 8 #会話
                    elif eee == 1:
                        rad = 25 #咳
                    elif eee == 2:
                        rad = 42 #くしゃみ

                    text.write(str(sep) + '\n')
                    text.write(str(ali) + '\n')
                    text.write(str(coh) + '\n')
                    text.write(str(prob) + '\n')
                    text.write(str(rad) + '\n')
text.close()

#マスク付けると79%感染確立が減る
#ふつうは70%