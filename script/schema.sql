CREATE TABLE db_covid.covid_values(
    id int primary key auto_increment,
    province_state varchar(50),
    country_region varchar(50),
    lat decimal(9,6),
    long decimal(9,6),
    date date,
    value int,
    status varchar(15),
    created_at datetime
);