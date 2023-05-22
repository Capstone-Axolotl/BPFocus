from sqlalchemy import text

df={}

df['one']=100
df['two']=5678

df['one']=df['one']/256*100

string=(text("""update :one, :two"""), df)

print(string)
