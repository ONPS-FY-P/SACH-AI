"""Prepare reference passages without inventing section boundaries.
Run: python prepare_data.py [optional/path/to/raw/jsons]
The combined file duplicates individual Acts and is deliberately omitted.
"""
import pathlib,json,re,sys
root=pathlib.Path(__file__).resolve().parent
src=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else root/'data/raw'
names={
 'a202345.json':'Bharatiya Nyaya Sanhita, 2023',
 'constitution_full_dataset.json':'Constitution of India',
 'the prevention of coruption act 1988.json':'Prevention of Corruption Act, 1988',
 'the_bharatiya_sakshya_adhiyanayam_2023.json':'Bharatiya Sakshya Adhiniyam, 2023',
 'THE_CONSUMER_PROTECTION_ACT_2019.json':'Consumer Protection Act, 2019',
 'THE_ENVIRONMENT.json':'Environment (Protection) Act, 1986',
 'THE_INFORMATION_TECHNOLOGY_ACT_2000.json':'Information Technology Act, 2000',
 'THE_JUVENILE_JUSTICE_(CARE_AND_PROTECTION_OF_CHILDREN)_ACT_2015.json':'Juvenile Justice Act, 2015',
 'The_Motor_Vehicles_Act_1988.json':'Motor Vehicles Act, 1988',
 'THE_PROTECTION_OF_CHILDREN_FROM_SEXUAL_OFFENCES_ACT_2012.json':'Protection of Children from Sexual Offences Act, 2012',
 'THE_PROTECTION_OF_WOMEN_FROM_DOMESTIC_VIOLENCE_ACT_2005.json':'Protection of Women from Domestic Violence Act, 2005'}
rows=[];manifest=[]
for name,title in names.items():
 data=json.loads((src/name).read_text(encoding='utf-8'));count=0
 for record in data:
  text=record.get('text','').strip()
  if not text:continue
  label=title
  if record.get('article_number'):label+=' · Article '+str(record['article_number'])
  elif len(data) > 1 and record.get('section'):label+=' · Section '+str(record['section'])
  words=text.split(); chunks=[words[i:i+360] for i in range(0,len(words),300)]
  for chunk in chunks:
   if not chunk:continue
   rows.append({'id':f'S{len(rows)+1}','title':label,'text':' '.join(chunk),'file':name});count+=1
 manifest.append({'file':name,'title':title,'records':len(data),'passages':count})
(root/'data').mkdir(exist_ok=True)
(root/'data/legal-corpus.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
(root/'data/corpus-manifest.json').write_text(json.dumps({'documents':manifest,'passages':len(rows),'limitations':['Dates and legal amendments are not independently verified.','Whole-Act inputs are windowed, not section-parsed.','BNSS was not supplied as a distinct Act.','all_acts_combined.json is excluded to avoid duplicate indexing.']},indent=2),encoding='utf-8')
print(f'Prepared {len(rows)} passages from {len(names)} distinct legal documents.')
