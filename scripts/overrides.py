# Hand-read overrides. Every entry quotes the printed key page (proof/<lvl>-key-NN.png) and the student-book page (proof/book-*.png, m*.png).
def c(lab,q,opts,ans): return ('C',lab,q,opts,ans)
def t(lab,q,acc): return ('T',lab,q,acc if isinstance(acc,list) else [acc])
def d(lab,q): return ('D',lab,q)
CW='Choose the correct form.'
PATCH={
 # bas-key-19 Section 2 Warm-Up 1 + book p.176: "divide subject and verb with a slash"
 ('bas-rc-p4-s02','Warm-Up','1-(a)'):[t('1-(a)','Put a slash (/) between the subject and the verb: David and Diane love movies.',['David and Diane / love movies.','David and Diane/love movies.','David and Diane / love movies'])],
 ('bas-rc-p4-s02','Warm-Up','1-(b)'):[t('1-(b)','Put a slash (/) between the subject and the verb: You and I learn English at school.',['You and I / learn English at school.','You and I/learn English at school.','You and I / learn English at school'])],
 # bas-key-19 GP1 "(a) window / 창문을 (b) fly / 난다 (c) He / 그는"; book p.178: find the English word for the blank
 ('bas-rc-p4-s02','Grammar Practice','1-(a)'):[t('1-(a)','She closed the window last night. Type the English word that matches the blank in the Korean translation.','window')],
 ('bas-rc-p4-s02','Grammar Practice','1-(b)'):[t('1-(b)','Birds fly in the sky. Type the English word that matches the blank in the Korean translation.','fly'),t('1-(c)','He can play the piano. Type the English word that matches the blank in the Korean translation.','He')],
 # GP2 "(a) 동사 (b) 목적어 (c) 주어" -> English grammar labels
 ('bas-rc-p4-s02','Grammar Practice 2-(a): type the answer (see the book page).','2-(a)'):[c('2-(a)','He stopped crying. What is the underlined word (stopped)?',['subject','verb','object','complement'],'verb')],
 ('bas-rc-p4-s02','Grammar Practice 2-(b): type the answer (see the book page).','2-(b)'):[c('2-(b)','Did you eat the ice cream? What is the underlined part (ice cream)?',['subject','verb','object','complement'],'object')],
 ('bas-rc-p4-s02','Grammar Practice 2-(c): type the answer (see the book page).','2-(c)'):[c('2-(c)','I watched a movie last night. What is the underlined word (I)?',['subject','verb','object','complement'],'subject')],
 # bas-key-19 S3 GP4 "(a) tooth-tooths (b) knife-knifes (c) foot-foots"; book p.189: choose the WRONG singular-plural pair
 ('bas-rc-p4-s03','Grammar Practice','4-(a)'):[c('4-(a)','Choose the wrong singular-plural pair.',['salmon - salmon','fish - fish','tooth - tooths'],'tooth - tooths')],
 ('bas-rc-p4-s03','Grammar Practice','4-(b)'):[c('4-(b)','Choose the wrong singular-plural pair.',['ox - oxen','knife - knifes','brush - brushes'],'knife - knifes')],
 ('bas-rc-p4-s03','Grammar Practice','4-(c)'):[c('4-(c)','Choose the wrong singular-plural pair.',['man - men','foot - foots','potato - potatoes'],'foot - foots')],
 # bas-key-19 S4 GP3 English part; Korean translation half is display-only. Book p.198
 ('bas-rc-p4-s04','Grammar Practice','3-(a)'):[t('3-(a)','Jane buys shoes. Change it to the past tense.','Jane bought shoes.')],
 ('bas-rc-p4-s04','Grammar Practice','3-(b)'):[t('3-(b)','Jane buys shoes. Change it to the present progressive.','Jane is buying shoes.')],
 ('bas-rc-p4-s04','Grammar Practice','3-(c)'):[t('3-(c)','Jane buys shoes. Change it to the present negative.','Jane does not buy shoes.'),d('3-trans','Translate (a)-(c) into Korean in your notebook (see the book page). Not scored.')],
 # bas-key-23 S7 Warm-Up 1 "Check-in"
 ('bas-rc-p5-s07','Warm-Up 1-','1-'):[t('1','Warm-Up 1: type the answer (see the book page).','Check-in')],
 # int-key-27 S1 Warm-Up 4 Korean meaning of underlined parts; book p.9 sources
 ('int-rc-p4-s01','Warm-Up 4-(a): type the answer (see the book page).','4-(a)'):[d('4-(a)','My father and mother are at table. Say the meaning of the underlined part in Korean (see the book page). Not scored.')],
 ('int-rc-p4-s01','Warm-Up 4-(b): type the answer (see the book page).','4-(b)'):[d('4-(b)','He wants to be a Newton. Say the meaning in Korean (see the book page). Not scored.'),d('4-(c)','A dog is a faithful animal. Say the meaning in Korean (see the book page). Not scored.')],
 ('int-rc-p4-s01','Warm-Up 4-(d): type the answer (see the book page).','4-(d)'):[d('4-(d)','I usually go to bed at 10:00 p.m. Say the meaning in Korean (see the book page). Not scored.')],
 # int-key-27 S2 Warm-Up 1 "1. (d)"
 ('int-rc-p4-s02','Warm-Up','1-(d)'):[c('1','Warm-Up 1: choose the answer (see the book page).',['(a)','(b)','(c)','(d)'],'(d)')],
 ('int-rc-p4-s02','Warm-Up 3-(a): type the answer (see the book page).','3-(a)'):[d('3-(a)','Can you solve the problem? Translate into Korean (see the book page). Not scored.')],
 ('int-rc-p4-s02','Warm-Up 3-(b): type the answer (see the book page).','3-(b)'):[d('3-(b)','She may be a spy. Translate into Korean. Not scored.')],
 ('int-rc-p4-s02','Warm-Up 3-(c): type the answer (see the book page).','3-(c)'):[d('3-(c)','We must arrive at the hotel before 7 p.m. Translate into Korean. Not scored.')],
 ('int-rc-p4-s02','Warm-Up 3-(d): type the answer (see the book page).','3-(d)'):[d('3-(d)','He must be tired. Translate into Korean. Not scored.')],
 # int-key-27 S4 WU3 "(c) expensively -> expensive"
 ('int-rc-p4-s04','Warm-Up','3-(c)'):[t('3-(c)','Correct the wrong word (see the book page).','expensive')],
 # int-key-28 S5 WU2 / WU4
 ('int-rc-p4-s05','Warm-Up','2-(a)'):[t('2-(a)','Write the comparative and superlative forms (see the book page).',['more - most / more - most','more most / more most','more, most / more, most'])],
 ('int-rc-p4-s05','Warm-Up','2-(c)'):[t('2-(b)','Write the comparative and superlative forms (see the book page).',['better - best / better - best','better best / better best','better, best / better, best']),t('2-(c)','Write the comparative and superlative forms (see the book page).',['worse - worst / worse - worst','worse worst / worse worst','worse, worst / worse, worst'])],
 ('int-rc-p4-s05','Warm-Up 4-(a): type the answer (see the book page).','4-(a)'):[d('4-(a)','Tom runs faster than his friend, James. Translate into Korean. Not scored.')],
 ('int-rc-p4-s05','Warm-Up 4-(b): type the answer (see the book page).','4-(b)'):[d('4-(b)','John is more famous than David. Translate into Korean. Not scored.'),d('4-(c)',"Alice's car is more expensive than Cathy's car. Translate into Korean. Not scored.")],
 ('int-rc-p4-s05','Warm-Up 4-(d): type the answer (see the book page).','4-(d)'):[d('4-(d)','Rita is the most beautiful girl in her class. Translate into Korean. Not scored.')],
 # int-key-28 S8 VP3 "(d) scuba diving / dangerous"
 ('int-rc-p4-s08','Vocabulary Practice','3-(d)'):[t('3-(d)','Fill in both blanks (see the book page).',['scuba diving / dangerous','scuba diving, dangerous','scuba diving dangerous'])],
 # adv-key-31 S1 GP; book p.164
 ('adv-rc-p4-s01','Grammar Practice','1-'):[c('1-(a)','I like (play / playing) soccer with my friends every day.',['play','playing'],'playing'),c('1-(b)','I ask them (come / to come / coming) to the playground as soon as the class is over.',['come','to come','coming'],'to come'),c('1-(c)','After (finish / to finish / finishing) the game, we go to the shower room.',['finish','to finish','finishing'],'finishing'),c('1-(d)','(take / to take / taking) showers.',['take','to take','taking'],'to take')],
 ('adv-rc-p4-s01','Grammar Practice','3-(d)'):[c('3','Choose the correct sentence.',['It is wise for you to say like that.','He has finished do his homework.','The doctor made her to stay at home for the time being.','It is necessary for him to prepare for the test.'],'It is necessary for him to prepare for the test.')],
 ('adv-rc-p4-s01','Grammar Practice 4-(a): type the answer (see the book page).','4-(a)'):[c('4-(a)','I have something to give you. Which use of the to-infinitive?',['noun use','adjective use','adverb use'],'adjective use')],
 ('adv-rc-p4-s01','Grammar Practice 4-(b): type the answer (see the book page).','4-(b)'):[c('4-(b)','My wish is to become a president. Which use of the to-infinitive?',['noun use','adjective use','adverb use'],'noun use'),c('4-(c)','I will go to America to study English. Which use of the to-infinitive?',['noun use','adjective use','adverb use'],'adverb use')],
 ('adv-rc-p4-s01','Grammar Practice 4-(d): type the answer (see the book page).','4-(d)'):[c('4-(d)','You must be very happy to see your father again. Which use of the to-infinitive?',['noun use','adjective use','adverb use'],'adverb use')],
 # adv-key-31 S2 GP1 "(1)" / GP2 "(d) / boring -> bored"; book p.174
 ('adv-rc-p4-s02','Grammar Practice','1-1)'):[c('1','Choose the set of participles that fits blanks (a)-(d).',['(1) interesting - interested - surprising - surprised','(2) interested - interesting - surprising - surprised','(3) interesting - interested - surprised - surprising','(4) interested - interesting - surprised - surprising'],'(1) interesting - interested - surprising - surprised')],
 ('adv-rc-p4-s02','Grammar Practice','2-(d)'):[c('2','Choose the awkward sentence.',['I was very tired when you called me last night.','The movie was really boring.',"Why don't we do something exciting?",'I am boring. I want to play computer games.'],'I am boring. I want to play computer games.'),t('2-fix','Correct the wrong word in the awkward sentence.','bored')],
 # adv-key-31 S3 GP1 Korean translations; book p.170 sources
 ('adv-rc-p4-s03','Grammar Practice 1-(a): type the answer (see the book page).','1-(a)'):[d('1-(a)','The rich are not always happy. Translate into Korean. Not scored.')],
 ('adv-rc-p4-s03','Grammar Practice 1-(b): type the answer (see the book page).','1-(b)'):[d('1-(b)','The deceased is said to have lived for his country. Translate into Korean. Not scored.'),d('1-(c)','One fifth of the class wants to take a trip to Hawaii. Translate into Korean. Not scored.')],
 ('adv-rc-p4-s03','Grammar Practice 1-(d): type the answer (see the book page).','1-(d)'):[d('1-(d)','My family is a large one. Translate into Korean. Not scored.')],
}
for k,(src) in {'a':'They are not only cheap but also useful.','b':'Get up now or you will miss the train.','c':'Many people insist that he be a spy from another country.','d':'Neither my father nor my uncle knows the secret.'}.items():
    PATCH[('adv-rc-p4-s04',f'Warm-Up 4-({k}): type the answer (see the book page).',f'4-({k})')]=[d(f'4-({k})',src+' Translate into Korean. Not scored.')]
# Whole-block rebuilds from key images (PDF text layer scrambled)
OVR={
 ('int-rc-p4-s02','gp'):[t('1-(a)','Correct the wrong part (see the book page).','will'),t('1-(b)','Correct the wrong part.','will be'),t('1-(c)','Correct the wrong part.','play'),t('1-(d)','Correct the wrong part.','be'),
   c('2-(a)','People (should / may) drive their car carefully when it snows.',['should','may'],'should'),c('2-(b)','Who broke the window? My sister (will / did).',['will','did'],'did'),c('2-(c)','May I come in? Yes, you may. But you (must / can) be quiet.',['must','can'],'must'),
   c('3','Choose the wrong sentence.',['We should be polite to other people.','She must be an English teacher.','John should be the dishes this evening.','He may be late for school tomorrow.'],'John should be the dishes this evening.'),t('3-fix','Correct the wrong part of that sentence.','should do'),
   c('4','Grammar Practice 4: choose the answer (see the book page).',['(a)','(b)','(c)','(d)'],'(a)')],
 ('int-rc-p4-s03','words-checkup'):[('BANK',['president','ghost','auditorium','coin'],['(a)','(b)','(c)','(d)'])],
 ('int-rc-p4-s03','gp'):[t('1-(a)','Write 5,462 in words.',['five thousand four hundred sixty-two','five thousand four hundred sixty two','five thousand four hundred and sixty-two']),t('1-(b)','Write 3/5 in words.','three fifths'),t('1-(c)','Write 2.47 in words.','two point four seven'),t('1-(d)','Write 2007 (the year) in words.','two thousand seven'),t('1-(e)','Write the date in words (see the book page).','November twentieth'),t('1-(f)','Write 243-5908 in words.','two four three five nine zero eight'),t('1-(g)','Write $5.41 in words.',['five dollars forty one cents','five dollars forty-one cents']),
   t('2-(a)','Combine: This is a truck. This truck is big.','This is a big truck.'),t('2-(b)','Combine: That building is a police station. That police station is old.','That police station building is old.'),
   t('3-(a)','Fill in the blank (see the book page).','a little'),t('3-(b)','Fill in the blank.','little'),t('3-(c)','Fill in the blank.','Every'),t('3-(d)','Fill in the blank.','many'),
   t('4-(a)','Fill in the blank (see the book page).','busy'),t('4-(b)','Fill in the blank.','kind'),t('4-(c)','Fill in the blank.','delicious')],
 ('adv-rc-p4-s01','warmup'):[c('1-(a)','We went to the station (see / to see) him off.',['see','to see'],'to see'),c('1-(b)','Thank you for (visiting / to visit) my Web site.',['visiting','to visit'],'visiting'),c('1-(c)','He is used to (get / getting) up early.',['get','getting'],'getting'),c('1-(d)','She wants (meet / to meet) your teacher in person.',['meet','to meet'],'to meet'),
   t('2-(a)',"I don't know ____. (see the book page)",'what to wear'),t('2-(b)','Do you know ____ the engine?','how to start'),t('2-(c)','Please tell me ____ for Seoul.','when to leave'),t('2-(d)','They will decide ____ next Friday.','where to meet'),
   c('3-(a)','I will let you (go / to go / going) if you want to.',['go','to go','going'],'go'),c('3-(b)','She expected me (do / to do / doing) a better job.',['do','to do','doing'],'to do'),c('3-(c)','She made me (work / to work / working) all day long.',['work','to work','working'],'work'),c('3-(d)','Thank you for (help / to help / helping) me with my work.',['help','to help','helping'],'helping')],
 ('adv-rc-p4-s04','gp'):[t('1-(a)','Catch me ____ you can!','if'),t('1-(b)','I must be going now ____ it is getting darker.','because'),t('1-(c)','I wonder ____ you are for it or against it.','if'),t('1-(d)','____ young, he is respected by many people.','Although'),
   t('2-(a)',"He can't come into the toy house ____ he is too tall.",'since'),t('2-(b)','I have been learning English ____ we moved to Seoul.','since'),t('2-(c)','Poor ____ he is, he is generous.','as'),t('2-(d)','____ I look back on, he is a man of great help.','as'),
   t('3-(a)','This is the day ____ we make a contract.','when'),t('3-(b)','This is the hall ____ the concert will be on.','where'),t('3-(c)','She bites her finger nails ____ she becomes nervous.','when'),t('3-(d)','This is the toy ____ my father gave me on my birthday.',['which','that']),
   t('4-(a)','Fill in the blank (see the book page).','In case of'),t('4-(b)','Fill in the blank.','If'),t('4-(c)','Fill in the blank.','While'),t('4-(d)','Fill in the blank.','If'),
   t('5-(a)','Rewrite the sentence (see the book page).','Because of the heavy snow, we had to stay at home.'),t('5-(b)','Rewrite the sentence.','After you finish your homework, you may get out.'),t('5-(c)','Rewrite the sentence.','When she was 18, she moved to Seoul.'),t('5-(d)','Rewrite the sentence.','If you find the person, please call me.')],
 ('adv-rc-p4-s05','words-checkup'):[('BANK',['keep an eye on','think about','fill out','take pictures'],['(a)','(b)','(c)','(d)'])],
 ('adv-rc-p4-s05','warmup'):[c('1','Choose the correct sentence.',['They traveled 1,300 kilometers on bike.','We will be home in Friday morning.','She was disappointed with her exam results.','The letter was full with mistakes.'],'She was disappointed with her exam results.'),
   t('1-(a)','Correct the wrong word: They traveled 1,300 kilometers on bike.','by'),t('1-(b)','Correct the wrong word: We will be home in Friday morning.','on'),t('1-(d)','Correct the wrong word: The letter was full with mistakes.','of'),
   t('2-(a)','He has lived ____ the city ____ ten years.',['in / for','in for','in, for']),t('2-(b)','I am going to meet him ____ noon ____ Sunday.',['at / on','at on','at, on']),t('2-(c)','Bob walked ____ an hour.','for'),t('2-(d)','I was born ____ (see the book page).','in'),
   t('3-(a)','We will go to Jeju island ____ plane.','by'),t('3-(b)','You must come back ____ 4 p.m.','by'),t('3-(c)','I had to wait for my teacher ____ three hours.','for'),t('3-(d)','I bought a toy ____ my son.','for')],
 ('adv-rc-p4-s05','gp'):[t('1-(a)','He sat ____ Sally and me.','between'),t('1-(b)','He went to school ____ taxi.','by'),t('1-(c)','The river runs ____ the bridge.','under'),t('1-(d)','We play soccer together ____ Thursdays.','on'),
   c('2','Grammar Practice 2: choose the answer (see the book page).',['(a)','(b)','(c)','(d)'],'(d)'),t('2-(d)','Grammar Practice 2: type the word for (d) (see the book page).','In'),
   c('3-(a)','Everyone must come back (by / until) 4 p.m.',['by','until'],'by'),c('3-(b)','We will have a vacation (by / until) the end of this month.',['by','until'],'until'),c('3-(c)','They work (from / since) 8 a.m. to 6 p.m.',['from','since'],'from'),c('3-(d)','They have known each other (from / since) they were children.',['from','since'],'since'),
   c('4-(a)','I slept (for / from) seven hours.',['for','from'],'for'),c('4-(b)','He helped the poor (with / during) the war.',['with','during'],'during'),c('4-(c)','You should return it (within / before) two hours.',['within','before'],'within'),c('4-(d)',"Let's meet (by / after) school.",['by','after'],'after')],
 # adv-key-35 Part V S3 W&I printed "(a) situation (b) violence (b) amount" - third entry printed with a repeated (b) label; it is the third blank (c)
 ('adv-rc-p5-s03','words-checkup'):[('BANK',['situation','violence','amount'],['(a)','(b)','(c)'])],
}
# int-key-28 S4 GP3(b) / GP4 "We watch often movies at home. (watch often -> often watch)"
PATCH[('int-rc-p4-s04','Grammar Practice','3-(b)')]=[t('3-(b)','Rewrite the sentence (see the book page).','I will go to the cinema with my friends next Wednesday.')]
PATCH[('int-rc-p4-s04','Grammar Practice','4-')]=[t('4','Correct the word order: We watch often movies at home.','We often watch movies at home.')]
# adv-key-28 Part III S5 W&I "(e) illegal"
