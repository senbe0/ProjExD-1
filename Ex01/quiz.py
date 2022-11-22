from random import randint
import datetime

def shutudai():
    num = randint(0,2)
    print(num)
    quiz_text = ["サザエの旦那の名前は？", "カツオの妹の名前は？", "タラオとカツオから見てどんな関係？"]
    quiz_ans = [["マスオ", "ますお"], ["ワカメ", "わかめ"], ["甥", "おい", "甥っ子", "おいっこ"]]
    print("問題："+ quiz_text[num])
    return quiz_ans[num]

def kaito(re_ans):
    st=datetime.datetime.now()
    us_ans = input("答えるんだ：")
    ed = datetime.datetime.now()
    print((ed-st).seconds)
    if us_ans in re_ans:
        ans_ms = "正解!!!"
    else:
        ans_ms = "出直してこい"
    return ans_ms

if __name__=="__mian__":
    re_ans = shutudai()
    print( kaito(re_ans))