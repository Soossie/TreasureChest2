-- Treasure_chest-tietokannan luominen

-- poista taulut, jos olemassa (tässä järjestyksessä)
DROP TABLE IF EXISTS rewards;
DROP TABLE IF EXISTS game_airports;
DROP TABLE IF EXISTS wise_man_questions;
DROP TABLE IF EXISTS game;
DROP TABLE IF EXISTS difficulty;

-- poista country-taulusta sarake capital, jos olemassa
ALTER TABLE IF EXISTS country DROP COLUMN IF EXISTS capital;

-- lisätään viiteavain airport-taulusta country-tauluun
alter table airport add foreign key(iso_country) references country(iso_country);

-- lisätään country-tauluun capital-sarake
alter table country add capital varchar(40);

-- luodaan tietokannan taulut

CREATE table wise_man_questions(
id int not null auto_increment,
question varchar(100),
answer varchar(40),
primary key (id)
);

CREATE table difficulty(
level varchar(40) not null,
country_count int,
airports_in_treasure_land int,
wise_man_count int,
starting_money int,
wise_man_cost int,
wise_man_reward int,
primary key (level)
);

CREATE table rewards(
id int not null auto_increment,
name varchar(40),
difficulty_level varchar(40),
primary key (id),
foreign key(difficulty_level) REFERENCES difficulty(level)
);

CREATE table game(
id int not null auto_increment,
screen_name varchar(40),
money int,
home_airport varchar(40),
location varchar(40),
difficulty_level varchar(40),
primary key (id),
foreign key (location) REFERENCES airport(ident),
foreign key (difficulty_level) REFERENCES difficulty(level)
);

CREATE table game_airports(
id int not null auto_increment,
game_id int,
airport_ident varchar(40),
wise_man_question_id int,
answered int,
has_treasure int,
is_default_airport int,
primary key (id),
foreign key (game_id) REFERENCES game(id),
foreign key (wise_man_question_id) REFERENCES wise_man_questions(id)
);

-- lisätään dataa difficulty-tauluun
insert into difficulty(level, country_count, airports_in_treasure_land, wise_man_count, starting_money, wise_man_cost, wise_man_reward)
values ('easy', 10, 10, 4, 1500, 100, 200),
('normal', 20, 20, 8, 3000, 200, 500),
('hard', 30, 40, 16, 5000, 400, 1000);

-- lisätään dataa rewards-tauluun
insert into rewards(name, difficulty_level)
values ('gold ring', 'easy'), ('magic carpet', 'easy'), ('silver tiara', 'easy'),
('gold bar', 'normal'), ('magic wand', 'normal'), ('diamond crown', 'normal'),
('world peace', 'hard'), ('time machine', 'hard'), ('diamond collection', 'hard');

-- lisätään dataa (kysymykset, vastaukset) wise_man_questions-tauluun
insert into wise_man_questions(question, answer)
values('What is the capital of France? a) London b) Paris c) San Marino', 'b'),
('What is the capital of Portugal? a) Skopje b) Valletta c) Lisbon', 'c'),
('What is the capital of Serbia? a)  Helsinki b) Belgrade c) Ljubljana', 'b'),
('What is the capital of Finland? a) Helsinki  b) Tallinn c) Stockholm', 'a'),
('What is the capital of Ukraine? a) Pristina b) Kiev c) Chisinau', 'b'),
('What is the capital of Hungary? a) Budapest b) Reykjavik  c) Rome', 'a'),
('What is the capital of Norway? a) Moscow  b) Stockholm c) Oslo', 'c'),
('What is the capital of Switzerland? a) Bern b) Sofia c) Brussels', 'a'),
('What is the capital of Austria? a) Madrid b) Tirana c) Vienna', 'c'),
('What is the capital of Albania? a) Sarajevo b) Tirana c) Prague', 'b'),
('How many letters are in the word ‘MEOW’? a) 2 b) 4 c) 6', 'b'),
('How many letters are in the word ‘WIZARD’? a) 6 b) 7 c) 8', 'a'),
('What item do you need to open the treasure chest? a) Lock b) Key c) Finger', 'b'),
('What item do you need to find to win this game? a) Key b) Wise man c) Treasure chest', 'c'),
('What do you need to buy a plane ticket? a) Key b) Money c) Rocks', 'b'),
('How many years does it take to graduate with an engineering degree from Metropolia? a) 5 b) 7 c) 4', 'c'),
('What is the opposite word for ‘CAT’? a) Tac b) Dog c) Human', 'b'),
('What is the opposite word for ‘WHITE’? a) Black b) Brown c) Grey', 'a'),
('What is the opposite word for ‘WATER’? a) Grass b) Air c) Fire', 'c'),
('What is the opposite word for ‘HAPPY’? a) Angry b) Sad c) Excited', 'b'),
('What is the opposite word for ‘EASY’? a) Normal b) Big c) Hard', 'c'),
('What is the correct answer to [5 + 2 * 4]? a) 28 b) 13 c) 16', 'b'),
('What is the correct answer to [2 * 3 * 0 * 1 + 4]? a) 4 b) 10 c) 30', 'b'),
('What is the correct answer to [1 + 2 * 3 - 6]? a) 3 b) -5 c) 1', 'c'),
('What is the correct answer to [1 + 2 + 3]? a) 6 b) 5 c) 7', 'a'),
('What is the correct answer to [2 * 2 * 2 * 2]? a) 8 b) 16 c) 32', 'b'),
('Why is recycling important? a) It increases pollution b) It has no impact c) It helps reduce waste', 'c'),
('What is a renewable energy source? a) Coal b) Wind power c) Oil', 'b'),
('How can you save energy at home? a) Use more water b) Turn off lights when not in use c) Leave television on all day', 'b'),
('What is a benefit of planting trees? a) They clean the air b) They waste space c) You get firewood', 'a'),
('How can you save water? a) Take three showers a day b) Let water run while brushing teeth c) Take shorter showers', 'c'),
('How can you help reduce air pollution? a) Use public transportation b) Burn more coal c) Drive everywhere', 'a');

-- lisää pääkaupungit country-tauluun
update country
set capital = case
	when name='Andorra' then 'Andorra la Vella'
	when name='Albania' then 'Tirana'
	when name='Austria' then 'Vienna'
	when name='Bosnia and Herzegovina' then 'Sarajevo'
	when name='Belgium' then 'Brussels'
	when name='Bulgaria' then 'Sofia'
	when name='Belarus' then 'Minsk'
	when name='Switzerland' then 'Bern'
	when name='Czech Republic' then 'Prague'
	when name='Germany' then 'Berlin'
	when name='Denmark' then 'Copenhagen'
	when name='Estonia' then 'Tallinn'
	when name='Spain' then 'Madrid'
	when name='Finland' then 'Helsinki'
	when name='Faroe Islands' then 'NULL'
	when name='France' then 'Paris'
	when name='United Kingdom' then 'London'
	when name='Guernsey' then 'NULL'
	when name='Gibraltar' then 'NULL'
	when name='Greece' then 'Athens'
	when name='Croatia' then 'Zagreb'
	when name='Hungary' then 'Budapest'
	when name='Ireland' then 'Dublin'
	when name='Isle of Man' then 'NULL'
	when name='Iceland' then 'Reykjavik'
	when name='Italy' then 'Rome'
	when name='Jersey' then 'NULL'
	when name='Liechtenstein' then 'Vaduz'
	when name='Lithuania' then 'Vilnius'
	when name='Luxembourg' then 'Luxembourg'
	when name='Latvia' then 'Riga'
	when name='Monaco' then 'Monaco'
	when name='Moldova' then 'Chisinau'
	when name='Montenegro' then 'Podgorica'
	when name='North Macedonia' then 'Skopje'
	when name='Malta' then 'Valletta'
	when name='Netherlands' then 'Amsterdam'
	when name='Norway' then 'Oslo'
	when name='Poland' then 'Warsaw'
	when name='Portugal' then 'Lisbon'
	when name='Romania' then 'Bucharest'
	when name='Serbia' then 'Belgrade'
	when name='Russia' then 'Moscow'
	when name='Sweden' then 'Stockholm'
	when name='Slovenia' then 'Ljubljana'
	when name='Slovakia' then 'Bratislava'
	when name='San Marino' then 'San Marino'
	when name='Ukraine' then 'Kiev'
	when name='Vatican City' then 'Vatican City'
	when name='Kosovo' then 'Pristina'
	end
where continent='EU';
