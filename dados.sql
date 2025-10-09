DROP DATABASE IF EXISTS mqtt_estufa;
CREATE DATABASE IF NOT EXISTS mqtt_estufa;
use mqtt_estufa;

DROP TABLE IF EXISTS dados_estufa;
create table dados_estufa(
	dado_id integer primary key auto_increment,
    dado_data datetime not null,
    dado_temp float not null,
    dado_umid float not null 
);
