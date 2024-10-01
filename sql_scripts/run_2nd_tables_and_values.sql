--PROJEKTI - aarrearkku-tietokannan luominen (treasure_chest)

--poista taulut jos olemassa (tässä järjestyksessä)
DROP TABLE IF EXISTS rewards;
DROP TABLE IF EXISTS game_airports;
DROP TABLE IF EXISTS wise_man_questions;
DROP TABLE IF EXISTS game;
DROP TABLE IF EXISTS difficulty;

--poista country taulusta sarake capital
ALTER TABLE IF EXISTS country DROP COLUMN capital;

---------------------------------------------------------------------------------------------------------
--viiteavain airportista countryyn:
alter table airport add foreign key(iso_country) references country(iso_country);

---------------------------------------------------------------------------------------------------------

CREATE table wise_man_questions(
ID int not null auto_increment,
question varchar(100),
answer varchar(40),
primary key (ID)
);


CREATE table difficulty(
level varchar(40) not null,
country_count int,
airports_in_treasure_land varchar(40),
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
answered varchar(10),
has_treasure varchar(10),
is_default_airport varchar(10),
primary key (id),
foreign key (game_id) REFERENCES game(id),
foreign key (airport_ident) REFERENCES airport(ident),
foreign key (wise_man_question_id) REFERENCES wise_man_questions(id)
);

--lisää country-tauluun capital-sarake:
alter table country add capital varchar(40);

----------------------------------------------------------------------------------------------------------------

--lisätään dataa difficulty-tauluun:
insert into difficulty(level, country_count, airports_in_treasure_land, wise_man_count, starting_money, wise_man_cost, wise_man_reward)
values ("easy", 10, 10, 4, 1500, 100, 200),
("normal", 20, 20, 8, 3000, 200, 500),
("hard", 30, 40, 16, 5000, 400, 1000);

--lisätään dataa rewards-tauluun:
insert into rewards(name, difficulty_level)
values ("gold ring", "easy"), ("magic carpet", "easy"),
("gold bar", "normal"), ("magic wand", "normal"),
("world peace", "hard"), ("time machine", "hard"), ("diamond collection", "hard");

--lisää pääkaupungit country-tauluun:
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


insert into wise_man_questions(question, answer)
values
    ('What is the capital of France? A) London B) Paris C) San Marino', 'Paris'),
    ('What is the capital of Portugal? A) Skopje B) Valletta C) Lisbon', 'Lisbon'),
    ('What is the capital of Serbia? A) Helsinki B) Belgrade C) Ljubljana', 'Belgrade')
;
