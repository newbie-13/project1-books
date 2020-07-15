create table books(
  isbn varchar not null,
  title varchar not null,
  author varchar not null,
  year integer not null
);

create table account(
  username varchar not null,
  password varchar not null
);

create table comment(
  isbn varchar not null,
  comment varchar not null,
  rating integer not null
);

psql postgres://mapmzheenltumc:f0c0f4cb7b60e169442a47cbd25092515dcae6544e3c1f9bbd2f4920711045fc@ec2-3-216-129-140.compute-1.amazonaws.com:5432/d71ivvnukvuj5p
